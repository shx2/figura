"""
Unit-tests for testing the auto-overlay and opaqueness functionality.
"""

################################################################
# Unittest definition

class test_auto_overlay:
    is_unittest = True
    class construct:
        entry_point = 'A2'
    class verify:
        entry_point = 'A2_result'

class test_opaque:
    is_unittest = True
    class construct:
        entry_point = 'A3'
    class verify:
        entry_point = 'A3_result'

class test_opaque_nested:
    is_unittest = True
    class construct:
        entry_point = 'A4'
    class verify:
        entry_point = 'A4_result'

class test_auto_overlay_levels:
    is_unittest = True
    class construct:
        entry_point = 'A5'
    class verify:
        entry_point = 'A5_result'

class test_opaque_levels1:
    is_unittest = True
    class construct:
        entry_point = 'A6'
    class verify:
        entry_point = 'A6_result'

class test_opaque_levels2:
    is_unittest = True
    class construct:
        entry_point = 'A7'
    class verify:
        entry_point = 'A7_result'

class test_derived_overlyee:
    is_unittest = True
    class construct:
        entry_point = 'A8'
    class verify:
        entry_point = 'A8_result'

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
# auto overlays

class A2(A):
    class B:  # overlay: gets b from A.B
        class C: # overlay: gets c1 from A.B.C, overrides c2 from A.B.C, adds new c3
            c2 = 66
            c3 = 77
        class D:
            d = 'dd'

class A2_result:
    a = 1
    class B:
        b = 2
        class C:
            c1 = 5
            c2 = 66
            c3 = 77
        class D:
            d = 'dd'

###############
# auto overlays, except for C, which is opaque:

class A3(A):
    class B:  # overlay: gets b from A.B
        class C:  # opaque, meaning no overlay. causes c1 to be excluded
            __opaque__ = True
            c2 = 66
            c3 = 77

class A3_result:
    a = 1
    class B:
        b = 2
        class C:
            c2 = 66
            c3 = 77

###############
# B is opaque, thus C has nothing to overlay

class A4(A):
    class B:  # not overlaying, will not contain b
        __opaque__ = True
        class C:  # not overlaying anything, will only contain z
            z = 9999

class A4_result:
    a = 1
    class B:
        class C:
            z = 9999

###############
# 2-level overlays: A->A2->A5

class A5(A2):
    class B:
        class C:
            c3 = 777
            c4 = 888

class A5_result:
    a = 1
    class B:
        b = 2
        class C:
            c1 = 5
            c2 = 66
            c3 = 777
            c4 = 888
        class D:
            d = 'dd'

###############
# 2-level overlays, but only one level is seen due to the __opaque__ in A3.C

class A6(A3):
    class B:
        class C:
            c3 = 777
            c4 = 888

class A6_result:
    a = 1
    class B:
        b = 2
        class C:
            c2 = 66
            c3 = 777
            c4 = 888
    
###############
# 2-level overlays, but only one level is seen due to the __opaque__ in A4.B

class A7(A4):
    class B:
        class C:
            c3 = 777
            c4 = 888
    
class A7_result:
    a = 1
    class B:
        class C:
            z = 9999
            c3 = 777
            c4 = 888

###############
# test when the overlayee (A8_base.C) is derived from another config (C2)

class C2:
    c1 = 5
    c2 = 6

class A8_base:
    class C(C2):
        c3 = 777

class A8(A8_base):
    class C:
        c4 = 888
    
class A8_result:
    class C:
        c1 = 5
        c2 = 6
        c3 = 777
        c4 = 888

###############
