=========
Configure
=========

**FORK** from https://github.com/andreypopp/configure

**ORGINAL AUTHOR** Andrey Popp @andreypopp

YAML configuration library which provides:

* interpolation for string configuration values

* configuration inheritance

* configuration composition

* object level configuration (like construct this object by calling some
  function with some arguments)

------------
Installation
------------

.. code-block:: bash

    $ pip install configure-fork

---------
Changelog
---------

0.6.1
-----

* Fix imports in newer Python versions. Thx @TheAbhijeet.
* Added default value for environment variables resolvers (use `?=` after variable name).

    .. code-block:: yaml

        config_field_1:!envvar MY_ENV_VAR_1?=1
        config_field_2: ENV:MY_ENV_VAR_2?="my value"


0.6.0
-----

* Added ENVVAR resolver in order to allow to use environment variables.

    .. code-block:: yaml

        config_field:!envvar PYTHON_PATH

* Added implicit resover for ENVVAR resolver:

    .. code-block:: yaml

        config_field: ENV:PYTHON_PATH

* Modified concat resolver to allow to use environment variables:

    .. code-block:: yaml

        config_field: ENV:HOME "/app/" ENV:OTHER_VAR var.in.python

* Changed name in order to allow to publish on pypi

0.5.1
-----

* Python3 (Python2 no compatible any more).

* Concatenate variables on configuration:

    .. code-block:: yaml

        config_field:!concat var.in.python "/relative/path"


* Support for implicit resolvers from PyYaml.

* Added concat implicit resolver:

    .. code-block:: yaml

        config_field: var.in.python "/relative/path"

0.5
---

* constructors and multi constructors now can be registered via
  Configuration.add_constructor and Configuration.add_multi_constructor
  decorators

* fix serious bug with factory and obj directives: previously they dropped away
  nested objects such as lists and/or mappings

* configure_logging call now can be made inside config via !logging constructor

* Configuration.configure() now called inside
  Configuration.{from_file,from_string,from_dict}() class methods, controlled
  via configure=True keyword argument

0.4.8
-----

* handle kwargs in factory directive

0.4.7
-----

* coerce filename to abs path
* directory — check if it exists and create if not
* interpolate config before YAML parsing

0.4.6
-----

* bytesize

0.4.5
-----

* bugfix release

0.4.4
-----

* add PyYAML to requirements

0.4.3
-----

* fix factories w/o args

0.4.2
-----

* fix configuration of values inside sequences (lists)

0.4.1
-----

* fix ``configure_logging`` formatters configuration

0.4
---

* remove ``configure.module`` -- it was a bad idea to synthesize new Python
  modules on a fly

0.3.4
-----

* added ``configure.module`` module which allows exposing configuration as
  synthesized Python module.


Development takes place at https://github.com/alfred82santa/configure
