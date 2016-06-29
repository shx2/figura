Override Sets
====================

:In this section: We learn about *config override sets*, including *opaque* ones.

So we have our SAW system running in production, interacting with all
sorts of external entities and resources (reading from WWW, writing to a remote DB, sending
alerts by mail).  Naturally, our developers need to be able to run the system in offline mode
(for developing new features, testing, debugging, etc.).

In our system, "offline" means:

- Searcher reads from our archive, not from WWW.
- "Raw" and "analyzed" files are written to a different directory than the one used in production.
- Writer writes to stdout, not to DB and possibly other locations.
- None of the modules send alerts by mail.

In Figura, this can be done by defining an *override set* ("patch") per module, which
defines the changes to apply to its config in order to make it "offline".

Since there are overrides which are common to all modules (namely, disabling the alerter), it
makes sense to define a common override set, which is then used as the base of the per-module
override sets.
