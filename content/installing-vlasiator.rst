Installing Vlasiator
==================

Why we teach this lesson
------------------------
Vlasiator is hosted on GitHub and is open source, but it is, still, a specialist code under development. Here we show how to obtain the up-to-date stable Vlasiator version with the requisite libraries.


Intended learning outcomes
--------------------------
You can install a correct version of Vlasiator.


Timing
------

Pre-material.

How to install Vlasiator
------------------------
Installing Vlasiator is easy and straightforward!

These steps should be taken:
 * Install libraries 
 * Clone Vlasiator *with submodule support*
 * Make new makefile for your machine in MAKE folder
 * Compile!

Here are some general steps. More machine-specific details may be detailed on one of the following pages:

Install libraries
^^^^^^^^^^^^^^^^^

Vlasiator needs a number of libraries:
 * `Zoltan <http://www.cs.sandia.gov/zoltan/>`_ (`install instructions <https://github.com/fmihpc/vlasiator/wiki/Installing-Vlasiator#zoltan>`__)
 * `Boost <http://www.boost.org/>`_ (`install instructions <https://github.com/fmihpc/vlasiator/wiki/Installing-Vlasiator#boost>`__)
 * `Eigen <http://eigen.tuxfamily.org/index.php?title=Main_Page>`_ (`install instructions <https://github.com/fmihpc/vlasiator/wiki/Installing-Vlasiator#eigen>`__)
 * `Vectorclass <http://www.agner.org/optimize/#vectorclass>`_ (`install instructions <https://github.com/fmihpc/vlasiator/wiki/Installing-Vlasiator#vectorclass>`__)
 * `Phiprof <https://github.com/fmihpc/phiprof>`_ (`install instructions <https://github.com/fmihpc/vlasiator/wiki/Installing-Vlasiator#phiprof>`__)
 * `VLSV <https://github.com/fmihpc/vlsv>`_ (`install instructions <https://github.com/fmihpc/vlasiator/wiki/Installing-Vlasiator#vlsv>`__)
 * MPI
 * C++11 compiler with OpenMP >=3 support
These libraries are handled via ``git submodules`` (nb. clone/pull instructions for submodules below), you do not need to install these separately.
 * `DCCRG <https://github.com/fmihpc/dccrg>`_ (`install instructions <https://github.com/fmihpc/vlasiator/wiki/Installing-Vlasiator#dccrg>`__)
  
  * See the linked install instructions for required libraries!
 
 * `FsGrid <https://github.com/fmihpc/fsgrid>`_ (`install instructions <https://github.com/fmihpc/vlasiator/wiki/Installing-Vlasiator#fsgrid>`__)

And also a number of optional but useful libraries
 * `Jemalloc <www.canonware.com/jemalloc/download.html>`_ Memory allocator with reduced memory fragmentation (`install instructions <https://github.com/fmihpc/vlasiator/wiki/Installing-Vlasiator#jemalloc>`__)
 * `Papi <http://icl.cs.utk.edu/papi/>`_ Memory measurement, module often available (`install instructions <https://github.com/fmihpc/vlasiator/wiki/Installing-Vlasiator#papi>`__)
 
On debian-based system (such as ubuntu and cubbli), some of the dependencies are provided as packages, installable via ``apt-get install libeigen3-dev libboost-dev libboost-program-options-dev libopenmpi-dev``

use of the `boost-latest ppa <https://launchpad.net/~boost-latest/+archive/ppa>`_ is recommended on Ubuntu.

See detailed library installation instructions at the end of this page.

Clone Vlasiator
^^^^^^^^^^^^^^^

We are transferring to use ``git submodules`` for the dependent libraries. So far, some of the header libraries have been moved to this framework, and some need to be installed manually (see above).

Use the ``--recurse-submodules`` when cloning, pulling, or checking out branches.

.. code-block:: bash

    git clone --recurse-submodules https://github.com/fmihpc/vlasiator
    git checkout <branch> --recurse-submodules
    git submodule update --init --recursive



Make new makefile
^^^^^^^^^^^^^^^^^

The main makefile is in the vlasiator main folder. There should be no need to modify that. All settings are in a separate machine specific file that is in the MAKE folder, where compiler names, compiler flags and library locations are set. In the MAKE folder there are several examples from various machines. The file name is Makefile.machine_name, where machine_name is whatever you want to call your machine. It is best to start from a makefile that is similar to the machine you are compiling on. The Makefile.home corresponds to a Linux computer with all libraries in ``${HOME}/lib`` and ``${HOME}/include``.

Compile!
^^^^^^^^

After one has created the makefile, one should set an environment variable with the name of your machine, matching the name used for the MAKE/Makefile.machine_name file. For example, to use the home makefile one can set it like this:

.. code-block:: bash

    export VLASIATOR_ARCH=home

To make the environment variable one can put it into the initialization files for your shell, e.g. .profile.

Then one can simply

.. code-block:: bash

    make clean
    make -j 12

to make vlasiator, or

.. code-block:: bash

    make clean 
    make -j 12 tools

to make the Vlasiator tools.

Detailed installation instructions for Libraries
------------------------------------------------

DCCRG
^^^^^

DCCRG is a pure header library so one needs to fetch it and make sure it is included (see Makefile.your-arch).

.. code-block:: bash

    git clone git@github.com:fmihpc/dccrg.git

If the ssh clone fails, use the https protocol.

.. code-block:: bash

    https://github.com/fmihpc/dccrg.git

DCCRG needs a few libraries, the instructions for installing them are on this page. Further instructions can also be found in dccrg wiki: https://github.com/fmihpc/dccrg/wiki

Currently Vlasiator uses not the master branch of DCCRG, instead the ``vlasiator-version`` branch. This is handled by submodules.

Boost
^^^^^

Boost (http://www.boost.org/) provides Vlasiator (and DCCRG) with some datastructures that are not in the pre C++11 standard. We also use the `program options <http://www.boost.org/doc/libs/1_55_0/doc/html/program_options.html>`_ module for reading cfg parameters (with some wrapper functions).


Debian-based systems
++++++++++++++++++++

On debian-based system (such as ubuntu and cubbli) boost is installable via 
``apt-get install libboost-dev libboost-program-options-dev``
Use of the boost-latest ppa (https://launchpad.net/~boost-latest/+archive/ppa) ppa is reccomended on ubuntu.

Cray XC platform
++++++++++++++++
One can use the Trilinos module:

.. code-block:: bash

    module load cray-trilinos


And add to Makefile.your-arch:

.. code-block:: bash

    INC_BOOST = -I$(CRAY_TRILINOS_PREFIX_DIR)/include/boost
    INC_BOOST = -L$(CRAY_TRILINOS_PREFIX_DIR)/lib -lboost_program_options


Other platforms
+++++++++++++++

On other platforms you can follow the instructions on DCCRG's wiki.(https://github.com/fmihpc/dccrg/wiki/Install). Boost is mostly a header library, so we only need to compile the program options module.

Summary:

.. code-block:: bash

    wget http://freefr.dl.sourceforge.net/project/boost/boost/1.72.0/boost_1_72_0.tar.bz2
    tar xf boost_1_72_0.tar.bz2
    cd boost_1_72_0
    ./bootstrap.sh --with-libraries=program_options
    echo "using mpi ;" >> ./tools/build/src/user-config.jam
    ./b2
    ./b2 --prefix=<path> install
    cd ..
    rm -r boost_1_72_0

Note that it detects ``gcc`` (too) efficiently at least on Mahti, so you might need to add ``--with-toolset=intel-linux`` to the ``bootstrap`` command.



Zoltan
^^^^^^

This library is used for load balancing.

Generic installation (add prefix path and replace cc and CC with the correct MPI wrappers):

.. code-block:: bash

    git clone git@github.com:sandialabs/Zoltan.git
    mkdir zoltan-build
    cd zoltan-build
    ../Zoltan/configure --prefix=<path> --enable-mpi --with-gnumake --with-id-type=ullong CC=cc CXX=CC
    make -j 8
    make install


Others
++++++
You can follow the installation instructions on DCCRG's wiki.(https://github.com/fmihpc/dccrg/wiki/Install).

Vectorclass
^^^^^^^^^^^
Download Vectorclass library from: http://www.agner.org/optimize/
Watch out: version 2 of this library uses advanced metaprogramming tricks that do not seem to sit well with compilers in common HPC environments. For the time being, it is recommended to use version 1 from here: https://github.com/vectorclass/version1

We use this to vectorize Vlasov propagation with SSE2/AVX. It is a header library so the header files only need to be placed in a include folder.

Additionally, ``vector3d.h`` needs to be copied from a now separate repo:

.. code-block:: bash

    git clone git@github.com:vectorclass/add-on.git
    cp add-on/vector3d/vector3d.h <PATH TO VECTORCLASS>

into the directory where the remaining vector class headers are lying.

phiprof
^^^^^^^
Clone the latest version from: https://github.com/fmihpc/phiprof/ 

Used for runtime performance tracking.

In the src folder there is a simple Makefile. Edit that to support you machine and make.- The library will then be in the phiprof include and lib folders.

vlsv
^^^^
Download from https://github.com/fmihpc/vlsv.

This is the file format/io library.

Installation instructions:
 * Create a Makefile.machine_name file based on the existing ones
 * Change ARCH at the top of the Makefile to you new Makefile.ARCH
 * make

VLSV plugin for VisIt
^^^^^^^^^^^^^^^^^^^^^
- Install VisIt or use a pre-installed version for the machine you target.
- Ask around if someone has the plugin compiled already on that machine. If yes, copy their ``$HOME/.visit/<version>/<arch>/plugins/databases/*Vlsv*`` into the same path in your home directory.

If you want/have to build yourself:

- Build VLSV as above first.
- Then ``cd visit-plugin``.
- Edit ``vlsv.xml`` so that it points to your vlsv directory where you just built vlsv. You can use ``xmledit`` for that, which you can find in the visit installation directory in the ``bin`` for the version and architecture you are using, e.g. ``$HOME/visit/3.0.2/linux-x86_64/bin/``.
- Locate ``xml2cmake`` in the same location, and run that ``xml2cmake -clobber vlsv.xml``.
- Run ``cmake CMakeLists.txt``.
- Run ``make`` to build and install, ``make -j 4`` makes it faster but it won't work well with a lot more than 4.

Note: As of Nov. 2020 it will complain about a VTK API function. You can checkout the version from https://github.com/fmihpc/vlsv/pull/41  until this is merged, or you can comment out the offending lines when building.
- NB for the pending update version, CXXFLAGS in vlsv.xml are also updated with ``-DNEW_VTK_API`` replaced with ``-DVTK_API=81`` (corresponds to VTK API for Mahti VisIt, 3.1). For fresh VisIt versions, the included flag should be good.

fsgrid
^^^^^^
Download from https://github.com/fmihpc/fsgrid.

This is the mesh library for cartesian domain decomposition of the fieldsolver.
It is a header-only library, and the only thing required for vlasiator is that the fsgrid.hpp file is available in its include path.

papi
^^^^
Download from http://icl.cs.utk.edu/papi/

Papi is optional, and only needed if ``CXXFLAGS += -DPAPI_MEM`` is defined in the makefile. It can provide information on the actual memory usage of Vlasiator. Most of the time papi is pre-installed on supercomputers and clusters and can often be loaded with `module load papi`.

If not, it can most of the time be compiled with the typical method:

.. code-block:: bash

    git clone https://github.com/icl-utk-edu/papi.git
    cd papi/src
    ./configure --prefix=${HOME}/libraries/papi
    make
    make install


jemalloc
^^^^^^^^
Download from http://www.canonware.com/jemalloc/download.html

jemalloc is an optional replacement for the normal malloc/free routines. It is optimized for minimizing memory fragmentation, and it can be of tremendous importance and is strongly recommended, see #25 

Current testing indicates that jemalloc should be compiled with support for transparent huge pages disabled. To perform this, add the flag --disable-thp during configuration.

To compile one would typically do something like this (replace prefix path with the correct one, and update version if there is a newer one)

.. code-block:: bash

    wget -O jemalloc-4.0.4.tar.bz2 https://github.com/jemalloc/jemalloc/releases/download/4.0.4/jemalloc-4.0.4.tar.bz2
    tar xf jemalloc-4.0.4.tar.bz2
    cd jemalloc-4.0.4
    ./configure --prefix=${HOME}/libraries/jemalloc --with-jemalloc-prefix=je_
    make
    make install


Eigen
^^^^^
Download from http://eigen.tuxfamily.org/index.php?title=Main_Page. One does not need to compile anything, it is enough to copy the Eigen sub-folder. Replace in the following instructions the version and paths:

.. code-block:: bash

    wget https://gitlab.com/libeigen/eigen/-/archive/3.2.8/eigen-3.2.8.tar.bz2
    tar -xvf eigen-3.2.8.tar.bz2
    cp -r eigen-3.2.8/Eigen $HOME/libraries/eigen


NOTE: Eigen 3.3.8 has an "'eigen_assert_exception' is not a member of 'Eigen'" bug during compilation. Do not use this specific version.



Other practical aspects
-----------------------



Interesting questions you might get
-----------------------------------



Typical pitfalls
----------------
