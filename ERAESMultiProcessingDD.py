import multiprocessing
from src.Graphs.Objects.MultipleEdge import DynamicGraph
from src.StastModules.Snapshot import get_snapshot,get_snapshot_dd
from src.FileOperations.WriteOnFile import create_file, create_folder, write_on_file_contents
import math as mt
import logging
import pandas as pd
import networkx as nx
#from src.tail_estimation_degree_distribution.tail-estimation.py import *
from networkx.algorithms.graphical import is_graphical
from networkx.utils.random_sequence import powerlaw_sequence

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)



def worker(data, return_dict):
    def flood():
        flood_dictionary = {}
        if (G.get_converged()):
            if (G.flooding.get_initiator() == -1):
                G.set_flooding()
                G.flooding.set_initiator()
                G.flooding.update_flooding(G)
                logging.info("Flooding Simulation : STARTED")
                # print("----- Flooding Simulation: STARTED -----\n")
            else:
                if (G.flooding.get_started() == True):
                    G.flooding.update_flooding(G)
                G.flooding.is_informed()
                if (G.flooding.get_converged()):
                    logging.info("ALL NODES IN THE NETWORK ARE INFORMED")
                    # print("--- ALL NODES IN THE NETWORK ARE INFORMED ---\n\n")
            flood_dictionary['informed_nodes'] = G.flooding.get_informed_nodes()
            flood_dictionary['uninformed_nodes'] = G.flooding.get_uninformed_nodes()
            flood_dictionary['t_flood'] = G.flooding.get_t_flood()
            flood_dictionary['process_status'] = G.get_converged()
            flood_dictionary['flood_status'] = G.flooding.get_converged()
            flood_dictionary['initiator'] = G.flooding.get_initiator()
        else:
            flood_dictionary['informed_nodes'] = 0
            flood_dictionary['uninformed_nodes'] = len(G.get_list_of_nodes())
            flood_dictionary['t_flood'] = 0
            flood_dictionary['process_status'] = G.get_converged()
            flood_dictionary['flood_status'] = G.flooding.get_converged()
            flood_dictionary['initiator'] = G.flooding.get_initiator()

        return (flood_dictionary)

    """worker function"""
    final_stats = []

    d = data["d"]
    c = data["c"]
    edge_falling_rate = data["edge_falling_rate"]
    dd = data["dd"]
    # sim = data["sim"]
    max_iter = data["max_iter"]
    G = DynamicGraph(n, d, c,falling_probability= edge_falling_rate,degree_sequence=dd)
    t = 0
    achieved = False
    repeat = True
    sim = {
        "simulation": data["sim"],
        "pl_exponend":data["gamma"]
    }
    while (repeat):



        G.add_phase_dd()
        G.del_phase_dd()
        if (edge_falling_rate != 0):
            G.random_fall()

        if (G.get_converged() == False):
            stats = get_snapshot_dd(G, edge_falling_rate, G.get_c(),dd, t)

        if (t == max_iter):
            G.set_converged(True)
            G.flooding.set_converged(False)

        if (G.get_converged()):
            if (nx.is_connected(G.get_G()) == False and edge_falling_rate == 0):
                flood_dictionary = {
                    'informed_nodes': 0,
                    'uninformed_nodes': len(G.get_list_of_nodes()),
                    't_flood': 0,
                    'process_status': G.get_converged(),
                    'flood_status': False,
                    'initiator': G.flooding.get_initiator()
                }

                repeat = False
                final_stats.append({**sim, **stats, **flood_dictionary})
                logging.info("The graph is not connected, flooding will always fail")
                logging.info("Exiting")

            if (repeat):

                if (G.flooding.get_converged() == False):
                    flood_dictionary = flood()
                    final_stats.append({**sim, **stats, **flood_dictionary})

                else:
                    logging.info("Flooding protocol simulation %r: CONVERGED" % data["sim"])

                    repeat = False




        t += 1

    # print(G.flooding.get_list_of_informed_ndoes())
    # print(str(sim) + " represent!")
    return_dict[sim['simulation']] = final_stats


if __name__ == "__main__":
    d_list = [3]
    c_list = [1.5,3,4]
    n_list = [512, 1024, 2048, 4096, 8192, 16384, 32768]

    exponent = [2,2.3,2.5,2.7,3]
    probs_list = [0.0,0.1,0.5,0.7,0.9]
    outPath = "./tmp/"
    for d in d_list:
        for c in c_list:
            for n in n_list:
                for probs in probs_list:
                    for ex in exponent:
                        iterate = True
                        dd = []
                        while iterate:  # Continue generating sequences until one of them is graphical
                            dd = sorted([int(round(d)) for d in powerlaw_sequence(n, ex)], reverse=True)  # Round to nearest integer to obtain DISCRETE degree sequence
                            if is_graphical(dd):
                                iterate = False
                  
                        data = {
                            "d": d,
                            "c": c,
                            "dd":dd,
                            "edge_falling_rate": probs,
                            "max_iter": 100,
                            "gamma":ex
                        }
                        name = "ERAESDD_c_" + str(c) +"_n_"+str(n)+ "_p_" + str(probs)+"_g_"+str(ex)
                        outpath = create_folder(outPath, name)
                        logging.info("EXECUTING: %r " % name)
                        manager = multiprocessing.Manager()
                        return_dict = manager.dict()
                        jobs = []
                        for i in range(10):
                            data["sim"] = i
                            p = multiprocessing.Process(target=worker, args=(data, return_dict))
                            jobs.append(p)
                            p.start()

                        for proc in jobs:
                            proc.join()

                        reduced = []
                        for key in return_dict:
                            reduced.extend(return_dict[key])

                        df = pd.DataFrame(reduced)

                        df.to_csv(outpath + "results.csv")
