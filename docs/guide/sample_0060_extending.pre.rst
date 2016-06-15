Extending a Base Container
================================

A config container can be used as the base of a new container, extending it with new definitions and overriding base definitions.
This is done using Python's inheritance syntax.

:note: For understanding how this works, it is useful to keep in mind the analogy between defining config containers and defining
    classes in OOP.

:note: The use of the term "override" above is inspired by the analogy to the OOP world. Not to be confused with *override sets*
    (described later). For clarity, the term "overshadow" could also be used here instead.

