How to configure Vlasiator for performance
==========================================

Why we teach this lesson
------------------------

Vlasiator requires a lot of resources to run, but thankfully it scales pretty well (super-linearly, even!). Good scaling requires, however, understanding of the system in use, and knowing how to profile and optimize the HPC environment from balancing threads vs tasks to parallel I/O. Here we introduce built-in Vlasiator profiling tools, rules-of-thumb for setting up the Slurm batch jobs, LUSTRE striping and ROMIO flags relevant to LUMI.


Intended learning outcomes
--------------------------

The user understands how to run Vlasiator, how to scale it and the options to affect scaling properties and can benchmark scaling.

Timing
------

Tue afternoon.

Preparing exercises
-------------------

Scaling exercise: few configurations to set up. Template file is decent, template jobscripts exist.

Running Vlasiator
-----------------

The recipe for a Vlasiator run. We use a benchmarking run for this exercise.

#. Folder to run the simulation. Use scratch for Lustre, our training project scratch is in ``/scratch/project_465000693/`` - make yourself a folder there with your username for your use.
#. ``vlasiator`` executable. 

  * These store versioning information, including git hashes and possible diffs. Probably a good idea to copy the executable to your run folder!

#. A Vlasiator configuration file. We will inspect our scaling test config soon, copy it from ``/scratch/project_465000693/example_runs/scaling/baseline/Flowthrough_amr.cfg``
#. Auxiliary input files for Vlasiator.

  * In this case, grab also the ``sw1.dat`` file from the above folder. This one defines inflow plasma parameters.
  * ``NRLMSIS.dat`` is another possibility, for an ionospheric profile for magnetospheric runs with an ionosphere.

#. A Slurm job script, for defining and requesting the HPC environment. Grab ``job-debug.sh`` from the above folder.

The Vlasiator Configuration file 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The configuration file uses the Boost program_options library. You can extract all available options by running ``./vlasiator --help``. There's plenty, so you may want to pipe that into a text file... but we have done that for you, see Vlasiator cfg reference!

Let's inspect the benchmark case config, here:

.. include:: shared_files/Flowthrough_amr.cfg


Lustre striping
---------------
Please refer to `LUMI docs <https://docs.lumi-supercomputer.eu/storage/parallel-filesystems/lustre/#file-striping>`_ for details.

Striping refers to spreading a file across several storage targets, and it is used to have better performance for parallel writes for large files. 

Rules of thumb: 

* Number tasks should be divisible by the number of stripes.
* Do not use more stripes than there are OSTs (for example, we use 20/32).
* Do not stripe small files: have one folder for restart files, and another for (each class of) bulk files.
* One stripe per ~5 GB of file size is what we have used for bulk files

``lfs getstripe <path>`` and ``lfs setstripe --count <n> <path>`` are the relevant commands.

Exercise:
^^^^^^^^^

#. Create a prototype run folder
#. Create a folder ``restart/``
#. Given an estimate of 1TB per restart file, set the striping of the ``restart/`` folder to a suitable values.
   #. ``lfs setstripe --count <n> <path>``
   #. ``lfs setstripe --stripe-size 16777216 <path>``
#. Create a folder ``bulks/``
#. Given an estimate of 20GB per bulk file, set the striping of ``bulks/`` to a suitable value.
#. Check the stripe counts for both folders with ``lfs getstripe``.

Next: how to communicate these to Vlasiator!

I/O config flags
----------------

Example from current large production run (5.5 TB restart files currently):

.. code-block:: cfg

  [io]
  diagnostic_write_interval = 10
  write_initial_state = 0
  restart_walltime_interval = 28400
  restart_write_path = restart
  number_of_restarts = 6 # = 8h / 28800s, change if modifying time limit or restart interval
  vlsv_buffer_size = 0
  restart_write_mpiio_hint_key = cb_buffer_size
  restart_write_mpiio_hint_value = 16777216
  restart_write_mpiio_hint_key = striping_unit
  restart_write_mpiio_hint_value = 16777216
  restart_write_mpiio_hint_key = romio_cb_write
  restart_write_mpiio_hint_value = disable
  restart_read_mpiio_hint_key = romio_ds_read
  restart_read_mpiio_hint_value = disable
  restart_read_mpiio_hint_key = romio_cb_read
  restart_read_mpiio_hint_value = disable
  write_restart_stripe_factor = 20

Let's check these in a bit more detail.

These set up restart file storing intervals and the path where to write, see next section:

.. code-block:: cfg

  restart_walltime_interval = 28400
  restart_write_path = restart
  number_of_restarts = 6 # = 8h / 28800s, change if modifying time limit or restart interval


These are hints for collective MPI I/O, in key-value pairs. 

.. code-block:: cfg

  restart_write_mpiio_hint_key = cb_buffer_size
  restart_write_mpiio_hint_value = 16777216
  restart_write_mpiio_hint_key = striping_unit
  restart_write_mpiio_hint_value = 16777216
  restart_write_mpiio_hint_key = romio_cb_write
  restart_write_mpiio_hint_value = disable
  restart_read_mpiio_hint_key = romio_ds_read
  restart_read_mpiio_hint_value = disable
  restart_read_mpiio_hint_key = romio_cb_read
  restart_read_mpiio_hint_value = disable

Notably, we are using here 16 MB buffers, matching the stripe unit.

The following informs Vlasiator of the restart file striping on Lustre (see below):

.. code-block:: cfg

  write_restart_stripe_factor = 20

Babysitting
===========

Writing restarts
^^^^^^^^^^^^^^^^

Vlasiator runs usually take a while to complete, and everything might not go as planned - node or interconnect failures come to mind. It is also easy to encounter edge cases where the plasma VDFs "hit the walls" of their velocity space, so prototyping and iteration of run configurations will come up.

We write restart files at given wall-clock time intervals, given in the config file, as already seen above:

.. code-block:: cfg

  restart_walltime_interval = 28400
  restart_write_path = restart
  number_of_restarts = 6 # = 8h / 28800s, change if modifying time limit or restart interval

Here we write a restart file each (a bit less than) 8 hours, to have a good coverage over a 48h slot. The last restart will be written at 47 hours 20 minutes, after which the run will finalize. This allows for a bit of a margin wrt. file system hiccups when writing - in case the file system is clogged at the time of the last write and it takes 30min to go through, we prefer to sacrifice a bit of the slot time for safety.

Restarting
^^^^^^^^^^

This is rather simple! To continue running from the last restart, one issues the ``--restart.filename`` program option at launch, either via the command line or by editing the config. Here, a snippet that finds and uses the last written restart file in the directory ``./restart/``:

.. code-block:: bash

  srun ./vlasiator --run_config Flowthrough_amr.cfg \
          --restart.filename $( ls restart/restart*vlsv | tail -n 1 )



Exercises
=========

Scaling test
------------

*Getting to know the basic run setup.*

We are going to be running a Flowthrough test to look a bit at weak scaling.

The test is a tube, with initial solar wind plasma flowing along the X direction. The inflow boundary injects faster, more dense solar wind into the domain, and the Y and Z directions are periodic. Dynamic AMR is applied to the simulation, tracking the interface between fast and slow flows.

To calculate weak scaling, we will expand the Y and Z dimensions of the domain with some factors, with a matching increase in cores. The shared sheet has some predetermined values, but feel free to experiment further (and add lines with notes).

Prototype: Magnetosphere3D
--------------------------

Prototype: Mercury5D
--------------------



``/pfs/lustrep2/scratch/project_465000693/example_runs/Mercury5D``

Other practical aspects
-----------------------



Interesting questions you might get
-----------------------------------



Typical pitfalls
----------------
