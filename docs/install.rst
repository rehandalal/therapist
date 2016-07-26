Installation
============

Install the tool
----------------

The first thing you need to do is to install therapist.

Using pip:

    .. code-block:: bash

        pip install therapist

You could also install the `development version`_:

    .. code-block:: bash

        pip install therapist==dev

Or:

    .. code-block:: bash

        git clone https://github.com/rehandalal/therapist.git
        mkvirtualenv therapist
        pip install -r requirements.txt
        pip install --editable .


.. _development version: https://github.com/rehandalal/therapist/tarball/master#egg=therapist-dev


Install the hook
----------------

To install the pre-commit hook you only have to run:

    .. code-block:: bash

        therapist install
