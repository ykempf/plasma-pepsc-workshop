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
  
  
Checking the configuration file
-------------------------------
In the source code we have a script `tools/check_vlasiator_cfg.sh` that helps you checking that every option in your config file is sane. As of February 2024 needs a slight modification to run on LUMI, remove "mpirun" from the quotes in the first line and just leave a space `" "`. If you have to use a specific launcher to run the binary in your system, insert that instead.
Run with
```
./check_vlasiator_cfg.sh ./vlasiator ./<your cfg file>
```
and it prints
- a list of options you could have used but are not explicitly in your cfg file
- a list of output variables you could have listed but are not using
- a list of invalid options in your cfg file (fix/remove those!)
- a list of invalid output variables in your cfg file (fix/remove those too!)


Performance monitoring
----------------------

Logfile.txt can be used for basic monitoring.

``phiprof`` is the default, lightweight performance tool used in Vlasiator. These timers track time spent in pre-defined code sections, with nested levels.

.. code-block:: cfg

                                                          All timers. Set of identical timers has 461 processes with up to 16 threads each.
  ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   |                                                                             | Threads |                         Time (s)                          | Calls  |               Workunit-rate               | 
  ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   | Id  | Lvl | Grp | Label                                                     | Avg     | Avg       | %         |  Max time,rank  |  Min time,rank  | Avg    | Total     | Per process | Unit            | 
  ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   | 1   | 1   |     | main                                                      | 1       | 8447      | 100       | 8447      | 29  | 8446      | 352 | 1      |           |             |                 | 
   | 2   | 2   |     |   Initialization                                          | 1       | 56.34     | 0.667     | 56.35     | 240 | 56.31     | 486 | 1      |           |             |                 | 
   | 3   | 3   |     |     Read parameters                                       | 1       | 0.09863   | 0.1751    | 0.1109    | 272 | 0.06298   | 486 | 1      |           |             |                 | 
   | 4   | 3   |     |     open logFile & diagnostic                             | 1       | 8.322e-05 | 0.0001477 | 0.005583  | 0   | 3.35e-05  | 299 | 1      |           |             |                 | 
   | 5   | 3   |     |     Init project                                          | 1       | 1.566e-05 | 2.78e-05  | 0.0001138 | 101 | 1.223e-06 | 491 | 1      |           |             |                 | 
   | 6   | 3   |     |     Init fieldsolver grids                                | 1       | 0.02803   | 0.04976   | 0.03005   | 187 | 0.02409   | 0   | 1      |           |             |                 | 
   | 7   | 3   |     |     Init grids                                            | 1       | 56.05     | 99.49     | 56.07     | 419 | 56.03     | 63  | 1      |           |             |                 | 
   | 8   | 4   |     |       Refine spatial cells                                | 1       | 13.26     | 23.66     | 13.8      | 509 | 13.04     | 269 | 1      |           |             |                 | 
   | 9   | 5   |     |         Override refines                                  | 1       | 3.119     | 23.52     | 3.513     | 0   | 0.01176   | 225 | 2      |           |             |                 | 
   | 10  | 5   |     |         Induce refines                                    | 1       | 1.417     | 10.69     | 1.419     | 80  | 1.416     | 326 | 2      |           |             |                 | 
   | 11  | 5   |     |         Override unrefines                                | 1       | 0.002455  | 0.01851   | 0.003982  | 259 | 0.0004373 | 80  | 2      |           |             |                 | 
   | 12  | 5   |     |         Map Refinement Level to FsGrid                    | 1       | 0.002119  | 0.01598   | 0.005737  | 283 | 0.00164   | 436 | 1      |           |             |                 | 
   |     | 5   |     |         Other                                             | 1       | 8.722     | 65.76     | 11.61     | 225 | 8.221     | 409 | 1      |           |             |                 | 
   | 13  | 4   |     |       Initial load-balancing                              | 1       | 3.444     | 6.145     | 4.54      | 265 | 2.344     | 368 | 1      |           |             |                 | 
   | 14  | 4   |     |       Set initial state                                   | 1       | 38.26     | 68.25     | 39.11     | 8   | 37.5      | 61  | 1      |           |             |                 | 
   | 15  | 5   |     |         Set spatial cell coordinates                      | 1       | 0.00045   | 0.001176  | 0.0008721 | 91  | 0.0001717 | 480 | 1      |           |             |                 | 
   | 16  | 5   |     |         Initialize system boundary conditions             | 1       | 0.08176   | 0.2137    | 0.1041    | 8   | 0.07811   | 133 | 1      |           |             |                 | 
   | 17  | 6   |     |           ionosphere-sphericalFibonacci                   | 1       | 0.01461   | 17.87     | 0.01762   | 431 | 0.0142    | 11  | 1      |           |             |                 | 
   | 18  | 6   |     |           ionosphere-subdivideElement                     | 1       | 0.01286   | 15.73     | 0.01678   | 239 | 0.01116   | 316 | 12758  |           |             |                 | 
   | 19  | 6   |     |           ionosphere-readAtmosphericModelFile             | 1       | 0.002412  | 2.95      | 0.02269   | 8   | 0.002031  | 288 | 1      |           |             |                 | 
   |     | 6   |     |           Other                                           | 1       | 0.05188   | 63.45     | 0.05909   | 442 | 0.0505    | 67  | 1      |           |             |                 | 
   | 20  | 5   |     |         Classify cells (sys boundary conditions)          | 1       | 0.4128    | 1.079     | 1.44      | 17  | 0.142     | 2   | 1      |           |             |                 | 
   | 21  | 5   |     |         Read restart                                      | 1       | 14.5      | 37.91     | 14.51     | 48  | 14.5      | 339 | 1      |           |             |                 | 
   | 22  | 6   |     |           readGrid                                        | 1       | 14.5      | 99.99     | 14.51     | 56  | 14.5      | 339 | 1      |           |             |                 | 
   | 23  | 7   |     |             readScalars                                   | 1       | 0.02776   | 0.1914    | 0.03241   | 56  | 0.02425   | 339 | 1      |           |             |                 | 
   | 24  | 7   |     |             readDatalayout                                | 1       | 6.164     | 42.5      | 6.165     | 268 | 6.164     | 320 | 1      |           |             |                 | 
   | 25  | 7   |     |             readCellParameters                            | 1       | 1.334     | 9.197     | 1.334     | 320 | 1.333     | 268 | 1      |           |             |                 | 
   | 26  | 7   |     |             readBlockData                                 | 1       | 5.964     | 41.12     | 6.419     | 384 | 5.861     | 9   | 1      |           |             |                 | 
   | 27  | 7   |     |             updateMpiGridNeighbors                        | 1       | 0.4356    | 3.004     | 0.5568    | 17  | 0.01425   | 416 | 1      |           |             |                 | 
   | 28  | 7   |     |             readFsGrid                                    | 1       | 0.4992    | 3.442     | 0.9608    | 188 | 0.4594    | 385 | 1      |           |             |                 | 
   | 29  | 8   |     |               updateGhostCells                            | 1       | 0.01472   | 2.949     | 0.04934   | 469 | 0.00222   | 7   | 2      |           |             |                 | 
   |     | 8   |     |               Other                                       | 1       | 0.4845    | 97.05     | 0.9564    | 188 | 0.4167    | 470 | 1      |           |             |                 | 
   | 30  | 7   |     |             readIonosphere                                | 1       | 0.07711   | 0.5317    | 0.07732   | 48  | 0.0764    | 398 | 1      |           |             |                 | 
   |     | 7   |     |             Other                                         | 1       | 0.001704  | 0.01175   | 0.01768   | 489 | 0.001147  | 48  | 1      |           |             |                 | 
   |     | 6   |     |           Other                                           | 1       | 0.001097  | 0.007561  | 0.004076  | 48  | 0.0005522 | 365 | 1      |           |             |                 | 
   | 31  | 5   |     |         Check boundary refinement                         | 1       | 0.0007237 | 0.001892  | 0.007383  | 422 | 2.734e-05 | 274 | 1      |           |             |                 | 
   | 32  | 5   |     |         Apply system boundary conditions state            | 1       | 0.0007087 | 0.001853  | 0.02225   | 388 | 1.001e-06 | 440 | 1      |           |             |                 | 
   | 33  | 5   | D   |         Balancing load                                    | 1       | 6.279     | 16.41     | 6.762     | 451 | 5.144     | 467 | 1      |           |             |                 | 
   | 34  | 6   |     |           deallocate boundary data                        | 1       | 0.001852  | 0.02949   | 0.00632   | 385 | 0.0006113 | 225 | 1      |           |             |                 | 
   | 35  | 6   |     |           dccrg.initialize_balance_load                   | 1       | 0.544     | 8.664     | 0.5548    | 114 | 0.519     | 452 | 1      |           |             |                 | 
   | 36  | 6   |     |           Data transfers                                  | 1       | 0.4398    | 7.005     | 0.82      | 8   | 0.04192   | 54  | 1      |           |             |                 | 
   | 37  | 7   |     |             Preparing receives                            | 1       | 0.05701   | 12.96     | 0.169     | 448 | 6.501e-07 | 511 | 1643   | 1.329e+07 | 2.883e+04   | Spatial cells/s | 
   | 38  | 7   |     |             transfer_all_data                             | 1       | 0.2809    | 63.87     | 0.6845    | 8   | 0.01069   | 454 | 5      |           |             |                 | 
   |     | 7   |     |             Other                                         | 1       | 0.1019    | 23.17     | 0.5186    | 242 | 0.005889  | 220 | 1      |           |             |                 | 
   | 39  | 6   |     |           dccrg.finish_balance_load                       | 1       | 1.458     | 23.22     | 4.899     | 19  | 0.4524    | 10  | 1      |           |             |                 | 
   | 40  | 6   |     |           compute_amr_transfer_flags                      | 1       | 0.006867  | 0.1094    | 0.07725   | 419 | 0.001871  | 38  | 1      |           |             |                 | 
   | 41  | 6   |     |           update block lists                              | 1       | 2.087     | 33.25     | 4.207     | 346 | 0.09587   | 407 | 1      |           |             |                 | 
   | 42  | 7   | E   |             Velocity block list update                    | 1       | 1.967     | 94.25     | 4.054     | 271 | 0.02872   | 231 | 1      |           |             |                 | 
   | 43  | 7   |     |             Preparing receives                            | 1       | 0.1198    | 5.742     | 0.2648    | 29  | 0.03104   | 441 | 1      | 1.547e+07 | 3.355e+04   | SpatialCells/s  | 
   |     | 7   |     |             Other                                         | 1       | 0.0001002 | 0.0048    | 0.004895  | 448 | 9.859e-06 | 253 | 1      |           |             |                 | 
   | 44  | 6   |     |           update sysboundaries                            | 1       | 0.002269  | 0.03614   | 0.03475   | 187 | 7.975e-05 | 258 | 1      |           |             |                 | 
   | 45  | 7   |     |             updateSysBoundariesAfterLoadBalance           | 1       | 0.002259  | 99.57     | 0.03474   | 187 | 7.706e-05 | 258 | 1      |           |             |                 | 
   |     | 7   |     |             Other                                         | 1       | 9.825e-06 | 0.433     | 0.0007654 | 424 | 1.844e-06 | 173 | 1      |           |             |                 | 
   | 46  | 6   |     |           Init solvers                                    | 1       | 5.478e-06 | 8.725e-05 | 0.000501  | 424 | 1.503e-06 | 186 | 1      |           |             |                 | 
   | 47  | 6   |     |           set face neighbor ranks                         | 1       | 0.0251    | 0.3997    | 0.08548   | 69  | 0.008767  | 372 | 1      |           |             |                 | 
   | 48  | 6   |     |           GetSeedIdsAndBuildPencils                       | 1       | 0.04302   | 0.6851    | 0.4       | 451 | 0.0137    | 372 | 1      |           |             |                 | 
   | 49  | 7   |     |             getSeedIds                                    | 1       | 0.007916  | 18.4      | 0.05184   | 451 | 0.002307  | 292 | 3      |           |             |                 | 
   | 50  | 7   |     |             buildPencils                                  | 1       | 0.03479   | 80.88     | 0.3432    | 451 | 0.01127   | 372 | 3      |           |             |                 | 
   | 51  | 8   |     |               check_ghost_cells                           | 1       | 0.001349  | 3.878     | 0.2473    | 451 | 8.518e-05 | 51  | 3      |           |             |                 | 
   |     | 8   |     |               Other                                       | 1       | 0.03344   | 96.12     | 0.1216    | 425 | 0.01118   | 372 | 3      |           |             |                 | 
   |     | 7   |     |             Other                                         | 1       | 0.0003073 | 0.7143    | 0.004975  | 451 | 5.954e-05 | 323 | 1      |           |             |                 | 
   |     | 6   |     |           Other                                           | 1       | 1.67      | 26.6      | 4.312     | 335 | 0.01161   | 235 | 1      |           |             |                 | 
   | 52  | 5   | E   |         Fetch Neighbour data                              | 1       | 0.1985    | 0.5189    | 1.346     | 467 | 0.008552  | 419 | 1      |           |             |                 | 
   | 53  | 5   |     |         setProjectBField                                  | 1       | 15.92     | 41.63     | 16.22     | 390 | 15.56     | 452 | 1      |           |             |                 | 
   | 54  | 5   |     |         Init moments                                      | 1       | 0.1236    | 0.3231    | 0.1522    | 422 | 0.1015    | 110 | 1      |           |             |                 | 
   | 55  | 5   |     |         Finish fsgrid setup                               | 1       | 0.2395    | 0.6261    | 0.275     | 289 | 0.2013    | 69  | 1      |           |             |                 | 
   | 56  | 6   |     |           AMR Filtering-Triangle-3D                       | 1       | 0.1186    | 49.51     | 0.1751    | 353 | 0.06054   | 0   | 2      |           |             |                 | 
   |     | 6   |     |           Other                                           | 1       | 0.1209    | 50.49     | 0.1792    | 456 | 0.06876   | 89  | 1      |           |             |                 | 
   |     | 5   |     |         Other                                             | 1       | 0.4901    | 1.281     | 1.414     | 435 | 0.006689  | 291 | 1      |           |             |                 | 
   |     | 4   |     |       Other                                               | 1       | 1.089     | 1.943     | 2.09      | 207 | 0.7609    | 506 | 1      |           |             |                 | 
   | 57  | 3   |     |     Init DROs                                             | 1       | 0.0004287 | 0.0007609 | 0.007283  | 448 | 0.000176  | 274 | 1      |           |             |                 | 
   | 58  | 3   |     |     getFieldsFromFsGrid                                   | 1       | 0.06079   | 0.1079    | 0.0892    | 63  | 0.03098   | 224 | 1      |           |             |                 | 
   | 59  | 3   |     |     ionosphere-updateIonosphereCommunicator               | 1       | 0.0208    | 0.03692   | 0.04898   | 85  | 0.001027  | 284 | 1      |           |             |                 | 
   | 60  | 3   |     |     fieldtracing-ionosphere-fsgridCoupling                | 1       | 0.07022   | 0.1246    | 0.07346   | 64  | 0.04959   | 476 | 1      |           |             |                 | 
   | 61  | 3   |     |     ionosphere-initSolver                                 | 1       | 0.004485  | 0.007961  | 0.01555   | 425 | 0.00365   | 294 | 1      |           |             |                 | 
   |     | 3   |     |     Other                                                 | 1       | 0.003553  | 0.006306  | 0.02718   | 495 | 5.835e-05 | 128 | 1      |           |             |                 | 
   | 62  | 2   |     |   report-memory-consumption                               | 1       | 0.05788   | 0.0006852 | 0.08273   | 0   | 0.04845   | 407 | 1      |           |             |                 | 
   | 63  | 2   |     |   Simulation                                              | 1       | 8390      | 99.33     | 8391      | 29  | 8390      | 352 | 1      |           |             |                 | 
   | 64  | 3   |     |     IO                                                    | 1       | 152.3     | 1.815     | 200.5     | 95  | 126.1     | 29  | 759    |           |             |                 | 
   | 65  | 4   |     |       checkExternalCommands                               | 1       | 0.003633  | 0.002385  | 1.571     | 0   | 0.0001467 | 334 | 759    |           |             |                 | 
   | 66  | 4   |     |       logfile-io                                          | 1       | 0.03492   | 0.02293   | 0.2181    | 0   | 0.02167   | 68  | 759    |           |             |                 | 
   | 67  | 4   |     |       Bailout-allreduce                                   | 1       | 33.55     | 22.03     | 81.67     | 95  | 8.082     | 29  | 759    |           |             |                 | 
   | 68  | 4   |     |       compute-is-restart-written-and-extra-LB             | 1       | 0.01469   | 0.009645  | 0.01983   | 496 | 0.01111   | 78  | 759    |           |             |                 | 
   | 169 | 4   |     |       diagnostic-io                                       | 1       | 0.5115    | 0.3358    | 6.001     | 352 | 0.01028   | 329 | 76     |           |             |                 | 
   | 196 | 4   |     |       Calculate volume gradients                          | 1       | 0.3295    | 0.2163    | 0.8119    | 95  | 0.09899   | 491 | 10     | 4.973e+07 | 1.079e+05   | Spatial Cells/s | 
   | 197 | 5   | E   |         Start comm                                        | 1       | 0.2989    | 90.71     | 0.7672    | 95  | 0.07832   | 491 | 10     | 5.482e+07 | 1.189e+05   | Spatial Cells/s | 
   | 198 | 5   |     |         Compute cells                                     | 1       | 0.03055   | 9.271     | 0.09107   | 371 | 0.01067   | 192 | 10     | 5.364e+08 | 1.163e+06   | Spatial Cells/s | 
   |     | 5   |     |         Other                                             | 1       | 4.922e-05 | 0.01494   | 0.0006382 | 254 | 2.93e-05  | 334 | 10     |           |             |                 | 
   | 199 | 4   |     |       fieldtracing-ionosphere-openclosedTracing           | 1       | 1.076     | 0.7062    | 1.416     | 235 | 0.9152    | 19  | 10     |           |             |                 | 
   | 200 | 4   |     |       fieldtracing-fullAndFluxTracing                     | 1       | 72.3      | 47.47     | 72.33     | 247 | 72.29     | 323 | 10     |           |             |                 | 
   | 201 | 5   |     |         initialization-loop                               | 1       | 0.9673    | 1.338     | 1.02      | 247 | 0.9424    | 445 | 10     |           |             |                 | 
   | 202 | 5   |     |         loop                                              | 1       | 67.91     | 93.93     | 67.97     | 0   | 67.86     | 107 | 10     |           |             |                 | 
   | 203 | 6   |     |           MPI-loop                                        | 16      | 183.1     | 269.6     | 231.2     | 429 | 108.1     | 285 | 500    |           |             |                 | 
   | 204 | 5   |     |         final-loop                                        | 1       | 0.3835    | 0.5304    | 0.4107    | 247 | 0.3736    | 323 | 10     |           |             |                 | 
   |     | 5   |     |         Other                                             | 1       | 3.041     | 4.206     | 3.077     | 107 | 2.968     | 0   | 10     |           |             |                 | 
   | 205 | 4   |     |       write-system                                        | 1       | 18.68     | 12.26     | 18.89     | 360 | 18.32     | 9   | 10     |           |             |                 | 
   | 206 | 5   | EA  |         Barrier-entering-writegrid                        | 1       | 0.4146    | 2.22      | 0.6223    | 360 | 0.0607    | 9   | 10     |           |             |                 | 
   | 207 | 5   |     |         writeGrid-reduced                                 | 1       | 18.26     | 97.77     | 18.26     | 304 | 18.24     | 239 | 10     | 0.5316    | 0.001153    | GB/s            | 
   | 208 | 6   |     |           open                                            | 1       | 0.7832    | 4.289     | 0.8339    | 464 | 0.715     | 421 | 10     |           |             |                 | 
   | 209 | 6   |     |           metadataIO                                      | 1       | 2.243     | 12.28     | 2.244     | 128 | 2.201     | 473 | 10     |           |             |                 | 
   | 210 | 6   |     |           velocityspaceIO                                 | 1       | 0.1373    | 0.7521    | 0.1374    | 8   | 0.1373    | 494 | 10     |           |             |                 | 
   | 211 | 6   |     |           reduceddataIO                                   | 1       | 15.06     | 82.45     | 15.06     | 505 | 15.05     | 64  | 10     |           |             |                 | 
   | 212 | 7   |     |             writeDataReducer                              | 1       | 15.05     | 99.99     | 15.05     | 509 | 15.05     | 3   | 10     |           |             |                 | 
   | 358 | 7   | EA  |             Barrier                                       | 1       | 0.000446  | 0.002963  | 0.0005074 | 1   | 0.0002238 | 476 | 10     |           |             |                 | 
   |     | 7   |     |             Other                                         | 1       | 0.0009875 | 0.006559  | 0.00157   | 473 | 0.0002494 | 400 | 10     |           |             |                 | 
   | 359 | 6   |     |           close                                           | 1       | 0.03292   | 0.1803    | 0.03422   | 358 | 0.02962   | 456 | 10     |           |             |                 | 
   |     | 6   |     |           Other                                           | 1       | 0.00834   | 0.04567   | 0.0748    | 416 | 0.0003039 | 167 | 10     |           |             |                 | 
   |     | 5   |     |         Other                                             | 1       | 0.00232   | 0.01242   | 0.03255   | 376 | 0.0003313 | 321 | 10     |           |             |                 | 
   | 360 | 4   |     |       write-restart                                       | 1       | 25.43     | 16.69     | 25.52     | 29  | 25.31     | 95  | 1      |           |             |                 | 
   | 361 | 5   | EA  |         BarrierEnteringWriteRestart                       | 1       | 0.0008407 | 0.003306  | 0.001098  | 6   | 1.548e-05 | 471 | 1      |           |             |                 | 
   | 362 | 5   |     |         writeRestart                                      | 1       | 25.42     | 99.99     | 25.52     | 29  | 25.31     | 95  | 1      | 10.42     | 0.0226      | GB/s            | 
   | 363 | 6   |     |           DeallocateRemoteBlocks                          | 1       | 0.0256    | 0.1007    | 0.05758   | 29  | 0.0102    | 489 | 1      |           |             |                 | 
   | 364 | 6   |     |           open                                            | 1       | 0.04866   | 0.1914    | 0.04887   | 0   | 0.0477    | 424 | 1      |           |             |                 | 
   | 365 | 6   |     |           metadataIO                                      | 1       | 2.969     | 11.68     | 2.969     | 262 | 2.969     | 7   | 1      |           |             |                 | 
   | 366 | 6   |     |           reduceddataIO                                   | 1       | 10.58     | 41.63     | 10.58     | 0   | 10.57     | 105 | 1      |           |             |                 | 
   | 433 | 6   |     |           velocityspaceIO                                 | 1       | 11.29     | 44.39     | 11.29     | 143 | 11.27     | 175 | 1      |           |             |                 | 
   | 434 | 6   |     |           close                                           | 1       | 0.182     | 0.7159    | 0.1822    | 0   | 0.1632    | 7   | 1      |           |             |                 | 
   | 435 | 6   |     |           updateRemoteBlocks                              | 1       | 0.1936    | 0.7617    | 0.2922    | 29  | 0.08067   | 95  | 1      |           |             |                 | 
   | 436 | 7   | E   |             Velocity block list update                    | 1       | 0.07758   | 40.06     | 0.1156    | 313 | 0.04427   | 97  | 1      |           |             |                 | 
   | 437 | 7   |     |             Preparing receives                            | 1       | 0.116     | 59.92     | 0.2124    | 29  | 0.03089   | 95  | 1      | 1.601e+07 | 3.473e+04   | SpatialCells/s  | 
   |     | 7   |     |             Other                                         | 1       | 3.954e-05 | 0.02042   | 0.008907  | 94  | 1.009e-05 | 153 | 1      |           |             |                 | 
   |     | 6   |     |           Other                                           | 1       | 0.1344    | 0.5287    | 0.1609    | 97  | 0.1022    | 29  | 1      |           |             |                 | 
   |     | 5   |     |         Other                                             | 1       | 0.002589  | 0.01018   | 0.03064   | 195 | 6.623e-05 | 355 | 1      |           |             |                 | 
   |     | 4   |     |       Other                                               | 1       | 0.3924    | 0.2576    | 0.7548    | 9   | 0.1819    | 360 | 759    |           |             |                 | 
   | 69  | 3   |     |     Propagate                                             | 1       | 8068      | 96.15     | 8094      | 29  | 8019      | 95  | 759    | 5.439e+09 | 1.18e+07    | Cells/s         | 
   | 70  | 4   |     |       Spatial-space                                       | 1       | 4172      | 51.71     | 4180      | 307 | 4164      | 110 | 759    | 1.052e+10 | 2.282e+07   | Cells/s         | 
   | 71  | 5   |     |         semilag-trans                                     | 1       | 4172      | 100       | 4180      | 307 | 4164      | 110 | 759    |           |             |                 | 
   | 72  | 6   |     |           compute_cell_lists                              | 1       | 0.1408    | 0.003375  | 0.6254    | 371 | 0.0462    | 258 | 759    |           |             |                 | 
   | 73  | 6   |     |           translate proton                                | 1       | 4127      | 98.93     | 4127      | 309 | 4127      | 371 | 759    |           |             |                 | 
   | 74  | 7   | BE  |             barrier-trans-pre-z                           | 1       | 1.021     | 0.02475   | 1.122     | 309 | 0.5356    | 371 | 759    |           |             |                 | 
   | 75  | 7   | E   |             transfer-stencil-data-z                       | 1       | 286.7     | 6.948     | 408.4     | 27  | 97.35     | 69  | 759    |           |             |                 | 
   | 76  | 7   |     |             compute-mapping-z                             | 1       | 357.6     | 8.664     | 673.1     | 140 | 207.3     | 186 | 759    |           |             |                 | 
   | 77  | 8   |     |               setup                                       | 1       | 9.725     | 2.72      | 27.76     | 494 | 4.79      | 372 | 759    |           |             |                 | 
   | 78  | 9   |     |                 buildBlockList                            | 1       | 4.477     | 46.03     | 14.49     | 113 | 1.243     | 148 | 759    |           |             |                 | 
   | 79  | 9   |     |                 computeSpatialTargetCellsForPencils       | 1       | 5.018     | 51.59     | 18.2      | 494 | 1.425     | 162 | 759    |           |             |                 | 
   |     | 9   |     |                 Other                                     | 1       | 0.2311    | 2.376     | 0.7481    | 441 | 0.09204   | 433 | 759    |           |             |                 | 
   | 80  | 8   |     |               mapping                                     | 16      | 217.2     | 60.74     | 412.5     | 201 | 106.5     | 187 | 91523  |           |             |                 | 
   | 81  | 8   |     |               store                                       | 16      | 109.3     | 30.57     | 207.2     | 140 | 47.21     | 217 | 91523  |           |             |                 | 
   |     | 8   |     |               Other                                       | 1       | 21.37     | 5.975     | 75.72     | 69  | 4.764     | 332 | 759    |           |             |                 | 
   | 82  | 7   | BE  |             barrier-trans-pre-update_remote-z             | 1       | 398       | 9.644     | 668.9     | 187 | 115.7     | 201 | 759    |           |             |                 | 
   | 83  | 7   | E   |             update_remote-z                               | 1       | 388.4     | 9.41      | 397.6     | 27  | 380.2     | 69  | 759    |           |             |                 | 
   | 84  | 7   | BE  |             barrier-trans-pre-x                           | 1       | 9.746     | 0.2361    | 17.89     | 69  | 0.5317    | 27  | 759    |           |             |                 | 
   | 85  | 7   | E   |             transfer-stencil-data-x                       | 1       | 277.6     | 6.726     | 368       | 368 | 69.34     | 187 | 759    |           |             |                 | 
   | 86  | 7   |     |             compute-mapping-x                             | 1       | 356       | 8.627     | 747.7     | 337 | 202.1     | 186 | 759    |           |             |                 | 
   | 87  | 8   |     |               setup                                       | 1       | 12.76     | 3.585     | 46.76     | 113 | 5.537     | 190 | 759    |           |             |                 | 
   | 88  | 9   |     |                 buildBlockList                            | 1       | 7.574     | 59.34     | 25.34     | 113 | 2.459     | 148 | 759    |           |             |                 | 
   | 89  | 9   |     |                 computeSpatialTargetCellsForPencils       | 1       | 4.935     | 38.66     | 22.7      | 252 | 1.359     | 355 | 759    |           |             |                 | 
   |     | 9   |     |                 Other                                     | 1       | 0.2551    | 1.999     | 0.7575    | 441 | 0.1093    | 437 | 759    |           |             |                 | 
   | 90  | 8   |     |               mapping                                     | 16      | 219.3     | 61.61     | 487.5     | 337 | 130.3     | 187 | 91798  |           |             |                 | 
   | 91  | 8   |     |               store                                       | 16      | 103.9     | 29.18     | 201.5     | 337 | 47.16     | 186 | 91798  |           |             |                 | 
   |     | 8   |     |               Other                                       | 1       | 20.03     | 5.626     | 73.57     | 422 | 4.528     | 221 | 759    |           |             |                 | 
   | 92  | 7   | BE  |             barrier-trans-pre-update_remote-x             | 1       | 443       | 10.73     | 735.9     | 187 | 1.142     | 337 | 759    |           |             |                 | 
   | 93  | 7   | E   |             update_remote-x                               | 1       | 340.7     | 8.255     | 346.4     | 126 | 334.5     | 187 | 759    |           |             |                 | 
   | 94  | 7   | BE  |             barrier-trans-pre-y                           | 1       | 6.601     | 0.16      | 12.8      | 187 | 0.8621    | 126 | 759    |           |             |                 | 
   | 95  | 7   | E   |             transfer-stencil-data-y                       | 1       | 275.6     | 6.678     | 363.1     | 290 | 54.37     | 187 | 759    |           |             |                 | 
   | 96  | 7   |     |             compute-mapping-y                             | 1       | 347.6     | 8.423     | 569.8     | 281 | 165.9     | 329 | 759    |           |             |                 | 
   | 97  | 8   |     |               setup                                       | 1       | 14.53     | 4.18      | 36.49     | 113 | 7.491     | 319 | 759    |           |             |                 | 
   | 98  | 9   |     |                 buildBlockList                            | 1       | 9.368     | 64.48     | 20.45     | 113 | 2.522     | 148 | 759    |           |             |                 | 
   | 99  | 9   |     |                 computeSpatialTargetCellsForPencils       | 1       | 4.917     | 33.84     | 20.54     | 252 | 1.438     | 184 | 759    |           |             |                 | 
   |     | 9   |     |                 Other                                     | 1       | 0.244     | 1.679     | 0.7736    | 398 | 0.1029    | 155 | 759    |           |             |                 | 
   | 100 | 8   |     |               mapping                                     | 16      | 209.3     | 60.22     | 373       | 281 | 105       | 187 | 91156  |           |             |                 | 
   | 101 | 8   |     |               store                                       | 16      | 103       | 29.63     | 179.7     | 113 | 38.33     | 329 | 91156  |           |             |                 | 
   |     | 8   |     |               Other                                       | 1       | 20.76     | 5.972     | 86.9      | 69  | 4.44      | 326 | 759    |           |             |                 | 
   | 102 | 7   | BE  |             barrier-trans-pre-update_remote-y             | 1       | 294.6     | 7.138     | 619.4     | 187 | 13.89     | 281 | 759    |           |             |                 | 
   | 103 | 7   | E   |             update_remote-y                               | 1       | 335.3     | 8.124     | 343.7     | 11  | 327.9     | 324 | 759    |           |             |                 | 
   | 104 | 7   | BE  |             barrier-trans-post-trans                      | 1       | 8.532     | 0.2067    | 15.89     | 324 | 0.11      | 11  | 759    |           |             |                 | 
   |     | 7   |     |             Other                                         | 1       | 0.06994   | 0.001695  | 0.1841    | 489 | 0.04843   | 385 | 759    |           |             |                 | 
   | 105 | 6   |     |           compute-moments-n                               | 1       | 44.68     | 1.071     | 52.86     | 307 | 36.79     | 110 | 759    |           |             |                 | 
   |     | 6   |     |           Other                                           | 1       | 0.02026   | 0.0004856 | 0.07562   | 371 | 0.009199  | 323 | 759    |           |             |                 | 
   |     | 5   |     |         Other                                             | 1       | 0.008274  | 0.0001983 | 0.0533    | 492 | 0.002867  | 162 | 759    |           |             |                 | 
   | 106 | 4   |     |       Update system boundaries (Vlasov post-translation)  | 1       | 205.7     | 2.55      | 239.2     | 29  | 150.9     | 95  | 759    |           |             |                 | 
   | 107 | 5   | E   |         Velocity block list update                        | 1       | 109.3     | 53.14     | 145.2     | 173 | 49.15     | 253 | 1518   |           |             |                 | 
   | 108 | 5   |     |         Preparing receives                                | 1       | 49.77     | 24.2      | 138.5     | 252 | 8.072     | 187 | 1518   | 6.556e+07 | 1.422e+05   | SpatialCells/s  | 
   | 109 | 5   | E   |         Start comm of cell and block data                 | 1       | 4.594     | 2.233     | 38.41     | 316 | 0.4894    | 298 | 759    |           |             |                 | 
   | 110 | 5   |     |         Compute process inner cells                       | 1       | 2.093     | 1.018     | 28.05     | 253 | 0.03307   | 220 | 759    |           |             |                 | 
   | 111 | 6   |     |           compute-moments-n                               | 1       | 0.5362    | 25.62     | 8.324     | 253 | 0.003975  | 204 | 759    |           |             |                 | 
   |     | 6   |     |           Other                                           | 1       | 1.557     | 74.38     | 20.44     | 405 | 0.02823   | 220 | 759    |           |             |                 | 
   | 112 | 5   | EG  |         Wait for receives                                 | 1       | 32.31     | 15.71     | 103.7     | 369 | 0.5165    | 29  | 759    |           |             |                 | 
   | 113 | 5   |     |         Compute process boundary cells                    | 1       | 1.428     | 0.6943    | 14.68     | 253 | 0.04366   | 29  | 759    |           |             |                 | 
   | 114 | 6   |     |           compute-moments-n                               | 1       | 0.3696    | 25.88     | 4.468     | 253 | 0.003528  | 7   | 759    |           |             |                 | 
   |     | 6   |     |           Other                                           | 1       | 1.058     | 74.12     | 10.21     | 253 | 0.0394    | 29  | 759    |           |             |                 | 
   |     | 5   |     |         Other                                             | 1       | 6.195     | 3.012     | 16.34     | 38  | 1.249     | 373 | 759    |           |             |                 | 
   | 115 | 4   |     |       Compute interp moments                              | 1       | 0.3852    | 0.004775  | 1.547     | 328 | 0.1292    | 84  | 1518   |           |             |                 | 
   | 116 | 4   |     |       Propagate Fields                                    | 1       | 2338      | 28.98     | 2387      | 235 | 2300      | 29  | 759    | 5.319e+05 | 1154        | SpatialCells/s  | 
   | 117 | 5   |     |         fsgrid-coupling-in                                | 1       | 149.1     | 6.376     | 199.3     | 95  | 117.1     | 29  | 759    |           |             |                 | 
   | 118 | 6   |     |           AMR Filtering-Triangle-3D                       | 1       | 79.18     | 53.11     | 106.6     | 95  | 57.38     | 284 | 1518   |           |             |                 | 
   |     | 6   |     |           Other                                           | 1       | 69.9      | 46.89     | 122.7     | 352 | 33.39     | 243 | 759    |           |             |                 | 
   | 119 | 5   |     |         Propagate magnetic field                          | 1       | 333.8     | 14.28     | 579       | 416 | 194.1     | 219 | 21252  | 2.857e+09 | 6.198e+06   | Spatial Cells/s | 
   | 120 | 6   |     |           Compute cells                                   | 1       | 43.73     | 13.1      | 68.27     | 0   | 41.85     | 400 | 21252  | 2.181e+10 | 4.731e+07   | Spatial Cells/s | 
   | 121 | 6   | E   |           MPI                                             | 1       | 180.9     | 54.2      | 316.3     | 457 | 118.7     | 31  | 42504  |           |             |                 | 
   | 122 | 6   |     |           Compute system boundary cells                   | 1       | 109       | 32.67     | 394.2     | 416 | 4.367     | 99  | 63756  | 1.749e+10 | 3.794e+07   | /s              | 
   |     | 6   |     |           Other                                           | 1       | 0.1105    | 0.0331    | 0.1611    | 150 | 0.08503   | 28  | 21252  |           |             |                 | 
   | 123 | 5   |     |         Calculate face derivatives                        | 1       | 240.1     | 10.27     | 374       | 345 | 134.6     | 63  | 21252  | 3.971e+09 | 8.615e+06   | Spatial Cells/s | 
   | 124 | 6   | E   |           MPI                                             | 1       | 162.8     | 67.81     | 281.3     | 353 | 72.67     | 319 | 21252  |           |             |                 | 
   | 125 | 6   |     |           Compute cells                                   | 1       | 77.25     | 32.17     | 94.67     | 337 | 51.95     | 59  | 21252  | 1.234e+10 | 2.678e+07   | Spatial Cells/s | 
   |     | 6   |     |           Other                                           | 1       | 0.05519   | 0.02299   | 0.09542   | 209 | 0.03441   | 451 | 21252  |           |             |                 | 
   | 126 | 5   |     |         Calculate GradPe term                             | 1       | 16.23     | 0.6942    | 27.52     | 283 | 10.33     | 327 | 1518   | 4.197e+09 | 9.104e+06   | Spatial Cells/s | 
   | 127 | 6   | E   |           MPI                                             | 1       | 15.05     | 92.76     | 26.17     | 283 | 9.326     | 327 | 1518   |           |             |                 | 
   | 128 | 6   |     |           Compute cells                                   | 1       | 1.171     | 7.214     | 1.465     | 300 | 0.8719    | 5   | 1518   | 5.818e+10 | 1.262e+08   | Spatial Cells/s | 
   |     | 6   |     |           Other                                           | 1       | 0.004606  | 0.02838   | 0.006637  | 244 | 0.003104  | 384 | 1518   |           |             |                 | 
   | 129 | 5   |     |         Calculate Hall term                               | 1       | 663       | 28.36     | 845.5     | 274 | 486.1     | 63  | 21252  | 1.438e+09 | 3.12e+06    | Spatial Cells/s | 
   | 130 | 6   | E   |           MPI                                             | 1       | 173.8     | 26.21     | 316.8     | 274 | 95        | 127 | 21252  |           |             |                 | 
   | 131 | 6   |     |           Compute cells                                   | 1       | 489.1     | 73.78     | 529.6     | 418 | 383.2     | 455 | 21252  |           |             |                 | 
   |     | 6   |     |           Other                                           | 1       | 0.0765    | 0.01154   | 0.1332    | 213 | 0.04423   | 384 | 21252  |           |             |                 | 
   | 132 | 5   |     |         Calculate upwinded electric field                 | 1       | 784.3     | 33.55     | 1072      | 508 | 648.5     | 72  | 21252  | 1.216e+09 | 2.637e+06   | Spatial Cells/s | 
   | 133 | 6   | E   |           MPI                                             | 1       | 439.7     | 56.06     | 806.6     | 508 | 271.5     | 72  | 42504  |           |             |                 | 
   | 134 | 6   |     |           Compute cells                                   | 1       | 344.5     | 43.92     | 396.3     | 339 | 239.1     | 7   | 21252  | 2.768e+09 | 6.005e+06   | Spatial Cells/s | 
   |     | 6   |     |           Other                                           | 1       | 0.1828    | 0.02331   | 0.2597    | 174 | 0.1262    | 384 | 21252  |           |             |                 | 
   | 135 | 5   |     |         FS subcycle stuff                                 | 1       | 82.19     | 3.516     | 178.6     | 63  | 32.71     | 347 | 10626  |           |             |                 | 
   | 136 | 6   |     |           MPI_Allreduce                                   | 1       | 80.68     | 98.16     | 177.1     | 63  | 31.16     | 347 | 9867   |           |             |                 | 
   |     | 6   |     |           Other                                           | 1       | 1.515     | 1.844     | 1.661     | 377 | 1.287     | 44  | 10626  |           |             |                 | 
   | 137 | 5   |     |         Calculate volume averaged fields                  | 1       | 1.224     | 0.05237   | 1.469     | 436 | 0.9462    | 5   | 759    | 2.782e+10 | 6.034e+07   | Spatial Cells/s | 
   | 138 | 5   |     |         Calculate volume derivatives                      | 1       | 7.981     | 0.3414    | 10.1      | 438 | 5.108     | 7   | 759    | 4.267e+09 | 9.256e+06   | Spatial Cells/s | 
   | 139 | 6   | E   |           Start comm                                      | 1       | 7.188     | 90.06     | 9.251     | 438 | 4.523     | 7   | 759    | 4.738e+09 | 1.028e+07   | Spatial Cells/s | 
   | 140 | 6   |     |           Compute cells                                   | 1       | 0.7908    | 9.909     | 0.9636    | 154 | 0.5727    | 63  | 759    | 4.307e+10 | 9.342e+07   | Spatial Cells/s | 
   |     | 6   |     |           Other                                           | 1       | 0.002362  | 0.02959   | 0.01186   | 110 | 0.001497  | 505 | 759    |           |             |                 | 
   | 141 | 5   |     |         Calculate curvature                               | 1       | 4.991     | 0.2135    | 7.732     | 127 | 4.105     | 27  | 759    | 6.824e+09 | 1.48e+07    | Spatial Cells/s | 
   | 142 | 6   | E   |           Start comm                                      | 1       | 3.773     | 75.6      | 6.749     | 127 | 2.927     | 27  | 759    | 9.027e+09 | 1.958e+07   | Spatial Cells/s | 
   |     | 6   |     |           Other                                           | 1       | 1.218     | 24.4      | 1.414     | 366 | 0.8458    | 0   | 759    |           |             |                 | 
   | 143 | 5   |     |         getFieldsFromFsGrid                               | 1       | 49.23     | 2.106     | 63.17     | 284 | 31.06     | 88  | 759    |           |             |                 | 
   |     | 5   |     |         Other                                             | 1       | 5.849     | 0.2502    | 11.48     | 119 | 3.534     | 210 | 759    |           |             |                 | 
   | 144 | 4   |     |       Velocity-space                                      | 1       | 893.8     | 11.08     | 928.5     | 7   | 830.9     | 397 | 759    | 4.91e+10  | 1.065e+08   | Cells/s         | 
   | 145 | 5   |     |         semilag-acc                                       | 1       | 852.6     | 95.4      | 892.9     | 7   | 795.9     | 397 | 759    |           |             |                 | 
   | 146 | 6   |     |           Compute _V moments                              | 1       | 22.43     | 2.63      | 24.92     | 140 | 19.45     | 38  | 1518   |           |             |                 | 
   | 147 | 6   |     |           cell-semilag-acc                                | 16      | 470.6     | 55.19     | 558.6     | 242 | 395.8     | 10  | 158608 |           |             |                 | 
   | 148 | 7   |     |             compute-transform                             | 16      | 0.2146    | 0.04561   | 1.066     | 499 | 0.06968   | 372 | 158608 |           |             |                 | 
   | 149 | 7   |     |             compute-intersections                         | 16      | 0.07004   | 0.01488   | 0.3508    | 400 | 0.02048   | 258 | 158608 |           |             |                 | 
   | 150 | 7   |     |             compute-mapping                               | 16      | 470.1     | 99.9      | 558.1     | 242 | 395.5     | 10  | 158608 |           |             |                 | 
   |     | 7   |     |             Other                                         | 16      | 0.1851    | 0.03933   | 1.155     | 308 | 0.051     | 192 | 158608 |           |             |                 | 
   | 151 | 6   | C   |           re-adjust blocks                                | 1       | 321.6     | 37.71     | 408.2     | 10  | 215.3     | 484 | 1518   |           |             |                 | 
   | 152 | 7   |     |             Compute with_content_list                     | 1       | 39.93     | 12.42     | 65.07     | 307 | 27.81     | 333 | 1518   |           |             |                 | 
   | 153 | 7   | E   |             Transfer with_content_list                    | 1       | 134.5     | 41.83     | 233.7     | 10  | 31.66     | 97  | 1518   |           |             |                 | 
   | 154 | 7   |     |             Adjusting blocks                              | 1       | 85.3      | 26.53     | 106.9     | 292 | 65.34     | 398 | 1518   |           |             |                 | 
   | 155 | 7   | E   |             Velocity block list update                    | 1       | 41.97     | 13.05     | 70.57     | 302 | 16.17     | 332 | 759    |           |             |                 | 
   | 156 | 7   |     |             Preparing receives                            | 1       | 19.81     | 6.161     | 48.75     | 243 | 3.158     | 187 | 759    | 7.112e+07 | 1.543e+05   | SpatialCells/s  | 
   |     | 7   |     |             Other                                         | 1       | 0.01958   | 0.006089  | 0.03275   | 135 | 0.01447   | 253 | 1518   |           |             |                 | 
   |     | 6   |     |           Other                                           | 1       | 38.09     | 4.467     | 56.59     | 88  | 22.79     | 284 | 759    |           |             |                 | 
   | 157 | 5   |     |         Compute _V moments                                | 1       | 41.07     | 4.595     | 52.77     | 47  | 23.02     | 68  | 759    |           |             |                 | 
   |     | 5   |     |         Other                                             | 1       | 0.063     | 0.007049  | 0.1671    | 328 | 0.02175   | 124 | 759    |           |             |                 | 
   | 158 | 4   |     |       Update system boundaries (Vlasov post-acceleration) | 1       | 214.2     | 2.655     | 261.9     | 397 | 182.1     | 179 | 759    |           |             |                 | 
   | 159 | 5   | E   |         Velocity block list update                        | 1       | 109.9     | 51.31     | 158.7     | 69  | 50.82     | 240 | 1518   |           |             |                 | 
   | 160 | 5   |     |         Preparing receives                                | 1       | 47.05     | 21.97     | 132.6     | 252 | 7.282     | 187 | 1518   | 6.935e+07 | 1.504e+05   | SpatialCells/s  | 
   | 161 | 5   | E   |         Start comm of cell and block data                 | 1       | 4.782     | 2.233     | 36.23     | 316 | 0.4917    | 298 | 759    |           |             |                 | 
   | 162 | 5   |     |         Compute process inner cells                       | 1       | 2.086     | 0.9741    | 27.95     | 253 | 0.03692   | 124 | 759    |           |             |                 | 
   | 163 | 6   |     |           Compute _V moments                              | 1       | 0.5466    | 26.2      | 8.406     | 253 | 0.004     | 204 | 759    |           |             |                 | 
   |     | 6   |     |           Other                                           | 1       | 1.54      | 73.8      | 20.01     | 307 | 0.03212   | 124 | 759    |           |             |                 | 
   | 164 | 5   | EG  |         Wait for receives                                 | 1       | 32.29     | 15.08     | 100.9     | 369 | 0.8707    | 29  | 759    |           |             |                 | 
   | 165 | 5   |     |         Compute process boundary cells                    | 1       | 1.429     | 0.667     | 14.67     | 253 | 0.04702   | 29  | 759    |           |             |                 | 
   | 166 | 6   |     |           Compute _V moments                              | 1       | 0.3795    | 26.57     | 4.489     | 253 | 0.003492  | 7   | 759    |           |             |                 | 
   |     | 6   |     |           Other                                           | 1       | 1.049     | 73.43     | 10.19     | 253 | 0.04324   | 29  | 759    |           |             |                 | 
   |     | 5   |     |         Other                                             | 1       | 16.63     | 7.766     | 54.55     | 398 | 0.9602    | 7   | 759    |           |             |                 | 
   | 170 | 4   |     |       fieldtracing-ionosphere-fsgridCoupling              | 1       | 2.399     | 0.02973   | 3.617     | 88  | 1.359     | 284 | 49     |           |             |                 | 
   | 171 | 4   |     |       ionosphere-mapDownMagnetosphere                     | 1       | 0.6545    | 0.008113  | 0.6979    | 421 | 0.6445    | 398 | 49     |           |             |                 | 
   | 172 | 4   |     |       ionosphere-calculateConductivityTensor              | 1       | 0.1307    | 0.00162   | 0.1341    | 234 | 0.13      | 96  | 49     |           |             |                 | 
   | 173 | 4   |     |       ionosphere-solve                                    | 1       | 240.4     | 2.98      | 250.5     | 416 | 236.1     | 58  | 49     |           |             |                 | 
   | 174 | 5   |     |         ionosphere-initSolver                             | 1       | 0.2439    | 0.1014    | 0.2703    | 427 | 0.2394    | 228 | 49     |           |             |                 | 
   |     | 5   |     |         Other                                             | 1       | 240.2     | 99.9      | 250.3     | 416 | 235.9     | 58  | 49     |           |             |                 | 
   |     | 4   |     |       Other                                               | 1       | 0.02644   | 0.0003277 | 0.105     | 374 | 0.01267   | 309 | 759    |           |             |                 | 
   | 167 | 3   |     |     Project endTimeStep                                   | 1       | 0.0009495 | 1.132e-05 | 0.002589  | 371 | 0.0006758 | 17  | 759    |           |             |                 | 
   | 168 | 3   |     |     compute-timestep                                      | 1       | 29.74     | 0.3545    | 29.84     | 94  | 29.39     | 371 | 758    |           |             |                 | 
   | 175 | 3   | D   |     Balancing load                                        | 1       | 124.4     | 1.483     | 137.3     | 498 | 104.1     | 51  | 38     |           |             |                 | 
   | 176 | 4   |     |       deallocate boundary data                            | 1       | 0.9602    | 0.7719    | 1.997     | 28  | 0.4402    | 187 | 38     |           |             |                 | 
   | 177 | 4   |     |       dccrg.initialize_balance_load                       | 1       | 3.131     | 2.517     | 3.744     | 395 | 2.197     | 28  | 38     |           |             |                 | 
   | 178 | 4   |     |       Data transfers                                      | 1       | 13.69     | 11.01     | 16.1      | 141 | 11.93     | 474 | 38     |           |             |                 | 
   | 179 | 5   |     |         Preparing receives                                | 1       | 0.2315    | 1.691     | 2.429     | 195 | 0.02703   | 68  | 5440   | 1.082e+07 | 2.348e+04   | Spatial cells/s | 
   | 180 | 5   |     |         transfer_all_data                                 | 1       | 5.931     | 43.32     | 10.13     | 440 | 2.845     | 411 | 190    |           |             |                 | 
   |     | 5   |     |         Other                                             | 1       | 7.527     | 54.98     | 10.53     | 248 | 3.963     | 202 | 38     |           |             |                 | 
   | 181 | 4   |     |       dccrg.finish_balance_load                           | 1       | 30.99     | 24.91     | 77.35     | 371 | 14.49     | 271 | 38     |           |             |                 | 
   | 182 | 4   |     |       compute_amr_transfer_flags                          | 1       | 0.08713   | 0.07004   | 0.3571    | 371 | 0.01466   | 124 | 38     |           |             |                 | 
   | 183 | 4   |     |       update block lists                                  | 1       | 44.49     | 35.76     | 80.37     | 30  | 14.63     | 371 | 38     |           |             |                 | 
   | 184 | 5   | E   |         Velocity block list update                        | 1       | 41.15     | 92.5      | 76.77     | 30  | 10.89     | 278 | 38     |           |             |                 | 
   | 185 | 5   |     |         Preparing receives                                | 1       | 3.334     | 7.495     | 6.418     | 29  | 1.116     | 187 | 38     | 2.116e+07 | 4.589e+04   | SpatialCells/s  | 
   |     | 5   |     |         Other                                             | 1       | 0.0003724 | 0.0008372 | 0.005403  | 364 | 0.0002562 | 162 | 38     |           |             |                 | 
   | 186 | 4   |     |       update sysboundaries                                | 1       | 0.07129   | 0.05731   | 0.8916    | 371 | 0.0038    | 309 | 38     |           |             |                 | 
   | 187 | 5   |     |         updateSysBoundariesAfterLoadBalance               | 1       | 0.07104   | 99.64     | 0.8914    | 371 | 0.003696  | 309 | 38     |           |             |                 | 
   |     | 5   |     |         Other                                             | 1       | 0.0002579 | 0.3617    | 0.02458   | 247 | 9.585e-05 | 338 | 38     |           |             |                 | 
   | 188 | 4   |     |       Init solvers                                        | 1       | 2.258e-05 | 1.815e-05 | 0.0002023 | 285 | 1.138e-05 | 187 | 38     |           |             |                 | 
   | 189 | 4   |     |       set face neighbor ranks                             | 1       | 0.9661    | 0.7766    | 3.083     | 69  | 0.3416    | 274 | 38     |           |             |                 | 
   | 190 | 4   |     |       GetSeedIdsAndBuildPencils                           | 1       | 1.562     | 1.256     | 4.632     | 75  | 0.5381    | 192 | 38     |           |             |                 | 
   | 191 | 5   |     |         getSeedIds                                        | 1       | 0.2891    | 18.5      | 0.9359    | 247 | 0.09034   | 274 | 114    |           |             |                 | 
   | 192 | 5   |     |         buildPencils                                      | 1       | 1.262     | 80.8      | 3.842     | 75  | 0.4409    | 192 | 114    |           |             |                 | 
   | 193 | 6   |     |           check_ghost_cells                               | 1       | 0.008167  | 0.647     | 0.1068    | 14  | 0.001828  | 452 | 114    |           |             |                 | 
   |     | 6   |     |           Other                                           | 1       | 1.254     | 99.35     | 3.832     | 75  | 0.4389    | 192 | 114    |           |             |                 | 
   |     | 5   |     |         Other                                             | 1       | 0.01092   | 0.6987    | 0.05609   | 371 | 0.002525  | 128 | 38     |           |             |                 | 
   |     | 4   |     |       Other                                               | 1       | 28.45     | 22.87     | 54.78     | 177 | 1.772     | 352 | 38     |           |             |                 | 
   | 194 | 3   |     |     Shrink_to_fit                                         | 1       | 0.006649  | 7.925e-05 | 0.01907   | 395 | 0.003076  | 298 | 38     |           |             |                 | 
   | 195 | 3   |     |     ionosphere-updateIonosphereCommunicator               | 1       | 16.12     | 0.1922    | 36.39     | 51  | 3.218     | 498 | 38     |           |             |                 | 
   |     | 3   |     |     Other                                                 | 1       | 0.1116    | 0.00133   | 0.4158    | 371 | 0.04017   | 309 | 1      |           |             |                 | 
   | 438 | 2   |     |   Finalization                                            | 1       | 0.0001897 | 2.246e-06 | 0.01933   | 9   | 1.181e-05 | 208 | 1      |           |             |                 | 
   |     | 2   |     |   Other                                                   | 1       | 1.658e-05 | 1.963e-07 | 0.0006017 | 181 | 8.618e-06 | 50  | 1      |           |             |                 | 
   |     | 1   |     | Other                                                     | 1       | 0.08239   | 0.0009754 | 0.1725    | 352 | 0.002773  | 466 | 0      |           |             |                 | 
  ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


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

To begin with, we inspect the ``logfile.txt`` produced by the simulation run - at the end of a successful run, the file will show you total wall-clock runtime and some other counters - mark up these for the exercise results! The logfile is handy for surface-level checks, but for in-depth analysis of performance one should consult the phiprof outputs.

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


