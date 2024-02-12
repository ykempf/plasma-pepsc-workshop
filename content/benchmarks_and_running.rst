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

.. code-block:: bash

  #!/bin/bash -l
  #SBATCH --job-name=PEPSC-demo-debug
  #SBATCH --partition=debug
  #SBATCH --nodes=2
  #SBATCH --mem=0
  #SBATCH --ntasks-per-node=16
  #SBATCH --cpus-per-task=8
  #SBATCH --time=0:30:00
  #SBATCH --account=project_465000693
  ##SBATCH --hint=multithread
  #SBATCH --exclusive # enforced on >=standard partitions, not on small
  ##SBATCH --dependency=singleton # useful for restarting

  date

  export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
  #export OMP_PLACES=cores
  #export OMP_PROC_BIND=spread
  export SRUN_CPUS_PER_TASK=$SLURM_CPUS_PER_TASK

  export TASKS_PER_NODE=$(( 128 / $SLURM_CPUS_PER_TASK ))
  echo "We use "${TASKS_PER_NODE}" tasks per node"

  # https://docs.olcf.ornl.gov/systems/crusher_quick_start_guide.html
  export MPICH_SMP_SINGLE_COPY_MODE=NONE

  ulimit -c unlimited
  export PHIPROF_PRINTS=detailed
  umask 007

  module --force purge
  module load LUMI/22.08
  module load cpeGNU
  module load craype-x86-milan
  module load papi
  module load Boost
  module load Eigen

  module list

  cd $SLURM_SUBMIT_DIR

  squeue --job $SLURM_JOB_ID -l

  sleep 5

  srun ./vlasiator --version

  sleep 5

  srun ./vlasiator --run_config Flowthrough_amr.cfg \
          #--restart.filename $( ls restart/restart*vlsv | tail -n 1 )



The Vlasiator Configuration file 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The configuration file uses the Boost program_options library. You can extract all available options by running ``./vlasiator --help``. There's plenty, so you may want to pipe that into a text file... but we have done that for you, see the Vlasiator cfg reference!

Let's inspect the benchmark case config, here:

.. code-block:: cfg
  
  # The root options describe toplevel solver properties and populations
  ParticlePopulations = proton
  
  project = Flowthrough
  propagate_field = 1
  propagate_vlasov_acceleration = 1
  propagate_vlasov_translation = 1
  dynamic_timestep = 1
  
  # <population>_properties, multiple populations are supported!
  [proton_properties]
  mass = 1
  mass_units = PROTON
  charge = 1
  
  # Adaptive Mesh Refinement - new development!
  [AMR]
  max_spatial_level = 2             # Maximum number of refinements
  max_allowed_spatial_level = 2     # *Currently* allowed number of refinements
                                    # - can be increased after restarts, gradually!
  adapt_refinement = 1

  # tuning parameters
  use_alpha1 = 1
  alpha1_coarsen_threshold = 0.1
  alpha1_refine_threshold = 0.4
  use_alpha2 = 1
  alpha2_refine_threshold = 1

  # Cadence and safeties
  refine_on_restart = 0
  refine_cadence = 4            # refinement cadence is in units of load balances
  refine_after = 50.0           # First adapt after 50s from start of run
  refine_radius = 7320e6        # We do not want to refine outer boundary cells
  
  # Spatial grid parameters - coarsest level grid.
  [gridbuilder]
  x_length = 48
  y_length = 12
  z_length = 12
  x_min = -16e7
  x_max = 16e7
  y_min = -4e7
  y_max = 4e7
  z_min = -4e7
  z_max = 4e7
  t_max = 400.0
  dt = 2.0
  
  # <population>_vspace - velocity grid definitions per population
  [proton_vspace]
  vx_min = -1.92e6
  vx_max = +1.92e6
  vy_min = -1.92e6
  vy_max = +1.92e6
  vz_min = -1.92e6
  vz_max = +1.92e6
  # vi_length are in units of block width (4, so far)
  # - these define 64x64x64 velocity-space cells over +-1.92e6 m/s.
  # -> dv = 61.250 km/s for this case
  vx_length = 16
  vy_length = 16
  vz_length = 16
  
  [io]
  diagnostic_write_interval = 1
  write_initial_state = 0
  
  # Reduced data writeouts
  system_write_t_interval = 10.0
  system_write_file_name = bulk

  # These set up strides for saving VDF data in the reduced data readouts
  system_write_distribution_stride = 0
  system_write_distribution_xline_stride = 0
  system_write_distribution_yline_stride = 0
  system_write_distribution_zline_stride = 0
  
  # Reduced data outputs
  [variables]
  output = populations_vg_rho
  output = populations_vg_v
  output = populations_vg_ptensor
  output = fg_e
  output = fg_b
  output = vg_boundarytype
  output = vg_boundarylayer
  output = vg_rank
  output = vg_b_vol_derivatives
  output = vg_amr_alpha
  output = vg_amr_jperb
  output = vg_loadbalance_weight
  output = populations_vg_blocks
  diagnostic = populations_vg_blocks

  # Declare boundary conditions
  [boundaries]
  periodic_x = no
  periodic_y = yes
  periodic_z = yes
  boundary = Outflow
  boundary = Maxwellian
  
  [outflow]
  precedence = 3
  
  # NB population-specific boundary conditions!
  [proton_outflow]
  face = x+
  #face = y-
  #face = y+
  #face = z-
  #face = z+
  
  [maxwellian]
  precedence = 4
  face = x-
  
  [proton_maxwellian]
  dynamic = 0
  # select the sw1.dat file for inflow Maxwellian parameters
  file_x- = sw1.dat
  
  [proton_sparse]
  minValue = 1.0e-15
  

  # Project settings
  [Flowthrough]
  Bx = 1.0e-9
  By = 1.0e-9
  Bz = 1.0e-9
  
  # Population-specific project settings - initial condition
  [proton_Flowthrough]
  T = 1.0e5
  rho  = 1.0e6
  VX0 = 1e5
  VY0 = 0
  VZ0 = 0
  
  [loadBalance]
  # algorithm = RIB
  algorithm = RCB
  optionKey = RCB_RECTILINEAR_BLOCKS # Recommended to use with RCB
  optionValue = 1
  rebalanceInterval = 5 # in timesteps
  
  # Safety bailouts (stores restart for potential recovery)
  [bailout]
  velocity_space_wall_block_margin = 0
  
  
Performance monitoring
----------------------

``phiprof`` is the default, lightweight performance tool used in Vlasiator. These timers track time spent in pre-defined code sections, with nested levels.

.. code-block:: cfg

  Small phiprof output here

The ``tau`` profiler can also be used to hook into ``phiprof`` timers.

PAPI can be used for memory use monitoring, and it is recommended to be used - monitoring the high water marks of memory use is well worth the trouble.

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
^^^^^^^^^^^^^^^^

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

Notably, we are using here 16 MB buffers and a matching stripe unit. These give decent 90s writes for 5.5 TB restart files from 500 nodes on LUMI.

The following informs Vlasiator of the restart file striping on Lustre (see below):

.. code-block:: cfg

  write_restart_stripe_factor = 20

Babysitting
-----------

Vlasiator runs usually take a while to complete, and everything might not go as planned - node or interconnect failures come to mind. It is also easy to encounter edge cases where the plasma VDFs "hit the walls" of their velocity space, so prototyping and iteration of run configurations will come up. It is also good to keep track of the performance, memory consumption and accrued costs over the simulation run.

Writing restarts
^^^^^^^^^^^^^^^^

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

When restarting, you can change config file and job script parameters, to e.g. introduce new/forgotten output variables, updated binary, or additional nodes - as the run progresses, the kinetic VDFs will usually take up much more resources than the initial ones.

Restarted runs will append to an existing logfile. Even if you do multiple restarts from the same savestate.

External commands
^^^^^^^^^^^^^^^^^

One can signal Vlasiator during run-time via files in the run directory. For example, creating a STOP file by ``touch STOP`` will signal the run to dump a restart and quit gracefully. The filename is appended with a timestamp. Other commands are available:

* ``SAVE``

  Dump a new restart file.

* ``STOP``

  Stop the run with a restart write.

* ``KILL``

  Stop the run *without* a restart write.

* ``DOLB``

  Force a load balance refresh - if walltime per timestep has grown unexpectedly, this might help.

* ``DOMR``

  Force a mesh re-refinement.

Exercises
=========

Today we will look at running small-ish simulations and scaling tests. We'll start by performing few runs to fill in a scaling test spreadsheet and draw some conclusions from those runs. There are few heavier prototypes for overnight runs or heavier testing, and we will get to know tools for inspecting the Vlasiator outputs tomorrow.

Scaling test
------------

*Getting to know the basic run setup.*

We are going to be running a Flowthrough test to look a bit at weak scaling. Find the configuration file and the job script from ``/scratch/project_465000693/example_runs/scaling/baseline/Flowthrough_amr.cfg``.

The test is a tube, with initial solar wind plasma flowing along the X direction. The inflow boundary injects faster, more dense solar wind into the domain, and the Y and Z directions are periodic. Dynamic AMR is applied to the simulation, tracking the interface between fast and slow flows.

To calculate weak scaling, we will expand the Y and Z dimensions of the domain with some factors, with a matching increase in cores. To inspect task-thread balance, we move from having many tasks with few cores per task to few tasks with many cores per task - but keep the number of cores constant!

Pick a line or two for yourselves and modify your config and job script accordingly. The shared sheet has some predetermined values, but feel free to experiment further (and add lines with notes).

Prototype: Magnetosphere3D/Ionosphere3D
---------------------------------------

*Advanced playthings*

These prototypes can be played with - Magnetosphere3D configuration is included in the Vlasiator master under ``samples/``. The sample magnetosphere is a good example of inner boundary instabilities at low resolutions - inner boundary VDFs hit the walls after ~60s of simulation time.

Ionosphere3D is freshly adapted version of the above to use an ionospheric inner boundary, and is somewhat more stable (with a highest-resolution region used for the inner boundary).

Note that these are "cheap" to run, expected O(100k) CPUh cost for a ~fully-developed system at around 1000s. If you wish to run these or use altered parameters, please feel free, but it may be a good idea to team up! Expect to use 16 nodes, so it would be hard to guarantee slots for everyone. You may also pick up the Ionosphere3D example run restart and keep running from there.

Prototype: Mercury5D
--------------------

*Audience request*

This is a prototype 2D/5D equatorial Mercury run, with a foreshock. Example run can be picked up for restarting. These runs have proved to be somewhat tricky, and proper treatment of Mercury will require some code extensions (and the coders to do that coding!). What would be required can be discussed in breakout session.

Find this run from:
``/pfs/lustrep2/scratch/project_465000693/example_runs/Mercury5D``

Other practical aspects
-----------------------

The rest of the day we get to play with running Vlasiator! Feel free to scatter, discuss, and join the online workshopping rooms, see HackMD for specifics.


Interesting questions you might get
-----------------------------------



Typical pitfalls
----------------


