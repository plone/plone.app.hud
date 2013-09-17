# -*- coding: utf-8 -*-
"""Installer for the plone.app.hud package."""

from setuptools import find_packages
from setuptools import setup

import os


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = \
    read('README.rst') + \
    read('docs', 'CHANGELOG.rst')

setup(
    name='plone.app.hud',
    version='1.0a1',
    description="Plone Heads Up Display Panels",
    long_description=long_description,
    # Get more from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
    ],
    keywords='Plone HUD Panels',
    author='Plone Foundation',
    author_email='plone-developers@lists.sourceforge.net',
    url='http://pypi.python.org/pypi/plone.app.hud',
    license='GPL version 2',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['plone', 'plone.app'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Pillow',
        'Plone',
        'plone.api',
        'plone.hud',
        'setuptools',
    ],
    extras_require={
        'test': [
            'mock',
            'plone.app.testing',
            'unittest2',
        ],
        'develop': [
            'Products.Clouseau',
            'Products.DocFinderTab',
            'Products.PDBDebugMode',
            'Products.PrintingMailHost',
            'Sphinx',
            'coverage',
            'flake8',
            'jarn.mkrelease',
            'niteoweb.loginas',
            'plone.app.debugtoolbar',
            'plone.reload',
            'zest.pocompile',
            'zest.releaser',
            'zptlint',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
