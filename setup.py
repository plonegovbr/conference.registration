# -*- coding:utf-8 -*-

import os
from setuptools import setup, find_packages

version = '1.0'
long_description = open("README.rst").read() + "\n" + \
                   open(os.path.join("docs", "CREDITS.txt")).read() + "\n" + \
                   open(os.path.join("docs", "HISTORY.txt")).read()

setup(name='conference.registration',
      version=version,
      description="Management of user profiles in a conference site",
      long_description=long_description,
      classifiers=[
        "Development Status :: 3 - Alpha",
        # XXX: Replace Development Status if needed:
        # "Development Status :: 4 - Beta",
        "Framework :: Plone",
        "Framework :: Plone :: 4.1",
        "Framework :: Zope2",
        "License :: Other/Proprietary License",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='python plone zope simples_consultoria',
      author='Simples Consultoria',
      author_email='products@simplesconsultoria.com.br',
      url='http://www.simplesconsultoria.com.br',
      license='gpl',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['conference'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'collective.grok',
        'conference.profile',
        'plone.app.dexterity',
        'plone.formwidget.autocomplete',
        ],
      extras_require={
        'test': ['plone.app.testing'],
        },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
