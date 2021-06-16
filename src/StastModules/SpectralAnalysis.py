import networkx as nx
import numpy as np
import math as mt
import cupy as cp
import scipy as sp

# Function that return the spectral Gap of the Transition Matrix P
def get_spectral_gap_transition_matrix(G):
    Isinvertible = False
    if(len(G)>0):
        # Checking if the Diagonal Degree Matrix is invertible
        nodes_degrees = G.degree
        c = 0
        for i in nodes_degrees:

            if (i[1]==0):
                c+=1
        # If is invertible
        if(c==0):
            Isinvertible = True
            # Calculating the sparse Adj Matrix
            A= nx.to_numpy_matrix(G)
            # Calculating the sparse Degree Diagonal Matrix
            n, m = A.shape
            diags = A.sum(axis=1).flatten()
            # Inverting D
            invDiags = []
            for i in diags:
                invDiags.append(1/i)
            I = np.identity(n)
            invD = invDiags*I
            # Getting the Transition Matrix

            #P =  invD* A
            cpInvD = cp.asarray(invD)
            cpA = cp.asarray(A)

            P = cp.matmul(cpInvD,cpA)
            #check = P.sum(axis=1).flatten()
            # Getting the spectral gap of P
            #spectrumP = np.linalg.eigvals(P)
            spectrumP,v = cp.linalg.eigh(P)
            cp.cuda.Stream.null.synchronize()

            # The first eigenvalue of the transition matrix is always 1
            #lamba1 = 1

            # Getting the second Eigenvalue
            #ordered_spectrum = sorted(spectrumP,reverse = True)
            ordered_spectrum = cp.sort(spectrumP[0])
            lamba1 = ordered_spectrum[-1]
            #lambda2 =ordered_spectrum[1]
            #lambda_n = ordered_spectrum[-1]
            #lambda_n_1 = ordered_spectrum[-2]
            lambda2 = ordered_spectrum[-2]
            if (np.iscomplex(lambda2)):
                lambda2 = lambda2.real
            spectralGap = float(lamba1 - lambda2)
            # Getting the n-th Eigenvalue
            lambdaN = ordered_spectrum[-2]
            lambdaNGap = ordered_spectrum[-1] - lambdaN
            if isinstance(spectralGap, complex):
                return(Isinvertible,0,0)
            return (Isinvertible,spectralGap, lambdaNGap)
    return(Isinvertible,0,0)


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
