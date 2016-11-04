
_root_dir = '/saw/data/'
_raw_content_dir = _root_dir + 'raw'
_analyzed_content_dir = _root_dir + 'analyzed'

class _saw_module:
    class alert:
        enabled = True
        channel = 'email'
        receipient = 'admin@saw.zzz'

class saw:
    
    class searcher(_saw_module):
        keywords = [ 'figura', 'configuration', 'language' ]
        class data_source:
            type = 'WWW'
        output_raw_content_dir = _raw_content_dir
        
    class analyzer(_saw_module):
        input_raw_content_dir = _raw_content_dir
        output_analyzed_content_dir = _analyzed_content_dir
        extract_features = [ 'sentiment' ]
        class alert:
            receipient = 'analyzers@saw.zzz'
        
    class writer(_saw_module):
        input_analyzed_content_dir = _analyzed_content_dir
        class outputs:
            class db:
                enabled = True
                type = 'mysql'
                connection_string = 'Server=localhost;Database=saw;Uid=saw_analyzer;Pwd=xxx;'
                table = 'features'
            class file:
                enabled = False
                type = 'file'
                path = '/saw/output/dump.txt'

# This part is explained in the next section
__entry_point__ = saw
