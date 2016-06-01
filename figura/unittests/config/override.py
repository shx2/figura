"""
Unit-tests for testing the overriding functionality, including opaque overrides.
"""

################################################################
# Unittest definition

class test_overrides_basic1:
    is_unittest = True
    class construct:
        entry_point = 'A'
        apply_overrides = [ ('A', 'A1_overrides') ]
    class verify:
        entry_point = 'A1_result'

class test_overrides_nested1:
    is_unittest = True
    class construct:
        entry_point = 'A'
        apply_overrides = [ ('A', 'A2_overrides') ]
    class verify:
        entry_point = 'A2_result'

class test_overrides_opaque1:
    is_unittest = True
    class construct:
        entry_point = 'A'
        apply_overrides = [ ('A', 'A3_overrides') ]
    class verify:
        entry_point = 'A3_result'

class test_overrides_flat1:
    is_unittest = True
    class construct:
        entry_point = 'A'
        apply_overrides = [ ('A', 'A4_overrides') ]
    class verify:
        entry_point = 'A4_result'

################################################################
# Unittest data

class A:
    a = 1
    class B:
        b = 2
        class C:
            c1 = 5
            c2 = 6

###############
# This override set, when applied to A, only overrides A.a

class A1_overrides:
    __override__ = True
    a = 111
        
class A1_result:
    a = 111
    class B:
        b = 2
        class C:
            c1 = 5
            c2 = 6

###############
# This override set, when applied to A, only overrides A.B.C.c1

class A2_overrides:
    __override__ = True
    class B:
        class C:
            c1 = 555

class A2_result:
    a = 1
    class B:
        b = 2
        class C:
            c1 = 555
            c2 = 6

###############
# This override set, when applied to A:
# - overrides A.a=111
# - overwrites B (will not contain b and C) with a container containing only b2
# - adds a A.B.D container (D is not originally in A.B)

class A3_overrides:
    __override__ = True
    a = 111
    class B:
        __opaque_override__ = True
        b2 = 8
    class D:
        __opaque_override__ = True
        d = 'dd'

class A3_result:
    a = 111
    class B:
        b2 = 8
    class D:
        d = 'dd'

###############
# This override set, in a flat ("cli") form, when applied to A:
# - overrides A.B.b
# - overrides A.B.C.c2
# - sets a new param A.B.C.c3

class A4_overrides:
    __override__ = True
    B__b = 22
    B__C__c2 = 66
    B__C__c3 = 77

class A4_result:
    a = 1
    class B:
        b = 22
        class C:
            c1 = 5
            c2 = 66
            c3 = 77

###############
