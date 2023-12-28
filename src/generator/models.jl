function has_to_stop(degrees::Array{Int64},d::Int64,cd::Int64,p::Float64,round::Int64,max_iter::Int64)::Bool
    if (p > 0 && round >= max_iter)
        return true
    elseif (p == 0)
        for i in 1:lastindex(degrees)
            if (degrees[i] > cd || degrees[i] < d)
                return false
            end
        end
        return true
    end
    return false
end


function edge_dynamic_d_regular_graph(n::Int64,d::Int64,c::Float64,p::Float64,max_iter::Int64 = 100,persist_snapshots::Bool = false,starting_graph = nothing)::Tuple{SimpleGraph,Int64,Array{Array{SimpleGraph}}}
    g::SimpleGraph = SimpleGraph()
    cd::Int64 = trunc(Int64,c*d)
    s_graph::String = ""
    round::Int64 = 0
    # Index for each phase
    snapshots::Array{Array{SimpleGraph}} = Array{Array{SimpleGraph}}([])
    for _ in 1:3
        push!(snapshots,[])
    end
    if (isnothing(starting_graph))
        g = SimpleGraph(n)
        s_graph = "Empty"
    else
        g = starting_graph
        s_graph = "Custom"
        n = nv(g)
    end
    gc::SimpleGraph = complement(g)
    println("----------------------------------------------------------------")
    println("Edge Dynamic Random Graph\nStarting Configuration : "*s_graph*"\nNumber of nodes : "*string(n)*"\nTarget degree : "*string(d)*"\nSlack constant c : "*string(c)*" | Slack c⋅d : "*string(cd)*"\nEdge disappearance probability p : "*string(p)*"\nMaximum number of iterations : "*string(max_iter))
    println("----------------------------------------------------------------")
    flush(stdout)
    while (!has_to_stop(degree(g),d,cd,p,round,max_iter))
        _phase_1!(g,gc,d)
        if persist_snapshots
            push!(snapshots[1],copy(g))
        end
        _phase_2!(g,gc,cd)
        if persist_snapshots
            push!(snapshots[2],copy(g))
        end
        if (p > 0)
           _phase_3!(g,gc,p)
            if persist_snapshots
                push!(snapshots[3],copy(g))
            end
        end
        round += 1
        println("Round t "*string(round)*"/"*string(max_iter))
        flush(stdout)
    end
    return g,round,snapshots
end