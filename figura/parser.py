"""
Parsing Figura config files.
"""

import inspect

from .misc import merge_dicts
from .errors import ConfigParsingError
from .container import ConfigContainer
from .override import ConfigOverrideSet, normalize_override_key
from .importutils import import_figura_file


################################################################################
# Constants and definitions

VALID_ATOMIC_VALUE_TYPES = set([type(None), type(''), type(u''), type(True), type(0), type(0.0)])
VALID_SEQUENCE_VALUE_TYPES = set([type(()), type([]), type({})])

META_MAP = {
    '__override__': 'is_override_set',
    '__opaque__': 'is_opaque',
    '__opaque_override__': 'is_opaque_override',
    '__doc__': 'doc',
}


################################################################################
# The parser

class ConfigParser:
    """
    A python-config parser.

    Should not be used directly, use ``read_config`` instead.  If used directly,
    the ``parse`` method should be called from within a ``FiguraImportContext`` context.

    Use like::

        parser = ConfigParser()
        with FiguraImportContext():
            config = parser.parse('figura.tests.config.basic1')

    """

    VALID_ATOMIC_VALUE_TYPES = VALID_ATOMIC_VALUE_TYPES
    """ A list of atomic types allowed as config values """

    VALID_SEQUENCE_VALUE_TYPES = VALID_SEQUENCE_VALUE_TYPES
    """ A list of sequence types allowed as config values """

    META_MAP = META_MAP
    """
    A conversion map from config-metadata-directives (e.g. __opaque__),
    to their metadata attribute (e.g., is_opaque)
    """

    # ============================================================================================
    # main parsing methods
    # ============================================================================================

    def parse(self, path):
        """
        Parse a figura config file, identified by its import path, E.g.
        ``figura.tests.config.basic1``.

        :return: a `ConfigContainer <#figura.container.ConfigContainer>`_ object.
        :raise ConfigParsingError: if parsing fails.
        """

        # load it using python's import mechanism:
        module = self.get_module(path)
        # post-import processing:
        conf = self._python_to_conf(module)
        # post-parsing:
        self._finalize_config_container(conf, module)
        return conf

    def get_module(self, path):
        return self._import_python_module(path)

    # ============================================================================================
    # python-import harnessing
    # ============================================================================================

    def _import_python_module(self, path):
        """
        parse the python-config files into an intermediate representation.
        """
        return import_figura_file(path)

    # ============================================================================================
    # post-import processing of python constructs
    # ============================================================================================

    def _python_to_conf(self, x, name='', nesting_context=None, **metadata):
        """
        convert the intermediate config representation into a ConfigContainer.
        """

        # If this is an atomic type, no parsing is required
        if type(x) in self.VALID_ATOMIC_VALUE_TYPES:
            return x
        elif type(x) in self.VALID_SEQUENCE_VALUE_TYPES:
            # a sequence. apply to elements recursively
            if hasattr(x, 'items'):
                return type(x)((k, self._python_to_conf(v)) for k, v in x.items())
            else:
                return type(x)(self._python_to_conf(elem) for elem in x)

        if type(x) == type(inspect):

            # the top-level module object --> a ConfigContainer
            raw_attrs = self._get_dunder_dict(x)

            # handle the __entry_point___ directive:
            new_x = self._find_entry_point(raw_attrs)
            if new_x is not None:
                # return the result of the recursive call on the new entry point
                return self._python_to_conf(new_x)

        elif _is_raw_container(x):
            # a class --> a ConfigContainer
            raw_attrs = self._get_dunder_dict(x)

            # handle auto-overlay magic
            if nesting_context is None:
                nesting_context = []
            nesting_context = nesting_context + [(name, x)]  # don't use append
            for overlayee in self._gen_overlayees(nesting_context):
                for k, v in self._get_dunder_dict(overlayee).items():
                    if k not in raw_attrs:
                        raw_attrs[k] = v
        else:
            # type misunderstood
            raise ConfigParsingError('Config construct of unsupported type %r: %s' % (type(x), x))

        # Separate raw_attrs to their types. See _prepare_attrs for more details.
        real_attrs, meta_attrs = self._prepare_attrs(raw_attrs)

        # if this is an overridet-set, all nested containers are also override sets automatically.
        # we propagate this metadata attribute using the metadata dict:
        if meta_attrs.get('is_override_set', False):
            metadata['is_override_set'] = meta_attrs['is_override_set']

        # convert real attr recursively
        attrs = {
            k: self._python_to_conf(v, name=k, nesting_context=nesting_context, **metadata)
            for k, v in real_attrs.items()
        }

        # create the container
        metadata_to_apply = merge_dicts(metadata, meta_attrs)
        if metadata_to_apply.get('is_override_set', False):
            container_cls = ConfigOverrideSet
        else:
            container_cls = ConfigContainer
        container = container_cls(attrs)

        # set metadata attributes on the container
        container.get_metadata().update(metadata_to_apply)

        return container

    def _get_dunder_dict(self, x, deep=True):
        if x == object:
            # result of the mro call:
            return {}
        if not deep:
            return dict(x.__dict__)
        objs = [x]
        try:
            objs.extend(inspect.getmro(x)[1:])
        except AttributeError:
            pass
        dicts = [self._get_dunder_dict(obj, deep=False) for obj in objs]
        d = merge_dicts(*reversed(dicts))
        return d

    def _prepare_attrs(self, raw_attrs):
        """
        There are four types of attributes:

        1. real config attrs, e.g., a=1
        #. private config attrs, e.g., _a=1 -- we drop them
        #. metadata attrs, e.g., __opaque__=True
        #. python internal attrs, e.g., __module__=xxx -- we drop them

        :return: a 2-tuple: (real_attrs, meta_attrs)
        """
        real_attrs = {}
        meta_attrs = {}
        for k, v in raw_attrs.items():
            # try meta:
            try:
                meta_attrs[self.META_MAP[k]] = v
                continue
            except KeyError:
                pass  # not meta
            # filter out private attrs and python internals
            if k.startswith('_'):
                continue
            # the rest are real
            k = normalize_override_key(k)
            real_attrs[k] = v
        return real_attrs, meta_attrs

    def _finalize_config_container(self, conf, module):
        conf._add_module_metadata(module)

    # ============================================================================================
    # overlay support
    # ============================================================================================

    def _gen_overlayees(self, nesting_context):
        nesting_path = [x[0] for x in nesting_context]
        nesting_containers = [x[1] for x in nesting_context]
        rel_path = []
        while nesting_containers:
            nester = nesting_containers[-1]
            # discontinue overlay chain if __opaque__ is set in nester
            if _is_marked_opaque(nester):
                break
            if rel_path:
                for nester_base in inspect.getmro(nester)[1:]:
                    try:
                        attr_path = '.'.join(rel_path)
                        overlayee, opaque = \
                            self._deep_getattr_with_opaqueness_check(nester_base, attr_path)
                        # make sure the overlayee is a raw container, because it should
                        # be possible to override any (primitive) value with a container,
                        # in which case, no overlaying takes place.
                        if _is_raw_container(overlayee):
                            yield overlayee
                        # discontinue overlay chain if __opaque__ is set somehere
                        # in nester_base's path
                        if opaque:
                            break
                    except AttributeError:
                        pass
            rel_path = nesting_path[-1:] + rel_path
            nesting_path = nesting_path[:-1]
            nesting_containers = nesting_containers[:-1]

    def _deep_getattr_with_opaqueness_check(self, x, attr_path, *args):
        opaque = _is_marked_opaque(x)
        while True:
            attr, delim, rest = attr_path.partition('.')
            if delim:
                # go one level deeper:
                x = getattr(x, attr)
                attr_path = rest
                opaque = opaque or _is_marked_opaque(x)
            else:
                # deepest level
                x = getattr(x, attr_path, *args)
                opaque = opaque or _is_marked_opaque(x)
                return x, opaque

    # ============================================================================================
    # __entry_point___ support
    # ============================================================================================

    def _find_entry_point(self, attrs):
        entry_point = attrs.get('__entry_point__')
        if entry_point is not None:
            if isinstance(entry_point, str):
                # entry_point is given by name
                try:
                    entry_point = attrs[entry_point]
                except KeyError:
                    raise ConfigParsingError(
                        'entry-point not found: %s' % (entry_point, )) from None
            else:
                # entry_point is given by pointing to to a container
                pass
        return entry_point


################################################################################

def _is_raw_container(x):
    # a raw container is the 'class x: ...' container as appears in the figura file, before
    # converting it to a ConfigContainer
    return inspect.isclass(x)


def _is_marked_opaque(x):
    return getattr(x, '__opaque__', False)


################################################################################
