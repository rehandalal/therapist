[![Build Status](https://travis-ci.org/rehandalal/therapist.svg?branch=master)](https://travis-ci.org/rehandalal/therapist)

# Therapist
Work out your commitment issues. Smart pre-commit hook for git.


## Installation

Installing therapist is easy. Just run:

```
$ pip install therapist
```

You could also install the development version 
(https://github.com/rehandalal/therapist/tarball/master#egg=therapist-dev):

```
$ pip install therapist==dev
```

or

```
$ git clone https://github.com/rehandalal/therapist.git
$ mkvirtualenv therapist
$ pip install -r requirements.txt
$ pip install --editable .
```

## Installing the hook

To install the pre-commit hook:

```
$ therapist install
```

## Configuration

In the root folder of your repo, create a file called `therapist.yml`. Here is a sample of what it might look like:

```yml
flake8:
  description: Flake8
  run: flake8 project_dir
eslint:
  descripton: ESLint
  run: eslint project_dir
build:
  description: Build the project
  run: ./build.sh
```

## Uninstalling the hook

If you decide you no longer want to have the hook installed, simply run:

```
$ therapist uninstall
```

## Run the tests

To run the tests from a tarball or git clone:

```
$ python setup.py test
```
