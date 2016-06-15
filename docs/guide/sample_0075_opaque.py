class a:
    class b:
        x = 1
        y = 2

class a2(a):
    class b:  # overshadowing, will not include any params from a.b
        __opaque__ = True
        y = 3
