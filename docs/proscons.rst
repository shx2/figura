==============================
Pros and Cons of Using Figura
==============================

What is it good for?
=========================

To begin with, Figura allows **re-using, extending, and combining config structures** in a variety of
ways.  This gives you the freedom to structure your config files in an intuitive, readable, and manageable way.
You should **never repeat yourself** in the process, no copy-pasting is required.

This flexibility also allows the **semantics and inter-relations of config-params to be expressed
in the config files**, as opposed to encoded in your code. This keeps your config-params-reading code
clean and simple, only dealing with the final "raw" config values.

Furthermore, Figura natively supports the notion of an **override-set**, i.e. a config "patch" to
be applied to other configs.  This allows great flexibility in building and combining different
configs.
For example, suppose your program has 5 independent features, each is off by default, and can
be enabled from configuration. Enabling each feature might require setting more than one config
param. With Figura, you simply create an override-set file for each features, and when you run your
program, you choose which override-sets to apply to the base config. This way you can avoid creating a
separate config file for each subset of features you want to use (in this example there are 2^N-1=31).

Specifying config **overrides from command line** is also supported natively, allowing even more
flexibility.

Figura also allows **flexibility in the way you organize your config directories**, and how you design the different
parts of your configuraion for reusability and flexibility.
In many cases you can completely reorganize the structure of your config files, the dependency
between them, and how sub-configs are reused, without having to change anything in the code
which uses the config params.

It is worth remembering that **each Figura config file is a valid Python module**. From this, many benefits arise (but
also some limitations).

For example, it can make use of the **rich syntax of the Python language** (e.g. comments, arithmetic expressions),
and wide **variaty of tools supporting it** (e.g. syntax highlighting, auto docs generation, pylint, pyflakes).


What is it bad for? (spoiler: security)
=========================================

Under certain (yet unusual) threat models, Figura should be considered utterly insecure.

Unlike most "raw" config languages, reading Figura files is done by loading Python modules,
during which arbitrary code inside those modules gets executed.  Typically there will be no
"real code" in the Figura files, but a malicious user can plant it there.

This means that if your **threat model includes untrusted users modifying config files** or somehow injecting
values into config files which are later read by your system, you should use a "dumb" configuration
language, such as JSON. Using Figura in this case can allow malicious users to run arbitrary code
on your machines. (This is not usually the case, of course, since configuration files are typically sensitive
system files.)

Other Pros and Cons
=========================

* [PRO] You can do anything inside a config file.

    - E.g., instead of something like::
        
        running_times_of_day = [ '0:00, '2:00', '4:00', <...more stuff here...>, '22:00' ]
        
      You can do::
      
        running_times_of_day = [ '%s:00'%hh for hh in range(0, 24, 2) ]
      
    - In general, these things are discouraged because config files should be definition-oriented. Yet, it can
      be useful in some cases. Since we're all responsible adults here, in cases you find it useful, you can do it.

* [CON] You can do anything inside a config file. 'Nuff said.
      
* [CON] Setup overhead caused by Python's import mechanism:

  - ``PYTHONPATH`` should be set correctly.
  -  relevant ``__init__.fig`` files must be created.

* [CON] Syntax awkwardness, caused by using a non-config-minded language (Python) for config purposes.(The syntax might seem awkward at first, but by no means complex. It is really simple, especially for Pythoners.)

  - you don't intuitively expect using words like ``class`` to define configs
    but since config containers are built upon python classes, that's what is used.
  - Python is indentation-sensitive, which is annoying to some non-Pythoners at first.
  - Empty config containers (though you rarely need them), must contain the statement ``pass``
    in order for the syntax to be correct.
  - Some reserved words may not be used as config parameters (e.g. ``class``, ``for``, ``while``, ``try``).

