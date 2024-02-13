Vlasiator config reference
==========================

These can be viewed by running ``./vlasiator --help``.


Command line arguments
----------------------
.. code-block:: cfg

 Usage: main [options (options given on the command line override options given everywhere else)], where options are::
  --help                                                                       print this help message
  --version                                                                    print version information
  --global_config arg                                                          read options from the global configuration file arg (relative to the current 
                                                                               working directory). Options given in this file are overridden by options given 
                                                                               in the user's and run's configuration files and by options given in environment 
                                                                               variables (prefixed with MAIN_) and the command line
  --user_config arg                                                            read options from the user's configuration file arg (relative to the current 
                                                                               working directory). Options given in this file override options given in the 
                                                                               global configuration file. Options given in this file are overridden by options 
                                                                               given in the run's configuration file and by options given in environment 
                                                                               variables (prefixed with MAIN_) and the command line
  --run_config arg                                                             read options from the run's configuration file arg (relative to the current 
                                                                               working directory). Options given in this file override options given in the 
                                                                               user's and global configuration files. Options given in this override options 
                                                                               given in the user's and global configuration files. Options given in this file 
                                                                               are overridden by options given in environment variables (prefixed with MAIN_) 
                                                                               and the command line


Configuration file options
--------------------------

.. include:: help.txt