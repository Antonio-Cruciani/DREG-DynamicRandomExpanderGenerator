import networkx as nx
import numpy as np
import math as mt
import scipy as sp



def spectral_gap_sparse(G):
    if (not nx.is_empty(G)):
        if (nx.is_connected(G)):
            d = []
            # start = time.time()

            for elem in list(G.nodes):
                deg = len(list(G.neighbors(elem)))
                d.append(1 / deg)

            Aa100 = nx.to_scipy_sparse_matrix(G)
            invD = np.diag(d)
            n = len(d)
            out = sp.sparse.csr_matrix(invD)
            P = out * Aa100


            if (len(G.nodes()) > 2):
                spettro = sp.sparse.linalg.eigsh(P, k=2, which="LA", return_eigenvectors=False)

                spettro = sorted(spettro, reverse=True)
                sg = spettro[0] - spettro[1]
            else:
                sg = 0
        else:
            sg = 0
    else:
        sg = 0

    sg_trans = float(sg)
    return (sg_trans)


def spectral_gap(G):
    if (not nx.is_empty(G)):
        if (nx.is_connected(G)):
            d = []
            # start = time.time()

            for elem in list(G.nodes):
                deg = len(list(G.neighbors(elem)))
                d.append(1 / deg)

            Aa100 = nx.to_scipy_sparse_matrix(G)
            # Aa100 = nx.adjacency_matrix(G)
            invD = np.diag(d)
            n = len(d)
            out = sp.sparse.csr_matrix(invD)
            P = out * Aa100

            # P = invD*Aa100
            # print(type(P))

            # m = len(P[0])
            # print("NODI : ", len(G.nodes()))
            if (len(G.nodes()) > 2):
                spettro = sp.sparse.linalg.eigsh(P, k=2, which="LA", return_eigenvectors=False)

                # print("SPETTRO=",spettro)
                # print("n = ",n," TIME ",time.time()-start)

                spettro = sorted(spettro, reverse=True)
                # print("L1",spettro[0])
                # print("L2",spettro[1])
                sg = spettro[0] - spettro[1]
            else:
                sg = 0
        else:
            sg = 0
    else:
        sg = 0
    # print("TEMPO IMPIEGATO ",time.time()-start, "NUMERO NODI: ",len(G.nodes))
    # print(float(sg))
    sg_trans = float(sg)

    return (sg_trans)