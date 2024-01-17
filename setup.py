#!/usr/bin/env python

from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()
    
requirements = ['numpy', 
                'anytree',
                'pyqt5',
                'screeninfo',
                'signalslot',
                'python-dateutil',
                'markdown']

setup(name='taskplanner',
      version='1',
      description='Task manager with Gantt chart.',
      long_description=readme(),
      url='https://github.com/Jiedz/taskplanner',
      author='Jiedz',
      author_email='',
      license='',
      packages=['taskplanner'],
      py_modules=[],
      install_requires=requirements)
