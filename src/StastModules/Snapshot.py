from src.StastModules.GraphAnalysis import get_graph_properties,get_graph_properties_ND
from src.StastModules.SpectralAnalysis import get_spectral_gap_transition_matrix

import numpy as np
def get_snapshot_dynamic(G,d,c,t):

    #IsInvertible,spectralGap, lambdaNGap = get_spectral_gap_transition_matrix(G.get_G())
    n, avg_deg, stdv, var, semireg, underreg, overreg, vol,diameter,radius = get_graph_properties(G.get_G(),d,c)
    # Creating Dictionary with all the informations
    if (G.isregular()):
        regularity = False
    else:
        regularity = True
    #if np.iscomplexobj(spectralGap):
    #    spectralGap =  abs(spectralGap)
    #if np.iscomplexobj(lambdaNGap):
    #    lambdaNGap =  abs(lambdaNGap)
    dict = {
        "n":n,
        "target_n":G.get_target_n(),
        "d":G.get_d(),
        "c":G.get_c(),
        "p":G.get_p(),
        "avg_deg":avg_deg,
        "stdv":stdv,
        "var":var,
        "semireg":semireg,
        "underreg":underreg,
        "overreg":overreg,
        "vol":vol,
        "diameter":diameter,
        "radius":radius,
        "regularity":regularity,
        "lambda": G.get_inrate(),
        "beta":G.get_outrate(),
        "model_type":G.get_type_of_dynamic_graph(),
        "entering_nodes":G.get_number_of_entering_nodes_at_each_round()[-1],
        "exiting_nodes":G.get_number_of_exiting_nodes_at_each_round()[-1],
        "t":t

    }



    return (dict)

def get_snapshot_dynamicND(G,d,c,t):

    #IsInvertible,spectralGap, lambdaNGap = get_spectral_gap_transition_matrix(G.get_G())
    n, avg_deg, stdv, var, semireg, underreg, overreg, vol = get_graph_properties_ND(G.get_G(),d,c)
    # Creating Dictionary with all the informations
    if (G.isregular()):
        regularity = False
    else:
        regularity = True
    #if np.iscomplexobj(spectralGap):
    #    spectralGap =  abs(spectralGap)
    #if np.iscomplexobj(lambdaNGap):
    #    lambdaNGap =  abs(lambdaNGap)
    dict = {
        "n":n,
        "target_n":G.get_target_n(),
        "d":G.get_d(),
        "c":G.get_c(),
        "p":G.get_p(),
        "avg_deg":avg_deg,
        "stdv":stdv,
        "var":var,
        "semireg":semireg,
        "underreg":underreg,
        "overreg":overreg,
        "vol":vol,
        "regularity":regularity,
        "lambda": G.get_inrate(),
        "beta":G.get_outrate(),
        "model_type":G.get_type_of_dynamic_graph(),
        "entering_nodes":G.get_number_of_entering_nodes_at_each_round()[-1],
        "exiting_nodes":G.get_number_of_exiting_nodes_at_each_round()[-1],
        "t":t

    }



    return (dict)

def get_snapshot(G,p,d,c,t,n_in=None,n_out=None):


    IsInvertible,spectralGap, lambdaNGap = get_spectral_gap_transition_matrix(G.get_G())
    n, avg_deg, stdv, var, semireg, underreg, overreg, vol,diameter,radius = get_graph_properties(G.get_G(),d,c)
    # Creating Dictionary with all the informations
    if (G.isregular()):
        regularity = False
    else:
        regularity = True
    dic={
        "spectralGap": spectralGap,
        "lambdaNGap":lambdaNGap,
        "p":p,
        "n":n,
        "d":d,
        "c":c,
        "avg_deg":avg_deg,
        "stdv":stdv,
        "var":var,
        "semiReg":semireg,
        "underReg": underreg,
        "overReg": overreg,
        "volume":vol,
        "diameter":diameter,
        "radius":radius,
        "Regular":regularity,
        "t":t
    }
    if(n_in != None and n_out != None):
        dic["EnteringNodes"] = n_in
        dic["ExitingNodes"] = n_out
    return (dic)