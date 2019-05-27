include("../src/utils/readfiles.jl")

function get_difference_1(basedir1::String, basedir2::String, tag::String)
    nproc = 441
    nspec = 4480
    me_gll = zeros(Float64, NGLLX, NGLLY, NGLLZ, nspec, nproc)
    s362ani_gll = zeros(Float64, NGLLX, NGLLY, NGLLZ, nspec, nproc)
    dummy = zeros(Float64, NGLLX, NGLLY, NGLLZ, nspec)

    for iproc in 0:nproc - 1
        sem_io_read_gll_file_1!(basedir1, iproc, tag, dummy)
        me_gll[:,:,:,:,iproc + 1] = dummy
        sem_io_read_gll_file_1!(basedir2, iproc, tag, dummy)
        s362ani_gll[:,:,:,:,iproc + 1] = dummy
    end
    return s362ani_gll - me_gll, s362ani_gll, me_gll
end
