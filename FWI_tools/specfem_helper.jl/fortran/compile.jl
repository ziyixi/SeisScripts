files = ["gll_library.f90","sem_mesh_mod.f90"]
FF = "gfortran"

for file in files
    fname = join(split(file, ".")[1:end - 1], ".")
    command = `$(FF) -fPIC -shared ./src/$(fname).f90 -o ./lib/$(fname).so`
    run(command)
end