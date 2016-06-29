class _alert:
    enabled = True
    channel = 'email'
    receipient = 'admin@saw.zzz'

class saw:
    class searcher:
        # ...
        alert = _alert
        
    class analyzer:
        # ...
        alert = _alert
        
    class writer:
        # ...
        alert = _alert
