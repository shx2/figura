class _saw_module:
    class alert:
        enabled = True
        channel = 'email'
        receipient = 'admin@saw.zzz'

class saw:
    class searcher(_saw_module):  # searcher extends _saw_module
        # ...
        # The "pass" statement is required in this example only because we define
        # an empty container, for brevity. Without it, we get a Python syntax error.
        pass
        
    class analyzer(_saw_module):
        # ...
        pass
        
    class writer(_saw_module):
        # ...
        pass
