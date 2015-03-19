# MultiOS #

MultiOS is little integration tool designed to work with multiple OpenStack 
installations. The intention is to support automatic load balancing of 
arbitrary work loads between multiple independent OpenStack installations 
without modifications to OpenStack.

The tool was created as a part of SIGMONA research project at Aalto University 
School of Science, Department of Computer Science, Communication Networks
research group.

Copyright Kimmo Ahokas 2014.

## Getting started ##

1.  Create new Python 2.7 virtual environment for your project (Python 3.x is
    not supported). You do not want to mess with your system-wide python 
    installation.

    There are various ways for doing this, and the method does not really 
    matter. My personal favourite is [virtualenvwrapper][]. Other popular 
    choice is bare [virtualenv][].
    
    If you chose to use virtualenvwrapper, install it globally using `sudo 
    pip install virtualenvwrapper` and add the following to your shell 
    startup script (often `~/.bashrc`)
    
        export WORKON_HOME=$HOME/.virtualenvs
        export PROJECT_HOME=$HOME/Devel
        export VIRTUALENVWRAPPER_SCRIPT=/usr/local/bin/virtualenvwrapper.sh
        source /usr/local/bin/virtualenvwrapper_lazy.sh
        
    Then create new virtualenv: `mkvirtualenv multios`.
    
2.  Ensure that you are using your new virtual env (run `which python`). 
    **Remember to do this step every time you work on this project!**
    
    If you are using virtualenvwrpper you can activate the existing 
    virtualenv using command `workon multios`.

3.  Install required libraries: `sudo apt-get install libxml2-dev libxslt1-dev 
    python-dev`

4.  Install required python libraries and development tools:
    `pip install -r requirements.txt -r dev-requirements.txt`.

5.  Copy `sample_config.json` to `config.json` and edit it to contain your own
    set of OpenStack credentials. Also ensure that you are able to reach given
    OpenStack installation from your development machine.
    
## Running tests ##

The simplest and fastest way to run all the tests in this project is to 
change to source directory (`cd src`) and run 
`python -m unittest discover multios/tests`.

For more fine-grained control of tests to be executed consult the 
[documentation of Python Unit testing framework][unittest].

## Package management ##

For [obvious reasons][pinning] the package versions in this project are 
pinned. Top-level requirements and development requirements are 
declared in `requirements.txt.in` and `dev-requirements.txt.in` respectively 
and converted to "normal" `requirements.txt` and `dev-requirements.txt` using
[pip-tools][].

To update requirements run `pip-review --interactive` to update packages. 
Verify that everything works as expected with new package versions and then
run `pip-dump` to generate new `*-requirements.txt` files. Remember to commit
the changed files to git.

To add new packages to the project add the package name to
`requirements.txt.in` file and the pinned version to `requirements.txt`
and then use `pip-review` and `pip-dump` in similar way as when updating 
packages.

## Remarks about the code ##

The `MultiOSCLI` class in file `cli.py` uses Python [docopt][] module to parse 
command line arguments. Because of this it is **required** that the docstring
in the beginning of the class contains all the possible command line options,
commands and arguments in the standard POSIX notation. The argument parser is
constructed from the usage string automatically.

## License ##

TODO: decide license
 
 


[virtualenvwrapper]: http://virtualenvwrapper.readthedocs.org/en/latest/ "virtualenvwrapper"
[virtualenv]: https://virtualenv.pypa.io/en/latest/ "virtualenv"
[unittest]: https://docs.python.org/2/library/unittest.html "Python unittest"
[pinning]: http://nvie.com/posts/pin-your-packages/ "Pin Your Packages"
[pip-tools]: https://github.com/nvie/pip-tools "pip-tools"
[docopt]: https://github.com/docopt/docopt "Pythonic command line arguments parser, that will make you smile http://docopt.org"