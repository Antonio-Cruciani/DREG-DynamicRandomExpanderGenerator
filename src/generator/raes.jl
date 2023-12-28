

function _phase_1!(g::SimpleGraph,gc::SimpleGraph,d::Int64)
    new_edges::Set{Tuple{Int64,Int64}} = Set{Tuple{Int64,Int64}}([])
    degree_array::Array{Int64} = degree(g)
    all_neigs::Array{} = Array{Int64}([])
    indices::Array{Int64} = Array{Int64}([])
    for u in 1:nv(g)
        # If node u has degree less than the target d
        if degree_array[u] < d
            # Get all the candidates from the complement graph 
            all_neigs = all_neighbors(gc, u)
            # Sample a subset of new neighbors
            indices = sample(1:length(all_neigs),d-degree_array[u],replace=true)
            for i in indices
                push!(new_edges,(min(u,all_neigs[i]),max(u,all_neigs[i])))
            end
        end
    end
    # Update the graph structures
    for e in new_edges
        a = add_edge!(g,e[1],e[2])
        b = rem_edge!(gc,e[1],e[2])
        if (!a || !b)
            println(" Error : add_edge "*a*" rem_edge "*b)
            exit(1)
        end
    end
    return nothing
end


function _phase_2!(g::SimpleGraph,gc::SimpleGraph,cd::Int64)
    rem_edges::Set{Tuple{Int64,Int64}} = Set{Tuple{Int64,Int64}}([])
    degree_array::Array{Int64} = degree(g)
    all_neigs::Array{} = Array{Int64}([])
    indices::Array{Int64} = Array{Int64}([])
    for u in 1:nv(g)
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
            println(" Error : rem_edge "*a*" add_edge "*b)
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
            println(" Error : rem_edge "*a*" add_edge "*b)
            exit(1)
        end
    end
    return nothing
end



