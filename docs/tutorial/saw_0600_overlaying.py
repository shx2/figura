class _saw_module:
    class alert:
        enabled = True
        channel = 'email'
        receipient = 'admin@saw.zzz'

class saw:
    class searcher(_saw_module):
        # ...
        pass
        
    class analyzer(_saw_module):
        # ...
        class alert:  # Definitions inside this container *overlay* _saw_module.alert
            # Only need to define receipient. The rest is taken from _saw_module.alert
            receipient = 'analyzers@saw.zzz'
        
    class writer(_saw_module):
        # ...
        pass
