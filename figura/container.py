"""
Definition of the config-container type.
"""

import json

from .misc import Struct, merge_dicts, deep_getattr, deep_setattr


################################################################################

class ConfigContainerMixin():
    """
    A mixin-baseclass of the `ConfigContainer <#figura.container.ConfigContainer>`_ class.
    """
    
    INDENT_LEN = 2
    
    DEFAULT_JSON_DUMP_KWARGS = {
        'indent': INDENT_LEN,
        'ensure_ascii': False,
    }

    #===================================================================================================================
    # attribute access
    #===================================================================================================================
    
    def deep_getattr(self, attr_path, *args):
        """
        See deep_getattr_.
        
        .. _deep_getattr:
        """
        return deep_getattr(self, attr_path, *args)

    def deep_setattr(self, attr_path, value):
        """
        See deep_setattr_.

        .. _deep_setattr:
        """
        return deep_setattr(self, attr_path, value)

    def apply_overrides(self, overrides, **kwargs):
        """
        A convenience method, simply calling apply_overrides_to_config_.
            
        :note: this method modifies the config container in-place.
        
        .. _apply_overrides_to_config: #figura.override.apply_overrides_to_config
        """
        from figura.override import apply_overrides_to_config  # avoid circular import
        apply_overrides_to_config(self, overrides, **kwargs)

    #===================================================================================================================
    # serialization
    #===================================================================================================================

    def to_string(self, **kwargs):
        """
        A JSON-string representation of the config container.
        """
        return self.to_json(**kwargs)
    
    def __str__(self):
        return self.to_string()
    
    def __repr__(self):
        return '%s(%s)' % (
            self.__class__.__name__,
            super(ConfigContainer, self).__repr__())
    
    def to_json(self, **kwargs):
        """
        :param args+kwargs: extra args to pass to ``json.dumps``.
        :return: the json string representation of self.
        """
        kw = dict(self.DEFAULT_JSON_DUMP_KWARGS)
        kw.update(kwargs)
        return json.dumps(self, **kw)
        
    @classmethod
    def from_json(cls, json_str):
        """
        Create a ConfigContainer from a json string.
        """
        return cls.from_dict(json.loads(json_str))
    
    def to_dict(self):
        """
        deep-conversion of self to a dict.
        """
        return json.loads(self.to_json())
    
    @classmethod
    def from_dict(cls, x):
        """
        deep-conversion of a dict to a ConfigContainer
        """
        return get_config_container_from_dict(x, cls = cls)

    def to_python_string(self):
        """
        A python-string representation of the config container.
        """
        lines = self._to_python_lines(self, 0)
        return '\n'.join(lines)
    
    def _to_python_lines(self, x, indent_level = 0):
        indent = ' ' * (self.INDENT_LEN * indent_level)
        lines = []
        for k, v in x.items():
            if isinstance(v, ConfigContainer):
                lines.append('%sclass %s:' % (indent, k))
                if len(v) > 0:
                    lines.extend(self._to_python_lines(v, indent_level + 1))
                else:
                    lines.append('%s%spass' % (indent, ' ' * self.INDENT_LEN))
            else:
                lines.append('%s%s = %r' % (indent, k, v))
        return lines

class ConfigContainer(Struct, ConfigContainerMixin):
    """
    A `Struct <#figura.misc.Struct>`_-like (recursive) container holding the configuration data.
    """
    
    DEFAULT_METADATA = Struct(
        is_override_set = False,
        is_opaque = False,
        is_opaque_override = False,
        doc = None,
    )
    
    def __init__(self, *args, **kwargs):
        metadata = kwargs.pop('metadata', self.DEFAULT_METADATA)
        super(ConfigContainer, self).__init__(*args, **kwargs)
        # not doing self._metadata=x because that results with self['_metadata']=x,
        # i.e. adding a new key to the container
        self.__dict__['_metadata'] = Struct(merge_dicts(self.DEFAULT_METADATA, metadata))
        
    def get_metadata(self):
        return self._metadata


################################################################################

def get_config_container_from_dict(x, cls = ConfigContainer):
    """
    Deep-conversion of a dict to a ConfigContainer.
    """
    if isinstance(x, dict):
        # convert recursively, and preserve dict type
        y = type(x)(
            ( k, get_config_container_from_dict(v, cls = cls) )
            for k, v in x.items()
        )
        return cls(y)
    else:
        # assume an atomic value
        return x

################################################################################
