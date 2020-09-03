2.0.1
----------------
* removed use of deprecated library imp

2.0.0
----------------
* ".fig" is now the default extension of config files
* Dropped support for python2
* Added support for python versions 3.7 and 3.8 -- versions 3.4 to 3.8 are officially supported
* ConfigContainer now includes module-related metadata: __name__, __file__, __package__
* Significant speed improvements
* Now using a custom importer, dropped dependency on polyloader
* Now PEP8 compliant (thanks to @stevenkaras)
* Now using tox+nosetests for testing


1.2.4
----------------
* Bug fixes


1.2.3
----------------
* Speed improvements


1.2.2
----------------
* Bug fixes


1.2.1
----------------
* Bug fixes


1.2.0
----------------
* ".py" is now the default extension again (but using ".fig" is encouraged)
* Bug fixes


1.1.0
----------------
* (Experimental) Support different file-extension for Figura files instead of ".py" (specifically ".fig")


1.0.0
--------
* Development Status upgraded to Production/Stable -- being used in production for a while now

* Improved double-underscore dot-escaping to actually be useful


0.10.0
--------
* A new directive: __entry_point__

* Various docs improvements. Added a tutorial to docs

* Fixed obscure unittests bugs (test_imports fail to import temp modules)


0.9.3
-----
* Added a reference guide

* Various documnetation improvements

* Minor bug fixes


0.9.2
-----
* Bug fixes


0.9.1
-----
* Bug fixes


0.9.0
-----
* Initial release

Future/Planned
----------------
* Type coercion when applying (cli) overrides

* Support specifying config files by file path (as opposed to import path)

* "Drivers" for reading figura files using a few languages other than python
