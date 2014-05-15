# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='CrowdProcess',
    version='0.1.2',
    packages=['crowdprocess'],
    license='MIT',
    maintainer='João Jerónimo',
    maintainer_email='jj@crowdprocess.com',
    url='https://github.com/CrowdProcess/crpy',
    long_description=open('README.rst').read(),
    install_requires=[
        "requests"
    ]
)