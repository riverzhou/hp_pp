#!/usr/bin/env python3

from setuptools import setup, Extension

source_files = ['hello_world.c', 'myhello.c']

module_name  = 'hello_world'

module1 = Extension ( 
                    module_name, 
                    sources = source_files,
                    extra_compile_args=['-std=gnu99', '-O3'],
                    )

setup   (
        name = 'HelloWorld',
        version = '1.0',
        description = 'This is a demo package',
        ext_modules = [module1],
        )


