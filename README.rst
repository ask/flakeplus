=================================
 flakeplus - additional pyflakes
=================================

:Version: 1.0.0
:Download: http://pypi.python.org/pypi/flakeplus/
:Source: http://github.com/ask/flakeplus/
:Keywords: flakes, development, process

--

.. contents::
    :local:

Overview
========

flakeplus detects some additional flakes, part of the release process
for Celery, Kombu et.al.

Flakes
------

- All files must import `absolute_import` from ``__future__``.
- If Python 2.5 is a target, any file using the with statement
  must also import that from ``__future__``.
- Code cannot contain debugging print statements

    A debugging print statement is any print
    emitting a string that

        - optionally starts with any sequence of non-alphanumeric chars
        - an all-uppercase word followed by a colon,

    Examples::

        print("CONN: %r" % (connection, ))     # DEBUG!

        print("The connection was lost")       # NOT DEBUG

        print("> STUPID: %r" % (obj, ))        # DEBUG!

        print(">>>>> OMFG: %r !!!!" % (obj, )) # definitely DEBUG!


Example
=======

flakeplus is run from the commandline::

    $ flakeplus dir1 .. dirN

If the target version is 2.6 and above, use the ``2.6`` switch::

    $ flakeplus --2.6 dir1 .. dirN

Installation
============

You can install flakeplus either via the Python Package Index (PyPI)
or from source.

To install using `pip`,::

    $ pip install -U flakeplus

To install using `easy_install`,::

    $ easy_install -U flakeplus

Downloading and installing from source
--------------------------------------

Download the latest version of flakeplus from
http://pypi.python.org/pypi/flakeplus/

You can install it by doing the following,::

    $ tar xvfz flakeplus-0.0.0.tar.gz
    $ cd flakeplus-0.0.0
    $ python setup.py build
    # python setup.py install # as root

Using the development version
-----------------------------

You can clone the repository by doing the following::

    $ git clone git://github.com/ask/flakeplus.git

.. _getting-help:

Bug tracker
===========

If you have any suggestions, bug reports or annoyances please report them
to the issue tracker at http://github.com/ask/flakeplus/issues/

.. _wiki:

License
=======

This software is licensed under the `New BSD License`. See the ``LICENSE``
file in the top distribution directory for the full license text.

.. # vim: syntax=rst expandtab tabstop=4 shiftwidth=4 shiftround

