import logging
from setuptools import setup

logger = logging.getLogger(__name__)

requirements = [  # pragma: no cover
        "wheel",
        "numpy",
        "Cython",
        "pyastar@git+git://github.com/hjweide/pyastar.git@master#egg=pyastar",
        "burnysc2",
        "matplotlib",
        "scipy",
        "loguru",
        "tqdm",
        "scikit-image",

]
setup(  # pragma: no cover
        name="sc2mapanalyzer",
        # version=f"{__version__}",
        version="0.0.76",
        install_requires=requirements,
        setup_requires=["wheel", "numpy"],
        extras_require={
                "dev": [
                        "pytest",
                        "pytest-html",
                        "monkeytype",
                        "mypy",
                        "mpyq",
                        "pytest-asyncio",
                        "hypothesis",
                        "pytest-benchmark",
                        "sphinx",
                        "sphinx-autodoc-typehints",
                        "pytest-cov",
                        "coverage",
                        "codecov",
                        "mutmut",
                        "radon",
                ]
        },
)
