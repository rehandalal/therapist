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
  include: "*.py"
  exclude:
    - "settings*.py"
    - "*migrations"
  run: flake8 {files}
eslint:
  descripton: ESLint
  run: eslint project_dir
build:
  description: Build the project
  run: ./build.sh
```

### Parameters

#####run
This is the actual command to be run. You can also include the `{files}` placeholder which will be replaced with a space separated list of files which have been modified.

#####description *(Optional)*
This is just a name or a brief description of what is happening in this command. If it is longer that 68 characters it will be truncated.

#####include *(Optional)*
Only files whose paths match these expressions will be passed through to the command.

#####exclude *(Optional)*
Files whose paths match these expressions will never be passed through to the command.

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
