Reusing Containers
============================================

:In this section: We learn that *we can also reuse config containers*.

Suppose our system is now running in production, but every once in a while it
encouters problems and errors.  We decided to add an alerting capability to all
modules in our system, to send the administrator an email in realtime, every time
a problem occurs.  Naturally, this feature should be configurable, and, since the
system is pretty simple at this stage, the same person maintains all the modules,
and therefor the config is the same for all modules.

The example below demonstrates how this can be done by reusing the config container which
defines the behavior of the "alerter" object.

(For readability, we omit the parts which are unchanged.)
