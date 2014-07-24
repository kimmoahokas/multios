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
    
2.  Ensure that you are using your new virtual env (run `which python`). 
    **Remember to do this step every time you work on this project!**

3.  Install required python libraries: `pip install -r requirements.txt`.

4.  Edit `credentials.json` to contain your own set of OpenStack credentials. 
    Also ensure that you are able to reach given OpenStack installation from your
    development machine.
    
## Running tests ##

The simplest and fastest way to run all the tests in this project is to 
change to src directory (`cd src`) and run 
`python -m unittest discover multios/tests`.

For more fine-grained control of tests to be executed consult the 
[documentation of Python Unit testing framework][unittest].

## License ##

TODO: decide license
 
 


[virtualenvwrapper]: http://virtualenvwrapper.readthedocs.org/en/latest/ "virtualenvwrapper"
[virtualenv]: https://virtualenv.pypa.io/en/latest/ "virtualenv"
[unittest]: https://docs.python.org/2/library/unittest.html "Python unittest"
