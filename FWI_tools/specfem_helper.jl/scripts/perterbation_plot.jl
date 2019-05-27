include("../src/utils/readfiles.jl")
import PyPlot
const plt = PyPlot

function get_perterbation_1(tag::String)
    tao_basedir = "/work/05880/tg851791/stampede2/model/FWEA18_smooth"
    s362ani_basedir = "/work/05880/tg851791/stampede2/specfem/20190115/tao_h_files/DATABASES_MPI"

    nproc = 336
    nspec = 4960
    tao_gll = zeros(Float64, NGLLX, NGLLY, NGLLZ, nspec, nproc)
    s362ani_gll = zeros(Float64, NGLLX, NGLLY, NGLLZ, nspec, nproc)
    dummy = zeros(Float64, NGLLX, NGLLY, NGLLZ, nspec)

    for iproc in 0:nproc - 1
        sem_io_read_gll_file_1!(tao_basedir, iproc, tag, dummy)
        tao_gll[:,:,:,:,iproc + 1] = dummy
        sem_io_read_gll_file_1!(s362ani_basedir, iproc, tag, dummy)
        s362ani_gll[:,:,:,:,iproc + 1] = dummy
    end
    return (tao_gll .- s362ani_gll) ./ s362ani_gll
end

function plot()
    tags = ["vpv","vph","vsv","vsh"]
    fig = plt.figure(figsize = (20, 8))
    for tag in tags
        data = get_perterbation_1(tag)
        plotdata = reshape(data, reduce(*, size(data)))
        plt.hist(plotdata, bins = 50, histtype = "stepfilled")
        plt.xlabel("perterbation")
        plt.ylabel("number")
        plt.title(tag)
        plt.savefig("./$(tag).eps")
        plt.clf()
    end
end
