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
