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


function edge_dynamic_d_regular_graph(n::Int64,d::Int64,c::Float64,p::Float64,max_iter::Int64 = 100,verbose::Int64 = 0,persist_snapshots::Bool = false,starting_graph = nothing)
    g::SimpleGraph = SimpleGraph()
    cd::Int64 = trunc(Int64,c*d)
    s_graph::String = ""
    round::Int64 = 0
    execution_time::Array{Array{Float64}} = Array{Array{Float64}}([])
    start_time::Float64 = 0.0
    # Index for each phase
    snapshots::Array{Array{SimpleGraph}} = Array{Array{SimpleGraph}}([])
    for _ in 1:3
        push!(snapshots,[])
        push!(execution_time,[])
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
    start_time = time()
    while (!has_to_stop(degree(g),d,cd,p,round,max_iter))
        g,gc = _phase_1!(g,gc,d)
        push!(execution_time[1],time()-start_time)
        if persist_snapshots
            push!(snapshots[1],copy(g))
        end
        #degs = degree(g)
        #println("Degree: AVG "*string(mean(degs))* " STD "*string(std(degs))*" Minimum "*string(minimum(degs))*" Maximum "*string(maximum(degs)))
        g,gc =_phase_2!(g,gc,cd)
        push!(execution_time[2],time()-start_time)
        if persist_snapshots
            push!(snapshots[2],copy(g))
        end
        #degs = degree(g)
        #println("Degree: AVG "*string(mean(degs))* " STD "*string(std(degs))*" Minimum "*string(minimum(degs))*" Maximum "*string(maximum(degs)))
        if (p > 0)
            g,gc = _phase_3!(g,gc,p)
           push!(execution_time[3],time()-start_time)
            if persist_snapshots
                push!(snapshots[3],copy(g))
            end
        end
        round += 1
        if verbose > 0 && round % verbose == 0
            println("Round t "*string(round)*"/"*string(max_iter))
            avg_ph_1 = string((mean(execution_time[1])))
            avg_ph_2 = string((mean(execution_time[2])))
            avg_ph_3 = string((mean(execution_time[3])))
            degs = degree(g)
            println("Degree: AVG "*string(mean(degs))* " STD "*string(std(degs))*" Minimum "*string(minimum(degs))*"(Target "*string(d)*") Maximum "*string(maximum(degs))*" (Target "*string(cd)*")")
            if (p > 0)
                println("Average times. Phase 1 : "*avg_ph_1*" Phase 2 : "*avg_ph_2*" Phase 3 : "*avg_ph_3)
            else
                println("Average times. Phase 1 : "*avg_ph_1*" Phase 2 : "*avg_ph_2)
            end
            flush(stdout)
        end
    end
    return g,round,snapshots,time()-start_time,execution_time
end



function vertex_dynamic_d_regular_graph(n::Int64,d::Int64,c::Float64,λ::Float64,p::Float64,max_iter::Int64 = 100,verbose::Int64 = 0,persist_snapshots::Bool = false,starting_graph = nothing)::Tuple{SimpleGraph,Int64,Array{Array{SimpleGraph}}}
    g::SimpleGraph = SimpleGraph()
    cd::Int64 = trunc(Int64,c*d)
    s_graph::String = ""
    round::Int64 = 0
    # Index for each phase
    snapshots::Array{Array{SimpleGraph}} = Array{Array{SimpleGraph}}([])
    for _ in 1:4
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
    println("Edge Dynamic Random Graph\nStarting Configuration : "*s_graph*"\nNumber of nodes : "*string(n)*"\nTarget degree : "*string(d)*"\nSlack constant c : "*string(c)*" | Slack c⋅d : "*string(cd)*"\nPoisson Process Rate (joining rate) : "*string(λ)*"\nNode disappearance probability q : "*string(p)*"\nMaximum number of iterations : "*string(max_iter))
    println("----------------------------------------------------------------")
    flush(stdout)
    prev_n::Int64 = nv(g)
    while (!has_to_stop(degree(g),d,cd,p,round,max_iter))
        prev_n = nv(g)
        _phase_0!(g,gc,d,λ)
        if persist_snapshots
            push!(snapshots[1],copy(g))
        end
        _phase_1!(g,gc,d,nv(g)-prev_n)
        if persist_snapshots
            push!(snapshots[2],copy(g))
        end
        _phase_2!(g,gc,cd,nv(g)-prev_n)
        if persist_snapshots
            push!(snapshots[3],copy(g))
        end
        if (p > 0)
           _phase_4!(g,gc,p)
            if persist_snapshots
                push!(snapshots[4],copy(g))
            end
        end
        round += 1
        if verbose > 0 && round % verbose == 0
            println("Round t "*string(round)*"/"*string(max_iter))
            flush(stdout)
        end
    end
    return g,round,snapshots
end