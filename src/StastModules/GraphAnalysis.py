import networkx as nx
import numpy as np
import math as mt

def get_graph_properties(G,d,c):
    if(len(G)>0):
        # Number of nodes
        n = len(list(G.nodes()))
        # Calculating the avg degree of the Graph
        s = 0
        for key, val in G.degree:
            s += val
        avg_deg = 2 * s / n
        # Calculating the Standard Deviation
        app = 0
        for key, val in G.degree:
            app += mt.pow((val - avg_deg), 2)
        stdv = mt.sqrt(app / n)
        # Calculating the Variance
        var = app / n

        # Getting the number of the vertices with less than d neighbours
        # Number of the nodes with a degree >=d and <= cd
        semireg = 0
        # Number of nodes with a degree <d
        underreg = 0
        # Number of nodes with a degree >cd
        overreg = 0
        # Volume of the Graph
        vol = 0

        for u in list(G.nodes()):
            if (G.degree(u) < d):
                underreg += 1
            elif (G.degree(u) > c * d):
                overreg += 1
            else:
                semireg += 1
            vol += G.degree(u)

        # Getting Radius and Diameter of the Graph
        if(nx.is_connected(G)):
            diameter = nx.diameter(G)
            radius = nx.radius(G)
        else:
            diameter = "Null"
            radius =  "Null"
    else:
        n=0
        avg_deg ="NULL"
        stdv = "NULL"
        var = "NULL"
        semireg = "NULL"
        underreg = "NULL"
        overreg = "NULL"
        vol = "NULL"
        diameter ="NULL"
        radius = "NULL"
    return(n,avg_deg,stdv,var,semireg,underreg,overreg,vol,diameter,radius)


def get_graph_properties_ND(G,d,c):
    if(len(G)>0):
        # Number of nodes
        n = len(list(G.nodes()))
        # Calculating the avg degree of the Graph
        s = 0
        for key, val in G.degree:
            s += val
        avg_deg = 2 * s / n
        # Calculating the Standard Deviation
        app = 0
        for key, val in G.degree:
            app += mt.pow((val - avg_deg), 2)
        stdv = mt.sqrt(app / n)
        # Calculating the Variance
        var = app / n

        # Getting the number of the vertices with less than d neighbours
        # Number of the nodes with a degree >=d and <= cd
        semireg = 0
        # Number of nodes with a degree <d
        underreg = 0
        # Number of nodes with a degree >cd
        overreg = 0
        # Volume of the Graph
        vol = 0

        for u in list(G.nodes()):
            if (G.degree(u) < d):
                underreg += 1
            elif (G.degree(u) > c * d):
                overreg += 1
            else:
                semireg += 1
            vol += G.degree(u)


    else:
        n=0
        avg_deg ="NULL"
        stdv = "NULL"
        var = "NULL"
        semireg = "NULL"
        underreg = "NULL"
        overreg = "NULL"
        vol = "NULL"

    return(n,avg_deg,stdv,var,semireg,underreg,overreg,vol)
