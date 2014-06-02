#!/usr/bin/env python3

from setuptools import setup, Extension

setup(ext_modules=[Extension('hello_world', sources=["hello_world.c"])])

