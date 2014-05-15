CrowdProcess API Client for Python
==================================

This is a client for `CrowdProcess <https://crowdprocess.com/>`__' `REST
API <https://crowdprocess.com/rest>`__.

Installing
----------

::

    pip install crowdprocess

or

::

    easy_install crowdprocess

Usage example
-------------

.. code:: python

    from crowdprocess import CrowdProcess
    crp = CrowdProcess('username', 'password')

    x2 = crp.job("function Run (d) { return d*2; }")
    print x2(range(5)) # outputs numbers 0, 2, 4, 6, 8, 10 in a random order

