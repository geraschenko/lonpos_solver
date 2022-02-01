"""Install lonpos."""

from setuptools import setup

setup(
    name='lonpos_solver',
    version='0.0',
    description='A Lonpos solver.',
    author='Anton Geraschenko',
    author_email='geraschenko@gmail.com',
    url='https://github.com/geraschenko/tree/master/lonpos_solver',
    packages=['lonpos_solver'],
    install_requires=[
        'matplotlib',
        'numpy',
    ],
    python_requires='>=3.6',
)
