import os
from pathlib import Path

from setuptools import find_packages, setup

import setup_utils

version_file = Path(__file__).parent / 'configure.py'

version = setup_utils.get_version_from_file(version_file)

PACKAGE_NAME = 'ubuviz-configure'

if os.environ.get('PACKAGE_DEVELOPMENT') is not None:
    version = setup_utils.get_development_version_from_file(version_file,
                                                            int(os.environ.get('PACKAGE_DEVELOPMENT')),
                                                            os.environ.get('PACKAGE_COMMIT'))

    setup_utils.set_version_to_file(version_file, version)

requirements = setup_utils.get_requirements_from_file(Path(__file__).parent / 'requirements.txt')

setup(
    name=PACKAGE_NAME,
    url='https://github.com/alfred82santa/configure',
    author='Andrey Popp, Alexander Solovyov, Alfred Santacatalina',
    version=version,
    author_email='Andrey Popp <8mayday@gmail.com>, Alexander Solovyov <alexander@solovyov.net>, Alfred Santacatalina <alfred82santa@gmail.com>',
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Development Status :: 4 - Beta'],
    py_modules=["configure"],
    install_requires=requirements,
    description='configuration toolkit based on YAML',
    long_description=(Path(__file__).parent / 'README.rst').read_text(),
    long_description_content_type='text/x-rst',
    zip_safe=True
)
