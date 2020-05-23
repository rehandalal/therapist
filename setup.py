"""
A lint suite runner with Git-aware capabilities and a smart pre-commit hook.

Full documentation for this tool is available at:
http://therapist.readthedocs.io/
"""
import os
import sys

from setuptools import find_packages, setup
from setuptools.command.install import install


ROOT = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(ROOT, "requirements.txt"), "r") as f:
    DEPENDENCIES = f.read().splitlines()
    print(DEPENDENCIES)

version = __import__("therapist").__version__


class VerifyVersionCommand(install):
    """Custom command to verify that the git tag matches our version"""

    description = "verify that the git tag matches our version"

    def run(self):
        tag = os.getenv("CIRCLE_TAG")

        if tag != "v{}".format(version):
            info = "Git tag: {0} does not match the version of this app: {1}".format(tag, version)
            sys.exit(info)


setup(
    name="therapist",
    version=version,
    url="https://github.com/rehandalal/therapist",
    license="Mozilla Public License Version 2.0",
    author="Rehan Dalal",
    author_email="rehan@meet-rehan.com",
    description="A lint suite runner with Git-aware capabilities and a smart pre-commit hook.",
    long_description=__doc__,
    packages=find_packages(exclude=["tests", "docs"]),
    include_package_data=True,
    zip_safe=False,
    platforms="any",
    install_requires=DEPENDENCIES,
    py_modules=["therapist"],
    entry_points={"console_scripts": ["therapist = therapist.cli:cli"]},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Natural Language :: English",
        "Operating System :: MacOS",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
    ],
    cmdclass={"verify": VerifyVersionCommand},
)
