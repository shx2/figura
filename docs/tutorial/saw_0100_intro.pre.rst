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

