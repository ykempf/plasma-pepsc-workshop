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

