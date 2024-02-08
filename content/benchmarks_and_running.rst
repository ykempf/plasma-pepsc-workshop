How to configure Vlasiator for performance
==========================================

Why we teach this lesson
------------------------

Vlasiator requires a lot of resources to run, but thankfully it scales pretty well (super-linearly!). Good scaling requires, however, understanding of the system in use, and knowing how to profile and optimize the HPC environment from balancing threads vs tasks to parallel I/O. Here we introduce built-in Vlasiator profiling tools, rules-of-thumb for setting up the Slurm batch jobs, LUSTRE striping and ROMIO flags relevant to LUMI.


Intended learning outcomes
--------------------------



Timing
------



Preparing exercises
-------------------


I/O config flags
----------------

Example from current production:

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

These set up restart file storign intervals
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


The following informs Vlasiator of the restart file striping on Lustre (see below):
.. code-block:: cfg

  write_restart_stripe_factor = 20


Lustre striping
---------------
Please refer to `LUMI docs <https://docs.lumi-supercomputer.eu/storage/parallel-filesystems/lustre/#file-striping>`_ for details.

Striping refers to spreading a file across several storage targets, and it is used to have better performance for parallel writes for large files. 

Rules of thumb: 


Other practical aspects
-----------------------



Interesting questions you might get
-----------------------------------



Typical pitfalls
----------------
