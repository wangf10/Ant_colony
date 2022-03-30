#! /bin/bash
#SBATCH --nodes=4
#SBATCH --job-name=test_mpi2
#SBATCH --partition=cpu_prod
#SBATCH --time=02:00:00
#SBATCH --qos=16nodespu
#SBATCH --exclusive
#SBATCH --ntasks 128

mpirun -np 4 -ppn 1 --bind-to socket python /usr/users/cpust75/cpust75_6/Ant_colony/antcolony_mpi.py --config benchmark_30_01.json


