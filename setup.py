"""
A smart pre-commit hook for git.
"""
import os

from setuptools import find_packages, setup


DEPENDENCIES = [
    'click >= 6.7',
    'colorama >= 0.3.7',
    'pathspec >= 0.5.0',
    'PyYAML >= 3.12',
    'six >= 1.10.0',
]

ROOT = os.path.abspath(os.path.dirname(__file__))

version = __import__('therapist').__version__


setup(
    name='therapist',
    version=version,
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
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
    ]
)
