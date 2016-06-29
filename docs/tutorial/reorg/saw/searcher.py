from .common import saw_module, raw_content_dir

class searcher(saw_module):
    keywords = [ 'figura', 'configuration', 'language' ]
    class data_source:
        type = 'WWW'
    output_raw_content_dir = raw_content_dir
    # <...all the other stuff addeed over the years...>
    
__entry_point__ = searcher
