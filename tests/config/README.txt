
Some implicit or "hidden" tests included here:

 * should_ignore_ext.py -- this tests files with ".py" extension are ignored by figura
 * _should_ignore_private.fig -- this tests files starting with an underscore are ignored by figura
 * samename.* -- this tests figura successfully reads the *.fig file when there's another *.py file
    with the same name, and also that it doesn't break regular importing of the *.py file
