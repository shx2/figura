"""
Unit-tests testing the most basic features.
"""

################################################################
# Unittest definition

class test1:
    is_unittest = True
    class construct:
        entry_point = 'some_params'
        #apply_overrides = [ (overridden, overriding), ...]
    class verify:
        entry_point = 'RESULT'
        #operator = 'equals' ?

class test_identity:
    is_unittest = True
    class construct:
        entry_point = 'some_params'
    class verify:
        entry_point = 'some_params'

################################################################
# Unittest data

class some_params:
    a = 1
    b = 2
    
    # starting with underscore meaning private, i.e. not included in the ConfigContainer.
    _c_hidden = [3,4]
    c = _c_hidden
    
    class nested:
        d = 'five'

# no special constructs, the results is the same as what we defined
class RESULT:
    a = 1
    b = 2
    c = [3,4]
    class nested:
        d = 'five'

################################################################
