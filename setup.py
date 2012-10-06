#!/usr/bin/env python

from setuptools import setup


setup(name='txTemplate',
      version='1.0.2',
      description='Twisted Adapters for Templating Engines',
      long_description=open("README.rst", "r").read(),
      author='Mike Steder',
      author_email='steder@gmail.com',
      url='http://github.com/steder/txtemplate',
      packages=['txtemplate',
                'txtemplate.test'],
      test_suite="txtemplate.test",
      install_requires=["genshi",
                        "jinja2",
                        "twisted"],
      license="MIT",
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7'
          ]
)
