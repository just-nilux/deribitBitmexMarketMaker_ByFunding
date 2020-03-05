#!/usr/bin/env python
from setuptools import setup
from os.path import join, dirname

here = dirname(__file__)

setup(name='market-maker',
      version='0.1.0',
      description='Make Markets Across Markets!',
      long_description=open(join(here, 'README.md')).read(),
      author='Jarett Dunn',
      author_email='jarettrsdunn@gmail.com',
      url='',
      install_requires=[
          'websocket-client==0.53.0','ccxt', 'deribit_api'
      ],
      packages=['util'],
      )
