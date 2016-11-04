"""
Configuration of the SAW system. (<-- This is a docstring)
"""

# The "class" Python-keyword defines a config container (<-- This is a comment)
class saw:
    """ The top-level config container of the SAW system. """
    
    class searcher:
        """ Configuration of the Searcher module. """
        
        keywords = [ 'figura', 'configuration', 'language' ]
        """ Search content containing these keywords. """
        
        class data_source:
            type = 'WWW'
            """ Looking for content in the World Wide Web. """
            
        output_raw_content_dir = '/saw/data/raw'
        """ Directory to store raw content in. """
        
    class analyzer:
        """ Configuration of the Analyzer module. """
        
        input_raw_content_dir = '/saw/data/raw'
        """ Directory to read content to analyze from. """

        output_analyzed_content_dir = '/saw/data/analyzed'
        """ Directory to write analyzed data to. """
        
        extract_features = [ 'sentiment' ]
        """ A list of features to extract from content. """
        
    class writer:
        """ Configuration of the Analyzer module. """

        input_analyzed_content_dir = '/saw/data/analyzed'
        """ Directory to read analyzed data from. """
        
        class outputs:
            
            class db:
                enabled = True  # enabled -- writing to a mysql DB
                type = 'mysql'
                connection_string = 'Server=localhost;Database=saw;Uid=saw_analyzer;Pwd=xxx;'
                table = 'features'
                
            class file:
                enabled = False  # disabled -- don't write to a file
                type = 'file'
                path = '/saw/output/dump.txt'
        
        