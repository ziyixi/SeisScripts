using DelimitedFiles

"""
    modify the values of vp,vs,rho in Crust1.0 with the upper layer's value, so that we won't have smoothing error.
"""
function modify_sediments(basedir::String, tag::String)
    filename = joinpath(basedir, "crust1." * tag)
    data = readdlm(filename)
    for i in 1:size(data)[1]
        if (data[i,3] == 0. ) && (data[i,4] == 0.) && (data[i,5] == 0.)
            continue
        elseif (data[i,3] != 0. ) && (data[i,4] == 0.) && (data[i,5] == 0.)
            data[i,4] = data[i,3]
            data[i,5] = data[i,3]
        elseif (data[i,3] != 0. ) && (data[i,4] != 0.) && (data[i,5] == 0.)
            data[i,5] = data[i,4]
        elseif (data[i,3] != 0. ) && (data[i,4] != 0.) && (data[i,5] != 0.)
            continue
        else 
            @error "abnormal 0 points"
        end
    end

    filename_old = filename * ".old"
    run(`mv $(filename) $(filename_old)`)
    writedlm(filename, data)
end

function modify_sediments_all(basedir::String)
    tags = ["vp","vs","rho"]
    for tag in tags
        modify_sediments(basedir, tag)
    end
end