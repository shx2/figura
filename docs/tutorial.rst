=================
Figura Tutorial
=================

Overview
=================

In this tutorial, we describe a (made up) system, show how its configuration file/s can
be written using Figura, and demonstrate how to take advantage of some of the key features
of the Figura language.

We start by describing the system we want to write config files for. We then present
a basic config file for it, and gradually improve it by taking advantage of various Figura
features and capabilities.
We also show what changes need to be done to the config files as the system evolves.


The SAW System
-----------------

In this tutorial, we deal with a (made up) system named "SAW".  The system searches the WWW
for content (news articles, blog posts) which contain certain keywords, downloads it, analyzes it
to extract some features from it (e.g. sentiment, provocativeness), and writes the analyzed data
to a DB.

The system consists of three modules:

#. **Searcher**: searches the WWW and fetches relevant content
#. **Analyzer**: analyzes the content and extracts features
#. **Writer**: writes the analyzed data to a DB

Each module runs in its own process.






A Basic Config File
============================================

:In this section: We learn about the *structure and syntax of the config file* and we are introduced to
    *config containers and nesting*.

Following is a basic Figura config file for the SAW system.

To reflect system's modularity, instead of defining a "flat" list of key/value pairs, we define
the config of each module in its own config container.



::

    > cat saw_0200_basic.fig
    """
    Configuration of the SAW system. (<-- This is a docstring)
    """
    
    # The "class" Python-keyword defines a config container (<-- This is a comment)
    class saw:
        """ The top-level config container of the SAW system. """
        
        class searcher:
            """ Configuration of the Searcher module. """
            
            keywords = [ 'figura', 'configuration', 'language' ]
            """ Search content containing these keywords. """
            
            class data_source:
                type = 'WWW'
                """ Looking for content in the World Wide Web. """
                
            output_raw_content_dir = '/saw/data/raw'
            """ Directory to store raw content in. """
            
        class analyzer:
            """ Configuration of the Analyzer module. """
            
            input_raw_content_dir = '/saw/data/raw'
            """ Directory to read content to analyze from. """
    
            output_analyzed_content_dir = '/saw/data/analyzed'
            """ Directory to write analyzed data to. """
            
            extract_features = [ 'sentiment' ]
            """ A list of features to extract from content. """
            
        class writer:
            """ Configuration of the Analyzer module. """
    
            input_analyzed_content_dir = '/saw/data/analyzed'
            """ Directory to read analyzed data from. """
            
            class outputs:
                
                class db:
                    enabled = True  # enabled -- writing to a mysql DB
                    type = 'mysql'
                    connection_string = 'Server=localhost;Database=saw;Uid=saw_analyzer;Pwd=xxx;'
                    table = 'features'
                    
                class file:
                    enabled = False  # disabled -- don't write to a file
                    type = 'file'
                    path = '/saw/output/dump.txt'
            
            

When processed and formatted as JSON::

    > figura_print saw_0200_basic
    {
      "saw": {
        "searcher": {
          "keywords": [
            "figura", 
            "configuration", 
            "language"
          ], 
          "data_source": {
            "type": "WWW"
          }, 
          "output_raw_content_dir": "/saw/data/raw"
        }, 
        "writer": {
          "outputs": {
            "db": {
              "connection_string": "Server=localhost;Database=saw;Uid=saw_analyzer;Pwd=xxx;", 
              "type": "mysql", 
              "enabled": true, 
              "table": "features"
            }, 
            "file": {
              "enabled": false, 
              "type": "file", 
              "path": "/saw/output/dump.txt"
            }
          }, 
          "input_analyzed_content_dir": "/saw/data/analyzed"
        }, 
        "analyzer": {
          "input_raw_content_dir": "/saw/data/raw", 
          "output_analyzed_content_dir": "/saw/data/analyzed", 
          "extract_features": [
            "sentiment"
          ]
        }
      }
    }




Reusing Parameters
============================================

:In this section: We learn how to *reuse parameters* and how to define *hidden parameters*.


You might have noticed the "config duplication" in setting the locations of the raw and analyzed data files.

This can easily be avoided by reusing a single definition in multiple places, as demonstrated below.

In Figura, you should never have to repeat yourself.

::

    > cat saw_0300_reuse.fig
    # The following parameters are prefixed with underscores, to make them "hidden"
    # -- they will not be included in the final config container.
    # This is useful in cases where they only serve as temporary definitions to be reused.
    _root_dir = '/saw/data/'
    _raw_content_dir = _root_dir + 'raw'
    _analyzed_content_dir = _root_dir + 'analyzed'
    
    class saw:
        class searcher:
            # ...
            output_raw_content_dir = _raw_content_dir
            # ...
            
        class analyzer:
            # ...
            input_raw_content_dir = _raw_content_dir
            output_analyzed_content_dir = _analyzed_content_dir
            # ...
            
        class writer:
            # ...
            input_analyzed_content_dir = _analyzed_content_dir
            # ...

When processed and formatted as JSON, the output is the same as before.




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


::

    > cat saw_0400_commonality.fig
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

When processed and formatted as JSON::

    > figura_print saw_0400_commonality
    {
      "saw": {
        "searcher": {
          "alert": {
            "receipient": "admin@saw.zzz", 
            "enabled": true, 
            "channel": "email"
          }
        }, 
        "writer": {
          "alert": {
            "receipient": "admin@saw.zzz", 
            "enabled": true, 
            "channel": "email"
          }
        }, 
        "analyzer": {
          "alert": {
            "receipient": "admin@saw.zzz", 
            "enabled": true, 
            "channel": "email"
          }
        }
      }
    }




Extending Containers
============================================

:In this section: We learn how *basic config containers can be extended*.

Once again, you might have noticed that in the last example we had to repeat ourselves.
All modules contained the exact same definition, namely ``alert = _alert``.

`No way <index.html#the-zen-of-figura>`_.

Since there are parts which are common to all modules, it makes sense to define them once
in a *base-module config container*, and having each module extend it.

Here is how this is done.



::

    > cat saw_0500_extending.fig
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

When processed and formatted as JSON, the output is the same as before.




Overlyaing Containers
============================================

:In this section: We learn how *basic config containers can be overlayed*.

Suppose our admin is clueless when it comes to troubleshooting the algorithmic
part of the system, i.e. the analyzer.  We decide alerts from the analyzer should
go to our analyzers (no change to the other modules).

This can be done by *overlaying definitions on top of a base config container*, as
demonstrated below.


::

    > cat saw_0600_overlaying.fig
    class _saw_module:
        class alert:
            enabled = True
            channel = 'email'
            receipient = 'admin@saw.zzz'
    
    class saw:
        class searcher(_saw_module):
            # ...
            pass
            
        class analyzer(_saw_module):
            # ...
            class alert:  # Definitions inside this container *overlay* _saw_module.alert
                # Only need to define receipient. The rest is taken from _saw_module.alert
                receipient = 'analyzers@saw.zzz'
            
        class writer(_saw_module):
            # ...
            pass

When processed and formatted as JSON::

    > figura_print saw_0600_overlaying
    {
      "saw": {
        "searcher": {
          "alert": {
            "receipient": "admin@saw.zzz", 
            "enabled": true, 
            "channel": "email"
          }
        }, 
        "writer": {
          "alert": {
            "receipient": "admin@saw.zzz", 
            "enabled": true, 
            "channel": "email"
          }
        }, 
        "analyzer": {
          "alert": {
            "receipient": "analyzers@saw.zzz", 
            "enabled": true, 
            "channel": "email"
          }
        }
      }
    }




A Quick Recap
===================

So far we've covered the basic syntax, semantics and capabilities of the Figura language.
In the rest of this tuturial we cover the more advanced stuff.

The next sections are based on the config we have so far, with all the changes and additions
from past sections.


To recap, this is the full config file that we have so far. We name it ``saw.fig``::

    > cat tutorial/saw.fig
    
    _root_dir = '/saw/data/'
    _raw_content_dir = _root_dir + 'raw'
    _analyzed_content_dir = _root_dir + 'analyzed'
    
    class _saw_module:
        class alert:
            enabled = True
            channel = 'email'
            receipient = 'admin@saw.zzz'
    
    class saw:
        
        class searcher(_saw_module):
            keywords = [ 'figura', 'configuration', 'language' ]
            class data_source:
                type = 'WWW'
            output_raw_content_dir = _raw_content_dir
            
        class analyzer(_saw_module):
            input_raw_content_dir = _raw_content_dir
            output_analyzed_content_dir = _analyzed_content_dir
            extract_features = [ 'sentiment' ]
            class alert:
                receipient = 'analyzers@saw.zzz'
            
        class writer(_saw_module):
            input_analyzed_content_dir = _analyzed_content_dir
            class outputs:
                class db:
                    enabled = True
                    type = 'mysql'
                    connection_string = 'Server=localhost;Database=saw;Uid=saw_analyzer;Pwd=xxx;'
                    table = 'features'
                class file:
                    enabled = False
                    type = 'file'
                    path = '/saw/output/dump.txt'
    
    # This part is explained in the next section
    __entry_point__ = saw




Entry Points
=================

:In this section: We learn how to define config file's *entry point* (and why).

You might have noticed a small repetition or awkwardness in the examples so far.
The identifier ``saw`` is repeated. It appear both in the config file name (and the
figura path used for pointing to it), and the top-level config container defined in
the config file.  The code which uses the config definitions will have to be aware of
both.

To avoid this, we could just avoid the ``class saw:`` container and put the nested definitions
at file's top level directly.  However, this has the disadvantage that it prevents us from
extending the ``saw`` container if we ever want to. In other words, this will no longer be possible::

    from .saw import saw
    class experimental_saw(saw):
        ...

Instead, we can define file's *entry point*, using the ``__entry_point__`` directive.

::

    ...
    class saw:
        ...
    __entry_point__ = saw


::

    > cat saw_0750_entry.fig
    from saw import saw
    __entry_point__ = saw

This allows accessing the config using figura paths which skip the top ``saw`` level, as demonstrated below::

    > figura_print saw.searcher.keywords
    ['figura', 'configuration', 'language']

:Note: The issue described in this section might seem too minor to worry about, but it might not always be.
    The benefits of structuring your config correctly is underlined in the
    `Reorganizing Files <#reorganizing-files>`_ part of this tutorial.





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


The override set is defined as follows::

    > cat tutorial/saw_offline_ovd.fig
    
    _offline_root_dir = '/saw/offline/'
    _raw_content_dir = _offline_root_dir + 'raw'
    _analyzed_content_dir = _offline_root_dir + 'analyzed'
    
    class _offline_module_overrides:
        """  A base override set of the per-module offline override sets. """
        # Don't send alerts
        class alert:
            enabled = False
    
    class saw_offline_overrides:
        """ An override set for running SAW in offline mode. """
    
        # This config container represents overrides to be applied to other containers:
        __override__ = True
        
        class searcher(_offline_module_overrides):
            # Reading from archive, not WWW
            class data_source:
                type = 'archive'
                path = '/saw/archive/raw/'
            output_raw_content_dir = _raw_content_dir
            
        class analyzer(_offline_module_overrides):
            input_raw_content_dir = _raw_content_dir
            output_analyzed_content_dir = _analyzed_content_dir
            
        class writer(_offline_module_overrides):
            input_analyzed_content_dir = _analyzed_content_dir
            # Writing to a local directory
            class outputs:
                # Overshadow, don't overlay (See explanation below)
                __opaque_override__ = True
                # Write output to stdout
                class file:
                    enabled = True
                    type = 'file'
                    path = '/dev/stdout'
    
    __entry_point__ = saw_offline_overrides

This is what we get when applying the offline-overrides to the base config::

    > figura_print saw saw_offline_ovd
    {
      "searcher": {
        "keywords": [
          "figura", 
          "configuration", 
          "language"
        ], 
        "data_source": {
          "path": "/saw/archive/raw/", 
          "type": "archive"
        }, 
        "output_raw_content_dir": "/saw/offline/raw", 
        "alert": {
          "receipient": "admin@saw.zzz", 
          "enabled": false, 
          "channel": "email"
        }
      }, 
      "writer": {
        "outputs": {
          "file": {
            "enabled": true, 
            "type": "file", 
            "path": "/dev/stdout"
          }
        }, 
        "input_analyzed_content_dir": "/saw/offline/analyzed", 
        "alert": {
          "receipient": "admin@saw.zzz", 
          "enabled": false, 
          "channel": "email"
        }
      }, 
      "analyzer": {
        "input_raw_content_dir": "/saw/offline/raw", 
        "output_analyzed_content_dir": "/saw/offline/analyzed", 
        "extract_features": [
          "sentiment"
        ], 
        "alert": {
          "receipient": "analyzers@saw.zzz", 
          "enabled": false, 
          "channel": "email"
        }
      }
    }

:note: When given multiple arguments, ``figura_print`` interprets all arguments which come after the first
    as override sets to be applied to the first. It is therefore useful for flexibly constructing configs, by
    combining the main config with one or more override sets.  Here, we make use of this flexibility.

Overlay vs. Overshadow
-----------------------------

Note the use of the ``__opaque_override__`` directive.  What does it do?

The Writer module may support new outputs in the future, which will cause new configs to be added
to the ``outputs`` container.
In offline mode, we know we only want one ("file").
The default semantic of override sets is to **overlay**, which means that if we had this::

    ...
    class outputs:
        class file:
            ...

other output types (e.g. ``db``) would not be affected. Only the container defining the ``file`` output
type will get new values.

Instead, when we do this::

    ...
    class outputs:
        __opaque_override__ = True
        class file:
            ...

we employ the **overshadow** semantics, which simply sets the value of ``outputs`` to the definitions
included, hiding existing definitions in the overridee.  This ensures we write to only one place.





Reorganizing Files
============================================

:In this section: We admire Figura's flexibility while learning how our config-directory structure can be
    completely *reorganized without requiring a single change to the code* reading the config. (Now that's decoupling!)

Our SAW system proved a huge success over time, and over the years we added countless features to it.
Naturally, our config file grew very long.

It now makes sense to have a separate config file for each module in the system. There
are also common definitions which are used by multiple modules. We create another ``common.fig``
file for including those.

We replace our existing directory structure::

    /systems/config
    ├── __init__.fig
    ├── ...
    ├── saw.fig
    └── ...
    
With this new one (note how ``saw.fig`` is replaced with a directory named ``saw``)::

    /systems/config
    ├── __init__.fig
    ├── ...
    ├── saw
    │   ├── __init__.fig
    │   ├── analyzer.fig
    │   ├── common.fig
    │   ├── searcher.fig
    │   └── writer.fig
    └── ...



For example, here is what the new ``searcher.fig`` looks like (``analyzer.fig`` and ``writer.fig`` should be obvious)::

    > cat saw/searcher.fig
    from .common import saw_module, raw_content_dir
    
    class searcher(saw_module):
        keywords = [ 'figura', 'configuration', 'language' ]
        class data_source:
            type = 'WWW'
        output_raw_content_dir = raw_content_dir
        # <...all the other stuff addeed over the years...>
        
    __entry_point__ = searcher

While ``common.fig`` contains the common defintions::

    > cat saw/common.fig
    
    root_dir = '/saw/data/'
    raw_content_dir = root_dir + 'raw'
    analyzed_content_dir = root_dir + 'analyzed'
    
    class saw_module:
        class alert:
            enabled = True
            channel = 'email'
            receipient = 'admin@saw.zzz'

Everything works as before. For example::

    > figura_print saw.searcher.keywords
    ['figura', 'configuration', 'language']




