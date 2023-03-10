import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
import numpy as np
from networkx.algorithms.graphical import is_graphical
from networkx.utils.random_sequence import powerlaw_sequence

def sim_eraes(d,c,p,n,dd,iters):
    edge_lists = []
    G = nx.empty_graph(n)
    i = 0
    while i<iters:
        nodes = G.nodes()
        neighs = {u: list(G.neighbors(u)) for u in nodes}
        for u in nodes:
            deg = len(neighs[u])
            if deg < dd[u]:
                delta = [v for v in nodes if v != u]
                add_neighs = {random.choice(delta) for _ in range(dd[u]-deg)}
                for v in add_neighs:
                    G.add_edge(u,v)
            if deg > int(c*dd[u]):
                del_neighs = {random.choice(neighs[u]) for _ in range(deg - int(c*dd[u]))}
                for v in del_neighs:
                    if G.has_edge(u,v):
                        G.remove_edge(u,v)
        el = nx.generate_edgelist(G,data=False)
        edge_lists.append([])
        for line in el:
            edge_lists[i].append(line)
        i+=1
        for e in list(G.edges()):
                if (random.random() < p):
                    G.remove_edge(e[0], e[1])
        #G = step_evolution(G,d,c,p)
        el = nx.generate_edgelist(G,data=False)
        edge_lists.append([])
        for line in el:
            edge_lists[i].append(line)
        i+=1
    return edge_lists

def step_evolution(G,d,c,p):
    nodes = G.nodes()
    neighs = {u: list(G.neighbors(u)) for u in nodes}
    for u in nodes:
        deg = len(neighs[u])
        if deg < d:
            delta = [v for v in nodes if v != u]
            add_neighs = {random.choice(delta) for _ in range(d-deg)}
            for v in add_neighs:
                G.add_edge(u,v)
        if deg > c*d:
            del_neighs = {random.choice(neighs[u]) for _ in range(deg - int(c*d))}
            for v in del_neighs:
                if G.has_edge(u,v):
                    G.remove_edge(u,v)

    for e in list(G.edges()):
            if (random.random() < p):
                G.remove_edge(e[0], e[1])
    return G


if __name__ == '__main__':
    n = 64
    d = 4
    c = 1.5 
    p = 0.5
    iters = 400
    iterate = True
    gamma = 2.5
    dd = []
    while iterate:  # Continue generating sequences until one of them is graphical
        dd = sorted([int(round(d)) for d in powerlaw_sequence(n, gamma)], reverse=True)  # Round to nearest integer to obtain DISCRETE degree sequence
        if is_graphical(dd):
            iterate = False
    els = sim_eraes(d,c,p,n,dd,iters)
    temporal_el = []
    t = 1
    edges = []
    for elem in els:
        for line in elem:
            temporal_el.append([int(line.split(" ")[0]),int(line.split(" ")[1]),t])
            edges.append((int(line.split(" ")[0]),int(line.split(" ")[1])))
        t+=1
    edge_set = set(edges)
    time_dict = {}
    edge_index = {}
    i = 1
    for key in temporal_el:
        if ((key[0],key[1]) in time_dict):
            time_dict[(key[0],key[1])].append(key[2])
        else:
            time_dict[(key[0],key[1])]=[key[2]]
            edge_index[(key[0],key[1])] = i
            i+=1
    temporal_file = []
    for key in time_dict:
        timestart = 0
        actual_time = 0
        for i in range(0,len(time_dict[key])):
            if (i == 0):
                actual_time = time_dict[key][i]
                timestart = time_dict[key][i]
            else:
                if time_dict[key][i] == time_dict[key][i-1]+1:
                    actual_time = time_dict[key][i]
                else:
                    temporal_file.append([key[0],key[1],timestart,time_dict[key][i-1]])
                    timestart = time_dict[key][i]
                    actual_time = time_dict[key][i]
            if i == len(time_dict[key])-1 and time_dict[key][i] == time_dict[key][i-1]+1:
                    temporal_file.append([key[0],key[1],timestart,time_dict[key][i]])


    # write temporal edgelist

    with open('eraes_'+str(n)+"_"+str(p)+".csv", 'w+') as f:
        f.write("onset,terminus,tail,head,onset.censored,terminus.censored,edge.id\n")
        for tedge in temporal_file:
            f.write(str(tedge[2])+","+str(tedge[3])+","+str(tedge[1]+1)+","+str(tedge[0]+1)+",False,False,"+str(edge_index[(tedge[0],tedge[1])])+"\n")

    with open('eraes_edges_'+str(n)+"_"+str(p)+".csv", 'w+') as f:
        for key in edge_index.keys():
            f.write(str(key[0]+1)+","+str(key[1]+1)+"\n")


    print(temporal_el)
    print(time_dict)    

    print(temporal_file)