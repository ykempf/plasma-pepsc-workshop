Preparations for the workshop
=============================

#. Watch the `introductory lectures<https://datacloud.helsinki.fi/index.php/s/wEZdF3szjBfapSs>`_ about Vlasiator.
#. Install locally `VisIt 3.3.3 <https://visit-dav.github.io/visit-website/releases-as-tables/>`_
#. Get LUMI access (information provided via ENCCS)
#. Clone Vlasiator and its prerequisite libraries on LUMI (see below)
#. Clone Analysator onto your LUMI workspace



Cloning Vlasiator
-----------------

git clone --recurse-submodules https://github.com/fmihpc/vlasiator
git submodule update --init --recursive

Vlasiator libraries
-------------------

*These start to go into workshop material, but might be a good exercise to go as far as one wishes*

Select toolchain/module environment, make note

Run ``build_libraries.sh`` to get and build libraries, note path

Adapting a Makefile
-------------------

...

Compiling Vlasiator
-------------------

...

