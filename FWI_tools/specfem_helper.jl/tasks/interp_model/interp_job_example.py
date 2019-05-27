from slurmpy import Slurm

# * background+tao/crust1.0 -> background+tao/crust1.0 -> background+tao/crust1.0+min/crust2.0
print("start job 4")
nproc_old = 336
old_mesh_dir = "/work/05880/tg851791/stampede2/specfem/20190115/tao_h_files/DATABASES_MPI"
old_model_dir = "/scratch/05880/tg851791/binfile/perturbation/tao_perturbation_smooth"
nproc_new = 441
new_mesh_dir = "/work/05880/tg851791/stampede2/specfem/20190115/simulation_taoreg/DATABASES_MPI"
new_model_dir = "/scratch/05880/tg851791/binfile/interp/s362ani_addmin-pert"
model_tags = ",".join(["vph", "vpv", "vsh", "vsv", "eta", "qmu", "rho"])
output_dir = "/scratch/05880/tg851791/binfile/interp/s362ani_addmin_addtao-pert"

command4 = f"ibrun julia src/program/xsem_interp_mesh2.jl --nproc_old {nproc_old} --old_mesh_dir {old_mesh_dir} --old_model_dir {old_model_dir} --nproc_new {nproc_new} --new_mesh_dir {new_mesh_dir} --new_model_dir {new_model_dir} --model_tags {model_tags} --output_dir {output_dir}"
s4 = Slurm("bg+tao", {"partition": "skx-normal",
                      "nodes": 10, "ntasks": 441, "time": "00:60:00"})
jobid_s4 = s4.run(command4)
