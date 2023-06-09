from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import os
import sys
import numpy

ext_modules = [
    Extension('mapanalyzerext',
            sources=[os.path.join('src', 'cext', 'ma_ext.c')],
            include_dirs=[numpy.get_include()],
            extra_compile_args=["-DNDEBUG", "-O2"]),
]

class ExtBuilder(build_ext):
    def run(self):
        try:
            build_ext.run(self)
        except Exception as e:
            raise BuildFailed(str(e))

    def build_extension(self, ext):
        try:
            build_ext.build_extension(self, ext)
        except Exception as e:
            raise BuildFailed(str(e))

class BuildFailed(Exception):
    pass

def build(setup_kwargs):
    setup_kwargs.update({
        'ext_modules': ext_modules,
        'cmdclass': {'build_ext': ExtBuilder},
    })

if __name__ == '__main__':
    setup(
        name='MapAnalyzer',
        version='0.1.0',
        description='',
        packages=['MapAnalyzer'],
        ext_modules=ext_modules,
        cmdclass={'build_ext': ExtBuilder},
        zip_safe=False,
    )
