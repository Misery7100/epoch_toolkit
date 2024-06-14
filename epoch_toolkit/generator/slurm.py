import os

# ----------------------- #


def generate_slurm_file(
    experiment_name: str,
    experiment_path: str,
    nodes: int = 42,
    tasks_per_node: int = 7,
    cpus_per_task: int = 4,
    partition: str = "tornado",
    time: str = "72:00:00",
    cleanup: bool = False,
    compiler: str = "compiler/gcc/11",
    mpi: str = "mpi/openmpi/4.1.3/gcc/11",
    epoch_path: str = "~/magneto/epoch/epoch3d/bin/epoch3d",
):
    script_content = f"""#!/bin/bash

    #SBATCH --nodes={nodes}
    #SBATCH --tasks-per-node={tasks_per_node}
    #SBATCH --cpus-per-task={cpus_per_task}
    #SBATCH -p {partition}
    #SBATCH -t {time}
    #SBATCH -J epoch3d-job-{experiment_name}
    #SBATCH -o epoch3d-job-{experiment_name}.out
    #SBATCH -e epoch3d-job-{experiment_name}.err

    EXPERIMENT_PATH="{experiment_path}"
    CLEANUP={"true" if cleanup else "false"}

    module purge
    export OMPI_MCA_osc=ucx
    export OMPI_MCA_pml=pml
    export OMPI_MCA_btl=^openib

    if $CLEANUP; then
        rm -r $EXPERIMENT_PATH/*.sdf*
    fi

    module load {compiler}
    module load {mpi}

    echo $EXPERIMENT_PATH | mpirun -mca pml ob1 {epoch_path}
    """

    script_filename = f"{experiment_name}.slurm"
    script_filename = os.path.join(experiment_path, script_filename)

    with open(script_filename, "w") as script_file:
        script_file.write(script_content)
