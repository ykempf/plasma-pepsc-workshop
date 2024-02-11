New project from template
=========================

Timing
------

Thursday, maybe.

Setting up a new project
------------------------

Set up a project folder
+++++++++++++++++++++++

First you need to create a subdirectory in the ``projects/`` directory. We will for this tutorial create the project ``MyPetProject``, by convention we use capitalized words. Do ``cd projects`` and ``mkdir MyPetProject``.

Set up the project code files
+++++++++++++++++++++++++++++

We need three files in ``projects/MyPetProject``, the code file ``MyPetProject.cpp``, its header file ``MyPetProject.h`` and a template/example configuration file used at runtime (waaaay later, not yet), ``MyPetProject.cfg``. The first two should be named like that for ease later in the coding process, the configuration file can have any name as that name is being passed as an option ``--run_config MyPetProject.cfg`` to the code at execution.

You can start with three empty files or copy them from a suitably similar existing project.

Code the project
++++++++++++++++

Base class
^^^^^^^^^^

Projects are classes in the ``projects`` namespace in Vlasiator. Individual projects are derived from the general ``Project`` class or from some special classes derived from that. The derived special classes are used to optimize the initialization of the velocity space by defining a different ``findBlocksToInitialize()`` function. This function gives a list of the velocity space blocks which will need to be initialized.

* In ``Project``, all blocks are returned. If you know that a significant fraction will be below the threshold and thus won't need to be initialized, this is not the good one to choose.
* In the derived class ``TriAxisSearch`` the project needs to define the function ``getV0()`` (see below). This is the origin of the Maxwellian population you want, the code then finds out how far around that point it needs to go to catch all velocity cells above the threshold. It is a major gain in efficiency and memory when you have a small Maxwellian in your velocity box, with respect to the default way of looping through the whole velocity space and discarding cells below threshold afterwards.

If none of the above suits your needs then you are welcome to code a new derived class to provide an efficient algorithm to select the blocks to initialize.

Basic structure
^^^^^^^^^^^^^^^

We present here the backbone of the project files.

MyPetProject.h
''''''''''''''

The basic backbone of the header file is

.. code-block:: c++

   #ifndef MYPETPROJECT_H
   #define MYPETPROJECT_H
   #include <stdlib.h>
   #include "../../definitions.h"
   #include "../project.h"
   namespace projects {
      class MyPetProject: public Project {
         public:
            MyPetProject();
            virtual ~MyPetProject();
            virtual bool initialize(void);
            static void addParameters(void);
            virtual void getParameters(void);
            virtual void calcCellParameters(Real* cellParams,creal& t);
            virtual Real calcPhaseSpaceDensity(
               creal& x, creal& y, creal& z,
               creal& dx, creal& dy, creal& dz,
               creal& vx, creal& vy, creal& vz,
               creal& dvx, creal& dvy, creal& dvz
            );
         protected:
            // (whatever you need)
      }; // class MyPetProject
   } // namespace
   #endif


MyPetProject.cpp
'''''''''''''''''

The basic backbone of the code file is (functions are explained below, not included here)

.. code-block:: c++

   #include <cstdlib>
   #include <iostream>
   #include <cmath>

   #include "../../common.h"
   #include "../../readparameters.h"
   #include "../../backgroundfield/backgroundfield.h"

   #include "MyPetProject.h"
   namespace projects {
      MyPetProject::MyPetProject(): Project() { }
      MyPetProject::~MyPetProject() { }
      // we do not use the constructor/destructor at the moment
      // your code, see functions below
   } // namespace projects


Functions
^^^^^^^^^

In the following we explain the functions you need in your project, i.e. the functions the code expects you to have in order to work. Not having them usually leads to an error message from the base project class informing you that you should use the function from the derived class (your project) and not the base class function. The constructors/destructors are not used at the moment.

MyPetProject::addParameters()
'''''''''''''''''''''''''''''

This is a static function because all ``addParameters()`` get called by the code to provide complete help. We use the Boost program options, thus to add a parameter use ``ReadParameters::add("MyPetProject.param", "This is the parameter for the MyPetProject project.", 0.0);``. The first is the option name, it can then be used as such in a command line, like ``--MyPetProject.param 1.0`` or in the configuration file as an entry of the form

.. code-block:: cfg
   [MyPetProject]
   param

but details on the configuration file come later. The last field is the default value in case the option is not set by the user. Make it a sensible value to avoid head-scratching and bug-hunting when a user wonders why your project does not work.

MyPetProject::getParameters()
'''''''''''''''''''''''''''''

This function is used to read in the parameters, it is used only if you actually use this project. The basic syntax is ``ReadParameters::get("MyPetProject.param", this->param);``, where we typically save the parameter's value into a member of the ``MyPetProject`` class. Of course it can be local to the function instead if it is not needed anywhere else, or you save it differently, as you wish.

MyPetProject::initialize()
''''''''''''''''''''''''''

This function can be used to set up things before any major computation is done, it is called early in the simulation initialization process. If nothing is needed, just ``return true;``.

MyPetProject::setCellBackgroundField()
''''''''''''''''''''''''''''''''''''''

Using the capabilities offered by the background field classes, you can set what you need here (constant or dipole at the moment). If you wish to do it by hand, make sure you also set all relevant derivative terms and not only the fields. Note that the background field is assumed to be curl-free, if it is not the calculations involving the current density in the Vlasov and field solvers are wrong.

MyPetProject::calcCellParameters()
''''''''''''''''''''''''''''''''''

This function is used to set the cell's (perturbed) magnetic field components. The electric field is computed self-consistently by the field solver.

MyPetProject::calcPhaseSpaceDensity()
'''''''''''''''''''''''''''''''''''''

This function is used to calculate the phase space density in each of the simulation cells in six dimensions. Typical examples are Maxwellians. Often one can code some form of averaging loops in that function and call one further function which has the actual distribution function calculation.

(TriAxisSearch) MyPetProject::getV0()
'''''''''''''''''''''''''''''''''''''

If you use the ``TriAxisSearch`` base class you have to provide this function. It must give the centre coordinate of the Maxwellian you want so that the ``findBlocksToInitialize()`` function can find out within what radius around this centre velocity blocks should be initialized.

Write a sensible default configuration file
+++++++++++++++++++++++++++++++++++++++++++

Once you coded your project and you know what parameters you will need, write a default configuration file to document workable and sensible options for your project. This file will be saved along in the repository for reference. Try to keep it up-to-date during the life of the project so that it still reflects a sensible state and not what you had in your crazy mind when you just made that file to comply with this paragraph. Otherwise you will incur the wrath of the next user trying to quickly run your project for a test and the pain of figuring out a new set of sensible parameters after failing to back up the configuration files you were actually using.

The only compulsory parameter in this file is the line

.. code-block:: cfg

   project = MyPetProject

otherwise Vlasiator will not run your project, no matter what.

A useful tool to check a cfg file is ``tools/check_vlasiator_cfg.sh``. It takes the ``vlasiator`` executable as a first argument and the cfg to check as second argument and returns a list of unused available options as well as a list of invalid options.


Integrate the project to Vlasiator
++++++++++++++++++++++++++++++++++

We decided that all projects should be compiled when compiling Vlasiator. This avoids hassle with the Makefile and it also helps to keep projects supported when coding new things related to the project class infrastructure (... or shuffled into the ``unsupported`` folder...). But this comes at the cost of adding some bits here and there. The file ``projects/project.cpp`` must be edited.

* Add ``#include "MyPetProject/MyPetProject.h"`` in the top section. Please use alphabetic ordering.
* Edit ``Project::addParameters()`` so that it also calls ``projects::MyPetProject::addParameters();``. You see, that's why it is static, we told you. Please use alphabetic ordering.
* If your project is so cool it created a new parameter that might be useful to other projects, add it to the ``Project_common`` category in this function and in ``Project::getParameters()``. If now you see that you need a parameter that actually was already available through the ``Project_common`` parameters, edit your code accordingly, no need to import twice the same stuff.
* In the function ``createProject()``, add
  
  .. code-block:: c++

     if(Parameters::projectName == "MyPetProject") {
        return new projects::MyPetProject;
     }

and yes, you guessed it, please use alphabetic ordering.

Set up the project compilation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You're almost there. Now the code is ready, it needs to be compiled. For that, obviously, the ``Makefile`` needs to be edited.

* ``DEPS_PROJECTS`` lists all project files, so add ``projects/MyPetProject/MyPetProject.h`` and ``projects/MyPetProject/MyPetProject.cpp``. Please use alphabetic ordering.
* ``OBJS`` should now include ``MyPetProject.o``. Please...
* Down in the actual making commands, add the relevant lines. Guess what order?

.. code-block: c++

   MyPetProject.o: ${DEPS_COMMON} projects/MyPetProject/MyPetProject.h projects/MyPetProject/MyPetProject.cpp
      ${CMP} ${CXXFLAGS} ${FLAGS} -c projects/MyPetProject/MyPetProject.cpp ${INC_DCCRG} ${INC_ZOLTAN} ${INC_BOOST} ${INC_EIGEN}

As a savvy ``Makefile`` guru you will remember that before ``${CMP}`` it is a tab character, not spaces.


("make", "debug")+
------------------

Now starts the actual work. In the base folder (where the ``Makefile`` is), use ``make`` to compile. If possible, use multiple processes to accelerate compilation by using ``make -j N`` where N is the number of concurrent compiling processes you want to use. It should be close to the number of physical cores available but not too much higher. In the unlikely event that the compilation should stop because it did not understand your code, debug, and iterate the above...

