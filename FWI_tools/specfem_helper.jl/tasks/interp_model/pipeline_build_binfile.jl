include("../scripts/perturbation_bin_file.jl")

function generate_tao_perturbation()
    url_reference_without_correctcrust = "/work/05880/tg851791/stampede2/specfem/20190115/tao_h_files/DATABASES_MPI"
    url_tao_binfile_smooth = "/work/05880/tg851791/stampede2/model/FWEA18_smooth"
    url_output = "/scratch/05880/tg851791/binfile/perturbation/tao_perturbation_smooth"
    nproc = 336
    nspec = 4960
    generate_perturbation(url_tao_binfile_smooth, url_reference_without_correctcrust, url_output, nproc, nspec)
end

function generate_min_perturbation()
    url_reference_without_correctcrust = "/work/05880/tg851791/stampede2/specfem/20190115/min_h_files/DATABASES_MPI"
    url_min_binfile = "/work/05880/tg851791/stampede2/model/EARA2014"
    url_output = "/scratch/05880/tg851791/binfile/perturbation/min_perturbation"
    nproc = 144
    nspec = 7236
    generate_perturbation(url_min_binfile, url_reference_without_correctcrust, url_output, nproc, nspec)
end

function generate_my_perturbation()
    url_reference_with_correctcrust = "/work/05880/tg851791/stampede2/specfem/20190115/simulation_taoreg/DATABASES_MPI"
    url_background_binfile = "/work/05880/tg851791/stampede2/specfem/20190115/simulation_taoreg/DATABASES_MPI"
    url_output = "/scratch/05880/tg851791/binfile/perturbation/background_perturbation"
    nproc = 441
    nspec = 4480
    generate_perturbation(url_background_binfile, url_reference_with_correctcrust, url_output, nproc, nspec)
end

function recover_tao()
    url_reference_with_correctcrust = "/work/05880/tg851791/stampede2/specfem/20190115/simulation_taoreg/DATABASES_MPI"
    url_tao_perturbation = "/scratch/05880/tg851791/binfile/interp/s362ani_addtao-pert"
    url_output = "/scratch/05880/tg851791/binfile/gll/bg-tao"
    nproc = 441
    nspec = 4480
    generate_real(url_tao_perturbation, url_reference_with_correctcrust, url_output, nproc, nspec)
end

function recover_tao_min()
    url_reference_with_correctcrust = "/work/05880/tg851791/stampede2/specfem/20190115/simulation_taoreg/DATABASES_MPI"
    url_min_perturbation = "/scratch/05880/tg851791/binfile/interp/s362ani_addtao_addmin-pert"
    url_output = "/scratch/05880/tg851791/binfile/gll/bg-tao-min"
    nproc = 441
    nspec = 4480
    generate_real(url_min_perturbation, url_reference_with_correctcrust, url_output, nproc, nspec)
end

function recover_min()
    url_reference_with_correctcrust = "/work/05880/tg851791/stampede2/specfem/20190115/simulation_taoreg/DATABASES_MPI"
    url_min_perturbation = "/scratch/05880/tg851791/binfile/interp/s362ani_addmin-pert"
    url_output = "/scratch/05880/tg851791/binfile/gll/bg-min"
    nproc = 441
    nspec = 4480
    generate_real(url_min_perturbation, url_reference_with_correctcrust, url_output, nproc, nspec)
end

function recover_min_tao()
    url_reference_with_correctcrust = "/work/05880/tg851791/stampede2/specfem/20190115/simulation_taoreg/DATABASES_MPI"
    url_min_perturbation = "/scratch/05880/tg851791/binfile/interp/s362ani_addmin_addtao-pert"
    url_output = "/scratch/05880/tg851791/binfile/gll/bg-min-tao"
    nproc = 441
    nspec = 4480
    generate_real(url_min_perturbation, url_reference_with_correctcrust, url_output, nproc, nspec)
end