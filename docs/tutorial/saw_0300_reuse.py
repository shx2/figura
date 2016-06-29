# The following parameters are prefixed with underscores, to make them "hidden"
# -- they will not be included in the final config container.
# This is useful in cases where they only serve as temporary definitions to be reused.
_root_dir = '/saw/data/'
_raw_content_dir = _root_dir + 'raw'
_analyzed_content_dir = _root_dir + 'analyzed'

class saw:
    class searcher:
        # ...
        output_raw_content_dir = _raw_content_dir
        # ...
        
    class analyzer:
        # ...
        input_raw_content_dir = _raw_content_dir
        output_analyzed_content_dir = _analyzed_content_dir
        # ...
        
    class writer:
        # ...
        input_analyzed_content_dir = _analyzed_content_dir
        # ...
