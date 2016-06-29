
_offline_root_dir = '/saw/offline/'
_raw_content_dir = _offline_root_dir + 'raw'
_analyzed_content_dir = _offline_root_dir + 'analyzed'

class _offline_module_overrides:
    """  A base override set of the per-module offline override sets. """
    # Don't send alerts
    class alert:
        enabled = False

class saw_offline_overrides:
    """ An override set for running SAW in offline mode. """

    # This config container represents overrides to be applied to other containers:
    __override__ = True
    
    class searcher(_offline_module_overrides):
        # Reading from archive, not WWW
        class data_source:
            type = 'archive'
            path = '/saw/archive/raw/'
        output_raw_content_dir = _raw_content_dir
        
    class analyzer(_offline_module_overrides):
        input_raw_content_dir = _raw_content_dir
        output_analyzed_content_dir = _analyzed_content_dir
        
    class writer(_offline_module_overrides):
        input_analyzed_content_dir = _analyzed_content_dir
        # Writing to a local directory
        class outputs:
            # Overshadow, don't overlay (See explanation below)
            __opaque_override__ = True
            # Write output to stdout
            class file:
                enabled = True
                type = 'file'
                path = '/dev/stdout'

__entry_point__ = saw_offline_overrides
