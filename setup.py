"""
Smart pre-commit hook for git.
"""
import os
import re

from setuptools import find_packages, setup


DEPENDENCIES = ['click', 'pathspec', 'PyYAML', 'six']
ROOT = os.path.abspath(os.path.dirname(__file__))


def get_version():
    versionfile = os.path.join(ROOT, 'therapist', '_version.py')
    verstrline = open(versionfile, 'rt').read()
    mo = re.search(r"""^__version__ = ['"]([^'"]*)['"]""", verstrline, re.M)
    if mo:
        return mo.group(1)
    else:
        raise RuntimeError('Unable to find version string in {0}.'.format(versionfile))

setup(
    name='therapist',
    version=get_version(),
    url='https://github.com/rehandalal/therapist',
    license='Mozilla Public License Version 2.0',
    author='Rehan Dalal',
    author_email='rehan@meet-rehan.com',
    description='A smart pre-commit hook for git.',
    long_description=__doc__,
    packages=find_packages(exclude=['tests', 'docs']),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=DEPENDENCIES,
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    py_modules=['therapist'],
    entry_points={
        'console_scripts': [
            'therapist = therapist.cli:cli',
        ],
    },
    classifiers=[
        # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
