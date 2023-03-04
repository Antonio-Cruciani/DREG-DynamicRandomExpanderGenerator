import multiprocessing
from src.Graphs.Objects.MultipleEdge import DynamicGraph
from src.StastModules.Snapshot import get_snapshot
from src.FileOperations.WriteOnFile import create_file, create_folder, write_on_file_contents
from src.StastModules.SpectralAnalysis import spectral_gap_sparse,spectral_gap

import networkx as nx
import math as mt
import logging
import pandas as pd

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


def worker(data, return_dict):


    """worker function"""
    final_stats = []

    d = data["d"]
    c = data["c"]
    edge_falling_rate = data["edge_falling_rate"]
    # sim = data["sim"]
    max_iter = data["max_iter"]
    G = DynamicGraph(n, d, c,falling_probability= edge_falling_rate)
    t = 0
    achieved = False
    repeat = True
    sim = {
        "simulation": data["sim"]
    }
    while (repeat):



        G.add_phase()
        G.del_phase()
        spectralGapBefore = spectral_gap(G.get_G())

        stats_bef = {
            "spectralGapBefore": spectralGapBefore,
        }
        if (edge_falling_rate != 0):
            G.random_fall()
        spectralGapAfter = spectral_gap(G.get_G())

        stats_aft = {
            "spectralGapAfter": spectralGapAfter,
        }
        stats = get_snapshot(G, edge_falling_rate, G.get_d(), G.get_c(), t)
        if t==max_iter:
            repeat = False
            logging.info("Spectral Gap simulation %r: TERMINATED" % data["sim"])

        final_stats.append({**sim, **stats_bef, **stats_aft, **stats})

        t += 1

    # print(G.flooding.get_list_of_informed_ndoes())
    # print(str(sim) + " represent!")
    return_dict[sim['simulation']] = final_stats


if __name__ == "__main__":
    d_list = [5]
    c_list = [1.5]
    n_list = [512, 1024, 2048, 4096, 8192, 16384, 32768]


    probs_list = [0.0]
    outPath = "./tmp/"
    for d in d_list:
        for c in c_list:
            for n in n_list:
                for probs in probs_list:
                    data = {
                        "d": d,
                        "c": c,
                        "edge_falling_rate": probs,
                        "max_iter": 100
                    }
                    name = "ERAES_d_" + str(d) + "_c_" + str(c) +"_n_"+str(n)+ "_p_" + str(probs)
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

    # print(return_dict.values())