.. _installing-vlasiator:

Installing Vlasiator
====================

Why we teach this lesson
------------------------
Vlasiator is hosted on GitHub and is open source, but it is, still, a specialist code under development. Here we show how to obtain the up-to-date stable Vlasiator version with the requisite libraries, and go through what the libraries are and what are they used for.


Intended learning outcomes
--------------------------
You can install a correct version of Vlasiator, required libraries and build everything.


Timing
------

Tuesday pre-lunch.

How to install Vlasiator
------------------------
Installing Vlasiator is easy and straightforward!

Tasks:

#. Clone Vlasiator *with submodule support*
#. Build libraries 
#. Make new makefile for your machine in MAKE folder
#. Compile!

Here are some general steps. More machine-specific details may be detailed on one of the following pages:

Cloning Vlasiator
^^^^^^^^^^^^^^^^^

We are transferring to use ``git submodules`` for the dependent libraries. So far, some of the header libraries have been moved to this framework, and some need to be installed manually (see above).

Use the ``--recurse-submodules`` when cloning, pulling, or checking out branches:

.. code-block:: bash

    git clone --recurse-submodules https://github.com/fmihpc/Vlasiator
    git checkout master --recurse-submodules
    git submodule update --init --recursive

Task: create a folder with your username under ``/projappl/project_465000693``, ``cd`` into it and clone Vlasiator master branch into it.

Vlasiator main branches
+++++++++++++++++++++++

* ``master``: Main branch, stable, lagging behind from development branch. Main releases.
* ``dev``: Latest features, but potentially not stable.

... plus a plethora of topic branches.

Building libraries
------------------

Vlasiator needs a number of libraries, a part of which need to be built. Some header libraries have been transferred to submodules, and those are automatically fetched with git (... when ``--recurse-submodules`` is used correctly!).

When building libraries and the code, we want to stick to a particular toolchain of compilers and MPI libraries, etc. On LUMI, we use the following modules:

.. code-block:: bash
  
  module load LUMI/22.08
  module load cpeGNU
  module load papi
  module load Eigen
  module load Boost/1.79.0-cpeGNU-22.08

Each cluster and supercomputer will have different modules available. If the prerequisite libraries are not available as modules, they need to be downloaded and built by the user. On debian-based system (such as ubuntu and cubbli), some of the dependencies are provided as packages, installable via ``apt-get install libeigen3-dev libboost-dev libboost-program-options-dev libopenmpi-dev``. Use of the `boost-latest ppa <https://launchpad.net/~boost-latest/+archive/ppa>`_ is recommended on Ubuntu.

Building the prerequisite libraries of Vlasiator can be done with the following script, included in the Vlasiator repository: `build_libraries.sh <https://github.com/fmihpc/vlasiator/blob/master/build_libraries.sh>`_. Our usual practice is to use a centralized library folder, but we'll set up one for each user as an exercise.

Tasks:

#. copy ``build_libraries.sh`` from Vlasiator root to ``projappl/project_465000693/<user>``.
#. load the above toolchain with the module load commands.
#. Build the libraries with a descriptive name for the toolchain: ``./build_libraries.sh LUMI-22.08-GNU-PEPSC``
#. Find the built libraries then under ``libraries-LUMI-22.08-GNU-PEPSC/``. We'll use this path for our Makefile.

That's done! Below, the libraries used for reference.

Library reference
^^^^^^^^^^^^^^^^^

Require building
++++++++++++++++

* `Zoltan <http://www.cs.sandia.gov/zoltan/>`_ (`install instructions <https://github.com/fmihpc/Vlasiator/wiki/Installing-Vlasiator#zoltan>`__)
  
  * Load balancing library.
* `Boost <http://www.boost.org/>`_ (`install instructions <https://github.com/fmihpc/Vlasiator/wiki/Installing-Vlasiator#boost>`__)

  * Configuration parser.
* `Eigen <http://eigen.tuxfamily.org/index.php?title=Main_Page>`_ (`install instructions <https://github.com/fmihpc/Vlasiator/wiki/Installing-Vlasiator#eigen>`__)

  * Linear algebra

* `Phiprof <https://github.com/fmihpc/phiprof>`_ (`install instructions <https://github.com/fmihpc/Vlasiator/wiki/Installing-Vlasiator#phiprof>`__)

  * Lightweight profiling. 
* `VLSV <https://github.com/fmihpc/vlsv>`_ (`install instructions <https://github.com/fmihpc/Vlasiator/wiki/Installing-Vlasiator#vlsv>`__)

  * Custom file format library, with parallel MPI I/O support.
  * NB: Contains the buildable VLSV plugin for VisIt.
* MPI
* C++17 compiler with OpenMP >=3 support

Header libraries fetched via submodules
+++++++++++++++++++++++++++++++++++++++

These libraries are handled via ``git submodules`` (nb. clone/pull instructions for submodules below), you do not need to install these separately.

* `DCCRG <https://github.com/fmihpc/dccrg>`_ (`install instructions <https://github.com/fmihpc/Vlasiator/wiki/Installing-Vlasiator#dccrg>`__)
 
  * Generic MPI grid library used for the Vlasov solver grid with AMR.
  * DCCRG has its own prerequisites (MPI 2, Zoltan, and Boost). See the linked install instructions for required libraries!

* `FsGrid <https://github.com/fmihpc/fsgrid>`_ (`install instructions <https://github.com/fmihpc/Vlasiator/wiki/Installing-Vlasiator#fsgrid>`__)

  * Lightweight parallel grid library used for the uniform field solver grid.

* `Vectorclass <http://www.agner.org/optimize/#vectorclass>`_ (`install instructions <https://github.com/fmihpc/Vlasiator/wiki/Installing-Vlasiator#vectorclass>`__)

  * SIMD support
  * See instructions for the required addon library if installing manually.


Optional libraries
++++++++++++++++++

And also a number of optional but useful libraries

* `Jemalloc <www.canonware.com/jemalloc/download.html>`_ (`install instructions <https://github.com/fmihpc/Vlasiator/wiki/Installing-Vlasiator#jemalloc>`__)

  * Memory allocator with reduced memory fragmentation (recommended for performance)

* `Papi <http://icl.cs.utk.edu/papi/>`_ (`install instructions <https://github.com/fmihpc/Vlasiator/wiki/Installing-Vlasiator#papi>`__)

  * Memory measurement, module often available on-site
 
Make a new makefile
^^^^^^^^^^^^^^^^^^^

The main makefile is in the vlasiator main folder. There should be no need to modify that. All settings are in a separate machine specific file that is in the MAKE folder, where compiler names, compiler flags and library locations are set. In the MAKE folder there are several examples from various machines. The file name is ``Makefile.machine_name``, where machine_name is whatever you want to call your machine. It is best to start from a makefile that is similar to the machine you are compiling on. The Makefile.home corresponds to a Linux computer with all libraries in ``${HOME}/lib`` and ``${HOME}/include``.

We'll do a new Makefile based on `a template <shared_files/Makefile.lumi-template>`_.

Firstly, note that mark, as comments, the module toolchain that we use with this Makefile:

.. code-block:: makefile

  # Modules loaded
  # module load LUMI/22.08 ; module load cpeGNU ; module load papi; module load Eigen; module load Boost/1.79.0-cpeGNU-22.08

These will need to be loaded while compiling and running, and need to match your library toolchain.

Find the LIBRARY_PREFIX variables and modify them to match your library paths:

.. code-block:: makefile
  
  LIBRARY_PREFIX = <library-dir/lib>
  LIBRARY_PREFIX_HEADERS = <library-dir/include>

This is enough! But note how these are used later, for example:

.. code-block:: make

  INC_ZOLTAN = -isystem$(LIBRARY_PREFIX_HEADERS)
  LIB_ZOLTAN = -L$(LIBRARY_PREFIX) -lzoltan -Wl,-rpath=$(LIBRARY_PREFIX)

If you wish, you can choose to point to different libraries via modifying these paths.

Compile!
^^^^^^^^

After one has created the makefile, one should set an environment variable with the name of your machine, matching the name used for the MAKE/Makefile.machine_name file. For example, to use the home makefile one can set it like this:

.. code-block:: bash

    export VLASIATOR_ARCH=home

To make the environment variable one can put it into the initialization files for your shell, e.g. .profile. or .bashrc.

After ensuring all libraries and compile options are made available for Vlasiator, and the correct machine-specific makefile has been set, one can simply

.. code-block:: bash

    make clean
    make -j 12

to make Vlasiator, or

.. code-block:: bash

    make clean 
    make -j 12 tools

to make the Vlasiator tools.

Note: The -j flag tells GNU Make to build the program in parallel on several threads. If you are building on a smaller computer, it is not recommended to have a -j count greater than the number of available cores on the frontend where you are compiling. This will not impact how many threads the actual simulation will run on.

Detailed installation instructions for Libraries
------------------------------------------------

If the install script or fetching submodules fails, you can review the more in-depth guidelines available at https://github.com/fmihpc/vlasiator/wiki/Installing-Vlasiator though it should not be necessary for the purposes of this tutorial.

Other practical aspects
-----------------------



Interesting questions you might get
-----------------------------------



Typical pitfalls
----------------

Some wise words of the pitfalls of submodules and git commands:
So trying with a fresh clone with **no** ``--recurse-submodules``, this gets the correct vlasiator-version target for dccrg:

``git checkout dev``
``git pull origin dev --recurse-submodules``

This works as well

``git checkout dev --recurse-submodules``
``git submodule update --init --recursive``

This however does not fetch the correct submodule commits:

``git checkout dev``

This does not fetch submodules by itself:

``git checkout dev --recurse-submodules``

but it needs then

``git submodule update --init --recursive``

But,

``git checkout dev``
``git submodule update --init --recursive``

is bad, since that will get the default master branch tip as the submodule commits and then updates the submodules to those ones. But then, if you start with

``git clone --recurse-submodules https://github.com/fmihpc/vlasiator``

you can do

``git checkout dev``
``git submodule update --init --recursive``

