"""
Definition of `FiguraPath <#figura.path.FiguraPath>`_.
"""

from .settings import get_setting
from .importutils import is_importable_path

################################################################################

class FiguraPath(object):
    """
    A path to a Figura config file, or a value within one.
    The path contains two (optional) parts: the file-path, which is a python-import
    path (e.g. figura.tests), and a (deep) attribute-path to point to a specific
    value inside the file.
    
    The two parts are concatenated together with the same delimiter used by each
    of the parts, thus one cannot immediately tell
    
    E.g.: a path representing "the value of ``A.B.b`` inside the config file ``figura.tests.config.override``,
    is written like: ``figura.tests.config.override.A.B.b``.
    """
    
    DELIM = '.'
    """
    The delimiter used for all purposes: inside the file-path, between file-path
    and attr-path, and inside attr-path.
    """

    #===================================================================================================================
    
    def __init__(self, path):
        self._path = self._normalize_other(path)
    
    #===================================================================================================================
    # Path-parts handling
    #===================================================================================================================

    @classmethod
    def from_parts(cls, file_path, attr_path = None):
        """
        Construct a FiguraPath object from its two parts.
        
        :param file_path: a python import-path. E.g. ``figura.tests.config.override``
        :param attr_path: a (deep) attribute inside the file. E.g. ``A.B.b``
        """
        path_str = cls.DELIM.join([ part for part in (file_path, attr_path) if part ])
        return cls(path_str)

    def split_parts(self):
        """
        Split the path to its two parts: the file-path and the attr-path.
        Note this method looks for python modules in the filesystem to
        determine what prefix of the FiguraPath is a valid file-path. The
        rest is considered the attr-path.
        
        :return: a 2-tuple of (file_path, attr_path)
        
        .. testsetup:: 
    
            from figura.path import FiguraPath
        
        >>> FiguraPath('figura.hello_world.greeting.greetee').split_parts()
        ('figura.hello_world', 'greeting.greetee')
        """
        tokens = self._path.split(self.DELIM)
        n = len(tokens)
        for idx in reversed(range(n + 1)):
            file_path = self.DELIM.join(tokens[:idx])
            if self._is_figura_file_path(file_path):
                break
        return self.DELIM.join(tokens[:idx]), self.DELIM.join(tokens[idx:])

    def _is_figura_file_path(self, path):
        fig_ext = get_setting('CONFIG_FILE_EXT')
        return is_importable_path(path, fig_ext)
    
    #===================================================================================================================
    # operators for FiguraPath manipulation
    #===================================================================================================================

    def __add__(self, other):
        """
        Add a string to the end of the path.
        :note: this follows string semantics. No implicit delimiter is added.

        .. testsetup:: 
    
            from figura.path import FiguraPath
        
        >>> FiguraPath('abc') + 'd'
        FiguraPath('abcd')
        """
        other = self._normalize_other(other)
        return self._like_self(self._path + other)

    def __mod__(self, other):
        """
        The FiguraPath equivalent of string formatting.

        .. testsetup:: 
    
            from figura.path import FiguraPath
        
        >>> FiguraPath('foo.%s.bar') % 'baz'
        FiguraPath('foo.baz.bar')
        """
        other = self._normalize_other(other)
        return self._like_self(self._path % other)

    @property
    def parent(self):
        """
        The parent path, one level up.

        .. testsetup:: 
    
            from figura.path import FiguraPath
        
        >>> FiguraPath('a.bb.ccc').parent
        FiguraPath('a.bb')
        >>> FiguraPath('a').parent is None
        True
        """
        path = self._path.rpartition(self.DELIM)[0]
        if path:
            return FiguraPath(path)
        else:
            return None
    
    @property
    def basename(self):
        """
        The basename of the path.
        
        .. testsetup:: 
    
            from figura.path import FiguraPath

        >>> FiguraPath('a.b').basename
        'b'
        """
        x = self._path.rpartition(self.DELIM)[2]
        if x:
            return x
        else:
            return None
    
    def _normalize_other(self, other):
        try:
            return other._path
        except AttributeError:
            pass
        return other
    
    def _like_self(self, other):
        return type(self)(other)

    #===================================================================================================================
    # python stuff
    #===================================================================================================================

    def __repr__(self):
        return '%s(%r)' % ( type(self).__name__, self._path )
    
    def __str__(self):
        return self._path
    
    def __hash__(self):
        return hash(( type(self), str(self) ))
    
    def __eq__(self, other):
        try:
            return self._path == other._path
        except AttributeError:
            return NotImplemented
    
    def __ne__(self, other):
        return not (self == other)
    
    def __nonzero__(self):
        return bool(self._path)


def to_figura_path(path):
    """
    Convert values of different types to a FiguraPath.

    .. testsetup:: 

        from figura.path import FiguraPath, to_figura_path
    
    >>> to_figura_path('a.b.c')
    FiguraPath('a.b.c')
    >>> to_figura_path(FiguraPath('a.b.c'))
    FiguraPath('a.b.c')
    >>> to_figura_path(('a.b', 'C.d'))
    FiguraPath('a.b.C.d')
    """
    if isinstance(path, FiguraPath):
        return path
    elif isinstance(path, (list, tuple)) and len(path) == 2:
        return FiguraPath.from_parts(*path)
    else:
        return FiguraPath(path)

################################################################################
