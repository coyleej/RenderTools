#!/bin/bash

#SBATCH --job-name=povray
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --time=10:00
#SBATCH --mem=8000
#SBATCH --partition=debug
#SBATCH --output=%x.o%j

srun python3 call_gif_POV.py 
