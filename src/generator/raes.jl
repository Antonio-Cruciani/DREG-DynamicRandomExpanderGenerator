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
    new_edges::Set{Tuple{Int64,Int64}} = Set{Tuple{Int64,Int64}}([])
    degree_array::Array{Int64} = degree(g)
    all_neigs::Array{} = Array{Int64}([])
    indices::Array{Int64} = Array{Int64}([])
    
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
    # Update the graph structures
    for e in new_edges
        a = add_edge!(g,e[1],e[2])
        b = rem_edge!(gc,e[1],e[2])
        if (!a || !b)
            println(" Phase 1 : Error : add_edge "*string(a)*" rem_edge "*strign(b))
            exit(1)
        end
    end
    return nothing
end


function _phase_2!(g::SimpleGraph,gc::SimpleGraph,cd::Int64,newborn::Int64 = 0)
    rem_edges::Set{Tuple{Int64,Int64}} = Set{Tuple{Int64,Int64}}([])
    degree_array::Array{Int64} = degree(g)
    all_neigs::Array{} = Array{Int64}([])
    indices::Array{Int64} = Array{Int64}([])
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
    # Update the graph structures
    for e in rem_edges
        a = rem_edge!(g,e[1],e[2])
        b = add_edge!(gc,e[1],e[2])
        if (!a || !b)
            println(" Phase 2 : Error : rem_edge "*string(a)*" add_edge "*string(b))
            exit(1)
        end
    end
    return nothing
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
    return nothing
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
