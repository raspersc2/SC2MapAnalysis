import os
import shutil

from distutils.command.build_ext import build_ext
from distutils.core import Distribution
from distutils.core import Extension
from distutils.errors import CCompilerError
from distutils.errors import DistutilsExecError
from distutils.errors import DistutilsPlatformError
import numpy


extensions = [
    Extension('mapanalyzerext',
              sources=[os.path.join('src', 'cext', 'ma_ext.c')],
              include_dirs=[numpy.get_include()],
              extra_compile_args=["-DNDEBUG", "-O2"]),
]


class ExtBuilder(build_ext):
    # This class allows C extension building to fail.

    built_extensions = []

    def run(self):
        try:
            build_ext.run(self)
        except (DistutilsPlatformError, FileNotFoundError):
            print("Unable to build the C extensions")

    def build_extension(self, ext):
        try:
            build_ext.build_extension(self, ext)
        except (CCompilerError, DistutilsExecError, DistutilsPlatformError, ValueError):
            print('Unable to build the "{}" C extension, '
                  "python_ctypes will use the pure python version of the extension.".format(ext.name))


def build(setup_kwargs):
    """
    This function is mandatory in order to build the extensions.
    """
    print(setup_kwargs)
    distribution = Distribution({"name": "python_ctypes", "ext_modules": extensions})
    distribution.package_dir = "python_ctypes"

    cmd = ExtBuilder(distribution)
    cmd.ensure_finalized()
    cmd.run()

    # Copy built extensions back to the project
    for output in cmd.get_outputs():
        relative_extension = os.path.relpath(output, cmd.build_lib)
        if not os.path.exists(output):
            continue

        shutil.copyfile(output, relative_extension)
        mode = os.stat(relative_extension).st_mode
        mode |= (mode & 0o444) >> 2
        os.chmod(relative_extension, mode)

    return setup_kwargs


if __name__ == "__main__":
    build({})
