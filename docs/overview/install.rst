Installing Therapist
====================

Installing Therapist is easily done using `pip`_. Assuming it is installed just
run the following from the command line:

    .. code-block:: bash

        # pip install therapist

This command will download the latest version of Therapist from the
`Python Package Index`_ and install it to your system. More information about
``pip`` and pypi can be found here:

* `install pip`_
* `pypi`_

Alternatively you can install from the distribution using the `setup.py`
script:

    .. code-block:: bash

        # python setup.py install

You could also install the `development version`_ by running the following:

    .. code-block:: bash

        # pip install therapist==dev

Or simple install from a clone of the `git repo`_:

    .. code-block:: bash

        # git clone https://github.com/rehandalal/therapist.git
        # mkvirtualenv therapist
        # pip install -r requirements.txt
        # pip install --editable .

.. _pip: https://github.com/pypa/pip
.. _Python Package Index: https://pypi.python.org/pypi/therapist
.. _install pip: https://pip.pypa.io/en/latest/installing.html
.. _pypi: https://pypi.python.org/pypi
.. _development version: https://github.com/rehandalal/therapist/tarball/master#egg=therapist-dev
.. _git repo: https://github.com/rehandalal/therapist/
