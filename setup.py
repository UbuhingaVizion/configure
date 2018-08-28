import ast

import os
from setuptools import setup

PACKAGE_NAME = 'whalesong'

path = os.path.join(os.path.dirname(__file__), 'configure.py')

with open(path, 'r') as file:
    t = compile(file.read(), path, 'exec', ast.PyCF_ONLY_AST)
    for node in (n for n in t.body if isinstance(n, ast.Assign)):
        if len(node.targets) != 1:
            continue

        name = node.targets[0]
        if not isinstance(name, ast.Name) or \
                name.id not in ('__version__', '__version_info__', 'VERSION'):
            continue

        v = node.value
        if isinstance(v, ast.Str):
            version = v.s
            break
        if isinstance(v, ast.Tuple):
            r = []
            for e in v.elts:
                if isinstance(e, ast.Str):
                    r.append(e.s)
                elif isinstance(e, ast.Num):
                    r.append(str(e.n))
            version = '.'.join(r)
            break

# Get the long description from the README file
with open(os.path.join(os.path.dirname(__file__), 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="configure-fork",
    version=version,
    description="configuration toolkit based on YAML",
    long_description=long_description,
    author="Andrey Popp, Alexander Solovyov, Alfred Santacatalina",
    author_email="Andrey Popp <8mayday@gmail.com>, Alexander Solovyov <alexander@solovyov.net>, Alfred Santacatalina <alfred82santa@gmail.com>",
    url='https://github.com/alfred82santa/configure',
    py_modules=["configure"],
    test_suite="tests",
    install_requires=["pyyaml"],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.6',
    ],
    zip_safe=False)
