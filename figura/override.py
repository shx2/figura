"""
Definitions and tools of override-set-related and config-overriding-related operations.
"""

from .container import ConfigContainer
from .errors import ConfigError
from .misc import deep_getattr, deep_setattr
   
    
################################################################################

class ConfigOverrideSet(ConfigContainer):
    """
    A ConfigContainer representing an override-set, which can be applied to
    other config containers.
    """
    
    def __init__(self, *args, **kwargs):
        super(ConfigOverrideSet, self).__init__(*args, **kwargs)
        self.get_metadata().is_override_set = True

################################################################################

def apply_overrides_to_config(container, overrides, callback_key_prefix = '', enforce_override_set = True, **kwargs):
    """
    Apply overrides from an override-set to a container (in-place).
    
    :param container: a ``ConfigContainer`` to modify in-place
    :param overrides: a ``ConfigContainer`` containing the overrides to apply
    :param enforce_override_set: if ``enforce_override_set`` is set, raises an
        exception if ``overrides`` is not an override set (according to its
        ``is_override_set`` metadata attribute)
    :param kwargs: extra kwargs to pass on to `apply_override
        <#figura.override.apply_override>`_.
    :raise ConfigError: if ``enforce_override_set`` and ``overrides`` isn't an
        override set.
    """
    
    if enforce_override_set and not overrides.get_metadata().is_override_set:
        raise ConfigError('Attempting to apply overrides while is_override_set=False')
    
    for key, value in overrides.items():
        applied = False

        # check if overlaying -- i.e. if value is a nested container, which isn't
        # marked as opaque.
        old_value = container.get(key)
        if (isinstance(old_value, ConfigContainer) and
            isinstance(value, ConfigContainer) and
            not value.get_metadata().is_opaque_override):
            
            # old_value and value are both containers -- a nested override, apply recursively
            nested_container = container[key]
            cur_key_prefix = '%s.' % ( key, )
            if callback_key_prefix:
                cur_key_prefix = '%s.%s' % ( callback_key_prefix, cur_key_prefix )
            apply_overrides_to_config(
                nested_container, value,
                callback_key_prefix = cur_key_prefix,
                enforce_override_set = enforce_override_set,
                **kwargs
            )
            applied = True

        if not applied:
            # flat or plain override
            apply_override(
                container, key, value,
                callback_key_prefix = callback_key_prefix,
                **kwargs
            )
            applied = True

def apply_override(
        container, key, value,
        callback = None,
        callback_missing_value = '<<undef>>',
        callback_key_prefix = '',
        ):
    """
    Apply an override (key=value pair) to the given container in-place.
    The key can indicate override of a nested param, by including dots
    (or the alternative double-underscore form). E.g.: ``A.B.x``, or ``A__B__x``.
    
    :param container: a ConfigContainer to modify in place
    :param key: the attribute (or attr-path) to set
    :param value: the new attribute value
    :param callback: An optional callable to be called for "reporting" the
        override operation. The callable should take as args: key, value,
        old_value.
    :param callback_missing_value: the value to pass as old_value, in case the param
        was not previously set.
        
    """
    if callback is not None:
        old_value = deep_getattr(
            container, key, callback_missing_value,
            key_normalizer = normalize_override_key,
        )
        callback_key = callback_key_prefix + key
        callback(callback_key, value, old_value)
    deep_setattr(
        container, key, value,
        auto_constructor = type(container),
        key_normalizer = normalize_override_key,
    )

def normalize_override_key(key):
    """
    .. testsetup:: 

        from figura.override import normalize_override_key

    >>> normalize_override_key('a__b__c')
    'a.b.c'
    """
    if key.startswith('__'):
        return key
    return key.replace('__', '.')

################################################################################
