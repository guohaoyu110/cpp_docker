"""Provide access to Python's configuration information.  The specific
configuration variables available depend heavily on the platform and
configuration.  The values may be retrieved using
get_config_var(name), and the list of variables is available via
get_config_vars().keys().  Additional convenience functions are also
available.

Written by:   Fred L. Drake, Jr.
Email:        <fdrake@acm.org>
"""

import os
import re
import sys

from .errors import DistutilsPlatformError

# These are needed in a couple of spots, so just compute them once.
PREFIX = os.path.normpath(sys.prefix)
EXEC_PREFIX = os.path.normpath(sys.exec_prefix)
BASE_PREFIX = os.path.normpath(sys.base_prefix)
BASE_EXEC_PREFIX = os.path.normpath(sys.base_exec_prefix)

# Path to the base directory of the project. On Windows the binary may
# live in project/PCBuild9.  If we're dealing with an x64 Windows build,
# it'll live in project/PCbuild/amd64.
# set for cross builds
if "_PYTHON_PROJECT_BASE" in os.environ:
    project_base = os.path.abspath(os.environ["_PYTHON_PROJECT_BASE"])
else:
    project_base = os.path.dirname(os.path.abspath(sys.executable))
if os.name == "nt" and "pcbuild" in project_base[-8:].lower():
    project_base = os.path.abspath(os.path.join(project_base, os.path.pardir))
# PC/VS7.1
if os.name == "nt" and "\\pc\\v" in project_base[-10:].lower():
    project_base = os.path.abspath(os.path.join(project_base, os.path.pardir,
                                                os.path.pardir))
# PC/AMD64
if os.name == "nt" and "\\pcbuild\\amd64" in project_base[-14:].lower():
    project_base = os.path.abspath(os.path.join(project_base, os.path.pardir,
                                                os.path.pardir))

# python_build: (Boolean) if true, we're either building Python or
# building an extension with an un-installed Python, so we use
# different (hard-wired) directories.
# Setup.local is available for Makefile builds including VPATH builds,
# Setup.dist is available on Windows
def _is_python_source_dir(d):
    for fn in ("Setup.dist", "Setup.local"):
        if os.path.isfile(os.path.join(d, "Modules", fn)):
            return True
    return False
_sys_home = getattr(sys, '_home', None)
if _sys_home and os.name == 'nt' and \
    _sys_home.lower().endswith(('pcbuild', 'pcbuild\\amd64')):
    _sys_home = os.path.dirname(_sys_home)
    if _sys_home.endswith('pcbuild'):   # must be amd64
        _sys_home = os.path.dirname(_sys_home)
def _python_build():
    if _sys_home:
        return _is_python_source_dir(_sys_home)
    return _is_python_source_dir(project_base)
python_build = _python_build()

# Calculate the build qualifier flags if they are defined.  Adding the flags
# to the include and lib directories only makes sense for an installation, not
# an in-source build.
build_flags = ''
try:
    if not python_build:
        build_flags = sys.abiflags
except AttributeError:
    # It's not a configure-based build, so the sys module doesn't have
    # this attribute, which is fine.
    pass

def get_python_version():
    """Return a string containing the major and minor Python version,
    leaving off the patchlevel.  Sample return values could be '1.5'
    or '2.2'.
    """
    return sys.version[:3]


def get_python_inc(plat_specific=0, prefix=None):
    """Return the directory containing installed Python header files.

    If 'plat_specific' is false (the default), this is the path to the
    non-platform-specific header files, i.e. Python.h and so on;
    otherwise, this is the path to platform-specific header files
    (namely pyconfig.h).

    If 'prefix' is supplied, use it instead of sys.base_prefix or
    sys.base_exec_prefix -- i.e., ignore 'plat_specific'.
    """
    if prefix is None:
        prefix = plat_specific and BASE_EXEC_PREFIX or BASE_PREFIX
    if os.name == "posix":
        if python_build:
            # Assume the executable is in the build directory.  The
            # pyconfig.h file should be in the same directory.  Since
            # the build directory may not be the source directory, we
            # must use "srcdir" from the makefile to find the "Include"
            # directory.
            base = _sys_home or project_base
            if plat_specific:
                return base
            if _sys_home:
                incdir = os.path.join(_sys_home, get_config_var('AST_H_DIR'))
            else:
                incdir = os.path.join(get_config_var('srcdir'), 'Include')
            return os.path.normpath(incdir)
        python_dir = 'python' + get_python_version() + build_flags
        if not python_build and plat_specific:
            import sysconfig
            return sysconfig.get_path('platinclude')
        return os.path.join(prefix, "include", python_dir)
    elif os.name == "nt":
        return os.path.join(prefix, "include")
    else:
        raise DistutilsPlatformError(
            "I don't know where Python installs its C header files "
            "on platform '%s'" % os.name)


def get_python_lib(plat_specific=0, standard_lib=0, prefix=None):
    """Return the directory containing the Python library (standard or
    site additions).

    If 'plat_specific' is true, return the directory containing
    platform-specific modules, i.e. any module from a non-pure-Python
    module distribution; otherwise, return the platform-shared library
    directory.  If 'standard_lib' is true, return the directory
    containing standard Python library modules; otherwise, return the
    directory for site-specific modules.

    If 'prefix' is supplied, use it instead of sys.base_prefix or
    sys.base_exec_prefix -- i.e., ignore 'plat_specific'.
    """
    is_default_prefix = not prefix or os.path.normpath(prefix) in ('/usr', '/usr/local')
    if prefix is None:
        if standard_lib:
            prefix = plat_specific and BASE_EXEC_PREFIX or BASE_PREFIX
        else:
            prefix = plat_specific and EXEC_PREFIX or PREFIX

    if os.name == "posix":
        libpython = os.path.join(prefix,
                                 "lib", "python" + get_python_version())
        if standard_lib:
            return libpython
        elif (is_default_prefix and
              'PYTHONUSERBASE' not in os.environ and
              'VIRTUAL_ENV' not in os.environ and
              'real_prefix' not in sys.__dict__ and
              sys.prefix == sys.base_prefix):
            return os.path.join(prefix, "lib", "python3", "dist-packages")
        else:
            return os.path.join(libpython, "site-packages")
    elif os.name == "nt":
        if standard_lib:
            return os.path.join(prefix, "Lib")
        else:
            return os.path.join(prefix, "Lib", "site-packages")
    else:
        raise DistutilsPlatformError(
            "I don't know where Python installs its library "
            "on platform '%s'" % os.name)



def customize_compiler(compiler):
    """Do any platform-specific customization of a CCompiler instance.

    Mainly needed on Unix, so we can plug in the information that
    varies across Unices and is stored in Python's Makefile.
    """
    if compiler.compiler_type == "unix":
        if sys.platform == "darwin":
            # Perform first-time customization of compiler-related
            # config vars on OS X now that we know we need a compiler.
            # This is primarily to support Pythons from binary
            # installers.  The kind and paths to build tools on
            # the user system may vary significantly from the system
            # that Python itself was built on.  Also the user OS
            # version and build tools may not support the same set
            # of CPU architectures for universal builds.
            global _config_vars
            # Use get_config_var() to ensure _config_vars is initialized.
            if not get_config_var('CUSTOMIZED_OSX_COMPILER'):
                import _osx_support
                _osx_support.customize_compiler(_config_vars)
                _config_vars['CUSTOMIZED_OSX_COMPILER'] = 'True'

        (cc, cxx, opt, cflags, ccshared, ldshared, shlib_suffix, ar, ar_flags,
         configure_cppflags, configure_cflags, configure_ldflags) = \
            get_config_vars('CC', 'CXX', 'OPT', 'CFLAGS',
                            'CCSHARED', 'LDSHARED', 'SHLIB_SUFFIX', 'AR', 'ARFLAGS',
                            'CONFIGURE_CPPFLAGS', 'CONFIGURE_CFLAGS', 'CONFIGURE_LDFLAGS')

        if 'CC' in os.environ:
            newcc = os.environ['CC']
            if (sys.platform == 'darwin'
                    and 'LDSHARED' not in os.environ
                    and ldshared.startswith(cc)):
                # On OS X, if CC is overridden, use that as the default
                #       command for LDSHARED as well
                ldshared = newcc + ldshared[len(cc):]
            cc = newcc
        if 'CXX' in os.environ:
            cxx = os.environ['CXX']
        if 'LDSHARED' in os.environ:
            ldshared = os.environ['LDSHARED']
        if 'CPP' in os.environ:
            cpp = os.environ['CPP']
        else:
            cpp = cc + " -E"           # not always
        if 'LDFLAGS' in os.environ:
            ldshared = ldshared + ' ' + os.environ['LDFLAGS']
        elif configure_ldflags:
            ldshared = ldshared + ' ' + configure_ldflags
        if 'CFLAGS' in os.environ:
            cflags = opt + ' ' + os.environ['CFLAGS']
            ldshared = ldshared + ' ' + os.environ['CFLAGS']
        elif configure_cflags:
            cflags = opt + ' ' + configure_cflags
            ldshared = ldshared + ' ' + configure_cflags
        if 'CPPFLAGS' in os.environ:
            cpp = cpp + ' ' + os.environ['CPPFLAGS']
            cflags = cflags + ' ' + os.environ['CPPFLAGS']
            ldshared = ldshared + ' ' + os.environ['CPPFLAGS']
        elif configure_cppflags:
            cpp = cpp + ' ' + configure_cppflags
            cflags = cflags + ' ' + configure_cppflags
            ldshared = ldshared + ' ' + configure_cppflags
        if 'AR' in os.environ:
            ar = os.environ['AR']
        if 'ARFLAGS' in os.environ:
            archiver = ar + ' ' + os.environ['ARFLAGS']
        else:
            archiver = ar + ' ' + ar_flags

        cc_cmd = cc + ' ' + cflags
        compiler.set_executables(
            preprocessor=cpp,
            compiler=cc_cmd,
            compiler_so=cc_cmd + ' ' + ccshared,
            compiler_cxx=cxx,
            linker_so=ldshared,
            linker_exe=cc,
            archiver=archiver)

        compiler.shared_lib_extension = shlib_suffix


def get_config_h_filename():
    """Return full pathname of installed pyconfig.h file."""
    if python_build:
        if os.name == "nt":
            inc_dir = os.path.join(_sys_home or project_base, "PC")
        else:
            inc_dir = _sys_home or project_base
    else:
        inc_dir = get_python_inc(plat_specific=1)

    return os.path.join(inc_dir, 'pyconfig.h')


def get_makefile_filename():
    """Return full pathname of installed Makefile from the Python build."""
    if python_build:
        return os.path.join(_sys_home or project_base, "Makefile")
    lib_dir = get_python_lib(plat_specific=0, standard_lib=1)
    config_file = 'config-{}{}'.format(get_python_version(), build_flags)
    if hasattr(sys.implementation, '_multiarch'):
        config_file += '-%s' % sys.implementation._multiarch
    return os.path.join(lib_dir, config_file, 'Makefile')


def parse_config_h(fp, g=None):
    """Parse a config.h-style file.

    A dictionary containing name/value pairs is returned.  If an
    optional dictionary is passed in as the second argument, it is
    used instead of a new dictionary.
    """
    if g is None:
        g = {}
    define_rx = re.compile("#define ([A-Z][A-Za-z0-9_]+) (.*)\n")
    undef_rx = re.compile("/[*] #undef ([A-Z][A-Za-z0-9_]+) [*]/\n")
    #
    while True:
        line = fp.readline()
        if not line:
            break
        m = define_rx.match(line)
        if m:
            n, v = m.group(1, 2)
            try: v = int(v)
            except ValueError: pass
            g[n] = v
        else:
            m = undef_rx.match(line)
            if m:
                g[m.group(1)] = 0
    return g


# Regexes needed for parsing Makefile (and similar syntaxes,
# like old-style Setup files).
_variable_rx = re.compile("([a-zA-Z][a-zA-Z0-9_]+)\s*=\s*(.*)")
_findvar1_rx = re.compile(r"\$\(([A-Za-z][A-Za-z0-9_]*)\)")
_findvar2_rx = re.compile(r"\${([A-Za-z][A-Za-z0-9_]*)}")

def parse_makefile(fn, g=None):
    """Parse a Makefile-style file.

    A dictionary containing name/value pairs is returned.  If an
    optional dictionary is passed in as the second argument, it is
    used instead of a new dictionary.
    """
    from distutils.text_file import TextFile
    fp = TextFile(fn, strip_comments=1, skip_blanks=1, join_lines=1, errors="surrogateescape")

    if g is None:
        g = {}
    done = {}
    notdone = {}

    while True:
        line = fp.readline()
        if line is None: # eof
            break
        m = _variable_rx.match(line)
        if m:
            n, v = m.group(1, 2)
            v = v.strip()
            # `$$' is a literal `$' in make
            tmpv = v.replace('$$', '')

            if "$" in tmpv:
                notdone[n] = v
            else:
                try:
                    v = int(v)
                except ValueError:
                    # insert literal `$'
                    done[n] = v.replace('$$', '$')
                else:
                    done[n] = v

    # Variables with a 'PY_' prefix in the makefile. These need to
    # be made available without that prefix through sysconfig.
    # Special care is needed to ensure that variable expansion works, even
    # if the expansion uses the name without a prefix.
    renamed_variables = ('CFLAGS', 'LDFLAGS', 'CPPFLAGS')

    # do variable interpolation here
    while notdone:
        for name in list(notdone):
            value = notdone[name]
            m = _findvar1_rx.search(value) or _findvar2_rx.search(value)
            if m:
                n = m.group(1)
                found = True
                if n in done:
                    item = str(done[n])
                elif n in notdone:
                    # get it on a subsequent round
                    found = False
                elif n in os.environ:
                    # do it like make: fall back to environment
                    item = os.environ[n]

                elif n in renamed_variables:
                    if name.startswith('PY_') and name[3:] in renamed_variables:
                        item = ""

                    elif 'PY_' + n in notdone:
                        found = False

                    else:
                        item = str(done['PY_' + n])
                else:
                    done[n] = item = ""
                if found:
                    after = value[m.end():]
                    value = value[:m.start()] + item + after
                    if "$" in after:
                        notdone[name] = value
                    else:
                        try: value = int(value)
                        except ValueError:
                            done[name] = value.strip()
                        else:
                            done[name] = value
                        del notdone[name]

                        if name.startswith('PY_') \
                            and name[3:] in renamed_variables:

                            name = name[3:]
                            if name not in done:
                                done[name] = value
            else:
                # bogus variable reference; just drop it since we can't deal
                del notdone[name]

    fp.close()

    # strip spurious spaces
    for k, v in done.items():
        if isinstance(v, str):
            done[k] = v.strip()

    # save the results in the global dictionary
    g.update(done)
    return g


def expand_makefile_vars(s, vars):
    """Expand Makefile-style variables -- "${foo}" or "$(foo)" -- in
    'string' according to 'vars' (a dictionary mapping variable names to
    values).  Variables not present in 'vars' are silently expanded to the
    empty string.  The variable values in 'vars' should not contain further
    variable expansions; if 'vars' is the output of 'parse_makefile()',
    you're fine.  Returns a variable-expanded version of 's'.
    """

    # This algorithm does multiple expansion, so if vars['foo'] contains
    # "${bar}", it will expand ${foo} to ${bar}, and then expand
    # ${bar}... and so forth.  This is fine as long as 'vars' comes from
    # 'parse_makefile()', which takes care of such expansions eagerly,
    # according to make's variable expansion semantics.

    while True:
        m = _findvar1_rx.search(s) or _findvar2_rx.search(s)
        if m:
            (beg, end) = m.span()
            s = s[0:beg] + vars.get(m.group(1)) + s[end:]
        else:
            break
    return s


_config_vars = None

def _init_posix():
    """Initialize the module as appropriate for POSIX systems."""
    # _sysconfigdata is generated at build time, see the sysconfig module
    from _sysconfigdata import build_time_vars
    global _config_vars
    _config_vars = {}
    _config_vars.update(build_time_vars)


def _init_nt():
    """Initialize the module as appropriate for NT"""
    g = {}
    # set basic install directories
    g['LIBDEST'] = get_python_lib(plat_specific=0, standard_lib=1)
    g['BINLIBDEST'] = get_python_lib(plat_specific=1, standard_lib=1)

    # XXX hmmm.. a normal install puts include files here
    g['INCLUDEPY'] = get_python_inc(plat_specific=0)

    g['EXT_SUFFIX'] = '.pyd'
    g['EXE'] = ".exe"
    g['VERSION'] = get_python_version().replace(".", "")
    g['BINDIR'] = os.path.dirname(os.path.abspath(sys.executable))

    global _config_vars
    _config_vars = g


def get_config_vars(*args):
    """With no arguments, return a dictionary of all configuration
    variables relevant for the current platform.  Generally this includes
    everything needed to build extensions and install both pure modules and
    extensions.  On Unix, this means every variable defined in Python's
    installed Makefile; on Windows it's a much smaller set.

    With arguments, return a list of values that result from looking up
    each argument in the configuration variable dictionary.
    """
    global _config_vars
    if _config_vars is None:
        func = globals().get("_init_" + os.name)
        if func:
            func()
        else:
            _config_vars = {}

        # Normalized versions of prefix and exec_prefix are handy to have;
        # in fact, these are the standard versions used most places in the
        # Distutils.
        _config_vars['prefix'] = PREFIX
        _config_vars['exec_prefix'] = EXEC_PREFIX

        # For backward compatibility, see issue19555
        SO = _config_vars.get('EXT_SUFFIX')
        if SO is not None:
            _config_vars['SO'] = SO

        # Always convert srcdir to an absolute path
        srcdir = _config_vars.get('srcdir', project_base)
        if os.name == 'posix':
            if python_build:
                # If srcdir is a relative path (typically '.' or '..')
                # then it should be interpreted relative to the directory
                # containing Makefile.
                base = os.path.dirname(get_makefile_filename())
                srcdir = os.path.join(base, srcdir)
            else:
                # srcdir is not meaningful since the installation is
                # spread about the filesystem.  We choose the
                # directory containing the Makefile since we know it
                # exists.
                srcdir = os.path.dirname(get_makefile_filename())
        _config_vars['srcdir'] = os.path.abspath(os.path.normpath(srcdir))

        # Convert srcdir into an absolute path if it appears necessary.
        # Normally it is relative to the build directory.  However, during
        # testing, for example, we might be running a non-installed python
        # from a different directory.
        if python_build and os.name == "posix":
            base = project_base
            if (not os.path.isabs(_config_vars['srcdir']) and
                base != os.getcwd()):
                # srcdir is relative and we are not in the same directory
                # as the executable. Assume executable is in the build
                # directory and make srcdir absolute.
                srcdir = os.path.join(base, _config_vars['srcdir'])
                _config_vars['srcdir'] = os.path.normpath(srcdir)

        # OS X platforms require special customization to handle
        # multi-architecture, multi-os-version installers
        if sys.platform == 'darwin':
            import _osx_support
            _osx_support.customize_config_vars(_config_vars)

    if args:
        vals = []
        for name in args:
            vals.append(_config_vars.get(name))
        return vals
    else:
        return _config_vars

def get_config_var(name):
    """Return the value of a single variable using the dictionary
    returned by 'get_config_vars()'.  Equivalent to
    get_config_vars().get(name)
    """
    if name == 'SO':
        import warnings
        warnings.warn('SO is deprecated, use EXT_SUFFIX', DeprecationWarning, 2)
    return get_config_vars().get(name)