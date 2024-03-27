function _reduce_arrays!(s::Vector{Array{Tuple{Int64,Int64}}},t::Array{Tuple{Int64,Int64}})

    for i in 1:lastindex(s)
        for j in 1:lastindex(s[i])
            append!(t,[s[i][j]])
        end
    end
    return nothing
end


function _phase_0!(g::SimpleGraph,gc::SimpleGraph,d::Int64,λ::Float64)
    X_new::Int64 = rand(Poisson(λ))
    node_map::Dict{Tuple{Int64,Int64},Int8} = Dict{Tuple{Int64,Int64},Int8}()
    new_edges::Set{Tuple{Int64,Int64}} = Set{Tuple{Int64,Int64}}([])
    prev_n::Int64 = nv(g)
    v_index::Int64 = 0
    if X_new > 0
        for _ in 1:X_new
            add_vertex!(g)
            add_vertex!(gc)
        end
        if prev_n > 0
            for v in 1:X_new
                v_index = prev_n + v
                for u in sample(1:prev_n,d,replace=true)
                    push!(new_edges,(min(u,v_index),max(u,v_index)))
                    node_map[(min(u,v_index),max(u,v_index))] = 1
                end
            end
        end
        # Update the graph structures
        for e in new_edges
            a = add_edge!(g,e[1],e[2])
            if !a
                println(" Phase 0 : Error : add_edge "*string(a)*" Edge : "*string(e))
                exit(1)
            end
        end
        for v in 1:X_new
            v_index = prev_n + v
            for u in 1:nv(g)
                if u != v_index
                    if !haskey(node_map,(min(u,v_index),max(u,v_index)))
                        a = add_edge!(gc,min(u,v_index),max(u,v_index))
                        node_map[(min(u,v_index),max(u,v_index))] = 1
                        if !a
                            println(" Phase 0 : Error : add_edge "*string(a))
                            exit(1)
                        end
                    end
                end
            end
        end
    end
    return nothing
end

function _phase_1!(g::SimpleGraph,gc::SimpleGraph,d::Int64,newborn::Int64 = 0)
    #new_edges::Set{Tuple{Int64,Int64}} = Set{Tuple{Int64,Int64}}([])
    new_edges::Array{Tuple{Int64,Int64}} = Array{Tuple{Int64,Int64}}([])
    degree_array::Array{Int64} = degree(g)
    
    vs_active = [i for i in 1:nv(g)-newborn]
    d, r = divrem(nv(g)-newborn, Threads.nthreads())
    ntasks = d == 0 ? r : Threads.nthreads()
    task_size = cld(nv(g), ntasks)
    local_new_edges::Vector{Array{Tuple{Int64,Int64}}} = [Array{Tuple{Int64,Int64}}([]) for _ in 1:ntasks]
    all_neigs::Array{Array{Int64}} = [Array{Int64}([]) for _ in 1:ntasks ]
    old_neigs::Array{Array{Int64}} = [Array{Int64}([]) for _ in 1:ntasks]
    indices::Array{Array{Int64}} = [Array{Int64}([]) for _ in 1:ntasks]
    println(task_size, " CIAO ")
    @sync for (t, task_range) in enumerate(Iterators.partition(1:(nv(g)-newborn), task_size))
        Threads.@spawn for u in @view(vs_active[task_range])
            all_neigs[t] = Array{Int64}([])
            old_neigs[t] = Array{Int64}([])
            indices[t] = Array{Int64}([])
            # If node u has degree less than the target d
            if degree_array[u] < d
                # Get all the candidates from the complement graph 
                all_neigs[t] = all_neighbors(gc, u)
                # Sample a subset of new neighbors
                old_neigs[t] = all_neigs[t][all_neigs[t] .<= nv(g)-newborn]
                if length(old_neigs[t]) > 0
                    for _ in 1:d-degree_array[u]
                        w = u
                        while w == u
                            w = sample(1:length(old_neigs[t]))
                        end
                        push!(indices[t],w)
                    end
                    #indices = sample(1:length(all_neigs[all_neigs .<= nv(g)-newborn]),d-degree_array[u],replace=true)
                    for i in indices[t]
                        push!(local_new_edges[t],(min(u,old_neigs[t][i]),max(u,old_neigs[t][i])))
                    end
                end
            end
        end
    end
    _reduce_arrays!(local_new_edges,new_edges)       

    #=
    for u in 1:(nv(g)-newborn)
        # If node u has degree less than the target d
        if degree_array[u] < d
            # Get all the candidates from the complement graph 
            all_neigs = all_neighbors(gc, u)
            # Sample a subset of new neighbors
            if length(all_neigs[all_neigs .<= nv(g)-newborn]) > 0
                indices = sample(1:length(all_neigs[all_neigs .<= nv(g)-newborn]),d-degree_array[u],replace=true)
                for i in indices
                    push!(new_edges,(min(u,all_neigs[i]),max(u,all_neigs[i])))
                end
            end
        end
    end
    =#
    

    # Update the graph structures
    for e in Set(new_edges)
        a = add_edge!(g,e[1],e[2])
        b = rem_edge!(gc,e[1],e[2])
        if (!a || !b)
            println(" Phase 1 : Error : add_edge "*string(a)*" rem_edge "*string(b))
            exit(1)
        end
    end
    return g,gc
end


function _phase_2!(g::SimpleGraph,gc::SimpleGraph,cd::Int64,newborn::Int64 = 0)
    rem_edges::Array{Tuple{Int64,Int64}} = Array{Tuple{Int64,Int64}}([])
    degree_array::Array{Int64} = degree(g)
    vs_active = [i for i in 1:nv(g)]
    d, r = divrem(nv(g), Threads.nthreads())
    ntasks = d == 0 ? r : Threads.nthreads()
    task_size = cld(nv(g), ntasks)
    local_rem_edges::Vector{Array{Tuple{Int64,Int64}}} = [Array{Tuple{Int64,Int64}}([]) for _ in 1:ntasks]
    all_neigs::Array{Array{Int64}} =[ Array{Int64}([]) for _ in 1:ntasks]
    indices::Array{Array{Int64}} = [Array{Int64}([]) for _ in 1:ntasks]
    @sync for (t, task_range) in enumerate(Iterators.partition(1:(nv(g)-newborn), task_size))
        Threads.@spawn for u in @view(vs_active[task_range])
            all_neigs[t] = Array{Int64}([])
            indices[t] = Array{Int64}([])
            # If node u has degree greater than the maximum tolerance c⋅d
            if degree_array[u] > cd
                # Get all the candidates from the graph 
                all_neigs[t] = all_neighbors(g, u)
                # Sample a subset of new neighbors
                for _ in 1:degree_array[u]-cd
                    w = u
                    while w == u
                        w = sample(1:length(all_neigs[t]))
                    end
                    push!(indices[t],w)
                end
                for i in indices[t]
                    push!(local_rem_edges[t],(min(u,all_neigs[t][i]),max(u,all_neigs[t][i])))
                end
            end
        end
    end
    _reduce_arrays!(local_rem_edges,rem_edges)       
  
    #=
    for u in 1:(nv(g)-newborn)
        # If node u has degree greater than the maximum tolerance c⋅d
        if degree_array[u] > cd
            # Get all the candidates from the graph 
            all_neigs = all_neighbors(g, u)
            # Sample a subset of new neighbors
            
            indices = sample(1:length(all_neigs),degree_array[u]-cd,replace=true)
           
            for i in indices
                push!(rem_edges,(min(u,all_neigs[i]),max(u,all_neigs[i])))
            end
        end
    end
    =#
    # Update the graph structures
    for e in Set(rem_edges)
        a = rem_edge!(g,e[1],e[2])
        b = add_edge!(gc,e[1],e[2])
        if (!a || !b)
            println(" Phase 2 : Error : rem_edge "*string(a)*" add_edge "*string(b))
            exit(1)
        end
    end
    return g,gc
end


function _phase_3!(g::SimpleGraph,gc::SimpleGraph,p::Float64)
    rem_edges::Set{Tuple{Int64,Int64}} = Set{Tuple{Int64,Int64}}([])
    for e in collect(edges(g))
        if (rand() < p)
            push!(rem_edges,(src(e),dst(e)))
        end
    end
    # Update the graph structures
    for e in rem_edges
        a = rem_edge!(g,e[1],e[2])
        b = add_edge!(gc,e[1],e[2])
        if (!a || !b)
            println(" Phase 3 : Error : rem_edge "*string(a)*" add_edge "*string(b))
            exit(1)
        end
    end
    return g,gc
end


function _phase_4!(g::SimpleGraph,gc::SimpleGraph,p::Float64)
    rem_nodes::Set{Int64} = Set{Int64}([])
    for u in 1:nv(g)
        if (rand() < p)
            push!(rem_nodes,u)
        end
    end
    # Update the graph structures
    for u in sort(collect(rem_nodes),rev=true)
        a = rem_vertex!(g,u)
        b = rem_vertex!(gc,u)
        if (!a || !b)
            println(" Phase 4 : Error : rem_node "*string(a)*" rem_node "*string(b))
            exit(1)
        end
    end
    return nothing
end
