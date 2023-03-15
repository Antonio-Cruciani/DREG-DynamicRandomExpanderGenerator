import multiprocessing
from src.Graphs.Objects.MultipleEdge import DynamicGraph
from src.StastModules.Snapshot import get_snapshot_dynamic_dd
from src.FileOperations.WriteOnFile import create_file, create_folder, write_on_file_contents

import math as mt
import logging
import pandas as pd

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


def worker(data, return_dict):
    def check_convergence_dynamic():
        flood_dictionary = {}
        # print(G.get_converged())
        if (G.get_converged()):
            if (G.flooding.get_initiator() == -1):
                # print("STARTING FLOODING")
                logging.info("Flooding started for simulation %r ", data['sim'])
                G.set_flooding()
                G.flooding.set_stop_time(mt.floor(mt.log(G.get_target_n(), 2)))
                G.flooding.set_initiator()
                G.flooding.update_flooding(G)
            else:

                # Updating Flooding
                # if (G.flooding.get_t_flood() == 1):
                #    print("Flooding protocol STARTED %r" % (G.flooding.get_started()))
                if (G.flooding.get_started() == True):
                    G.flooding.update_flooding(G)

                    if (not G.flooding.check_flooding_status()):
                        G.set_converged(True)
                        if (G.flooding.get_number_of_restart() == 0):
                            # print("All the informed nodes left the network")
                            # print("Flooding Protocol status: Failed")
                            # print("----------------------------------------------------------------")
                            G.flooding.set_converged(False)
                            G.flooding.set_failed(True)
                    # if (G.flooding.get_converged()):
                    # print("AL NODES IN THE NETWORK ARE INFORMED")
                    # print("Number of informed nodes %d" % (G.flooding.get_informed_nodes()))
                    # print("Number of uninformed nodes %d " % (G.flooding.get_uninformed_nodes()))
                    # print("Percentage of informed nodes %r" % (G.flooding.get_percentage()))
                    # print("Informed Ratio: %r" % (G.flooding.get_last_ratio()))
                    # print("Flooding Protocol status: Correctly Terminated")
                    # print("Flooding time: %d" % (G.flooding.get_t_flood()))
                    # print("----------------------------------------------------------------")

                    threshold = G.get_target_n()
                    if (G.flooding.get_t_flood() > 100 * threshold):
                        # print("Iterations > threshold")
                        # print("The Flooding protocol is too slow, stopping the simulation")
                        # print("Number of informed nodes %d " % (G.flooding.get_informed_nodes()))
                        # print("Number of uninformed nodes %d " % (G.flooding.get_uninformed_nodes()))
                        # print("Percentage of informed nodes %r" % (G.flooding.get_percentage()))
                        # print("Informed Ratio: %r" % (G.flooding.get_last_ratio()))
                        # print("Flooding Protocol status: Failed")
                        # print("Number of executed steps: %d  Step threshold: %d" % (
                        # G.flooding.get_t_flood(), threshold))
                        # print("----------------------------------------------------------------")
                        G.set_converged(True)
                        G.flooding.set_converged(False)
                        G.flooding.set_failed(True)

            flood_dictionary['informed_nodes'] = G.flooding.get_informed_nodes()
            flood_dictionary['uninformed_nodes'] = G.flooding.get_uninformed_nodes()
            flood_dictionary['percentage_informed'] = G.flooding.get_percentage()
            flood_dictionary['t_flood'] = G.flooding.get_t_flood()
            flood_dictionary['process_status'] = G.get_converged()
            flood_dictionary['flood_status'] = G.flooding.get_converged()
            flood_dictionary['initiator'] = G.flooding.get_initiator()

        else:
            flood_dictionary['informed_nodes'] = 0
            flood_dictionary['uninformed_nodes'] = len(G.get_list_of_nodes())
            flood_dictionary['percentage_informed'] = 0
            flood_dictionary['t_flood'] = 0
            flood_dictionary['process_status'] = G.get_converged()
            flood_dictionary['flood_status'] = G.flooding.get_converged()
            flood_dictionary['initiator'] = G.flooding.get_initiator()

        return (flood_dictionary)

    """worker function"""
    final_stats = []

    c = data["c"]
    gamma = data["gamma"]
    inrate = data["inrate"]
    outrate = data["outrate"]
    edge_falling_rate = data["edge_falling_rate"]
    # sim = data["sim"]
    max_iter = data["max_iter"]
    G = DynamicGraph(0, 3, c, inrate, outrate, edge_falling_rate,gamma=gamma)
    t = 0
    achieved = False
    repeat = True
    sim = {
        "simulation": data["sim"],
        "pl_exponent":data["gamma"]
    }
    while (repeat):

        G.disconnect_from_network()
        G.connect_to_network_dd()
        # print("NODES IN new ",G.get_nodes_t())

        G.add_phase_vd_dd()
        G.del_phase_vd_dd()
        if (edge_falling_rate != 0):
            G.random_fall()

        if (not achieved):
            if (G.get_target_density()):
                # print("The Graph contains the desired number of nodes")
                achieved = True
                # print("CI SONO")
                G.set_converged(True)
                stats = get_snapshot_dynamic_dd(G, G.get_c(),G.get_vd_dd(), t)
                flood_info = check_convergence_dynamic()
                conv_perc = {"conv_percentage": (G.get_semiregular_percentage())}
                final_stats.append({**sim, **conv_perc, **stats, **flood_info})
            else:
                stats = get_snapshot_dynamic_dd(G, G.get_c(),G.get_vd_dd(), t)
                flood_info = check_convergence_dynamic()
                conv_perc = {"conv_percentage": (G.get_semiregular_percentage())}
                final_stats.append({**sim, **conv_perc, **stats, **flood_info})

        else:
            stats = get_snapshot_dynamic_dd(G, G.get_c(),G.get_vd_dd(), t)
            flood_info = check_convergence_dynamic()
            conv_perc = {"conv_percentage": (G.get_semiregular_percentage())}
            final_stats.append({**sim, **conv_perc, **stats, **flood_info})

        if (G.flooding.get_t_flood() == max_iter):
            logging.info("Flooding protocol simulation %r: CONVERGED" % data["sim"])
            repeat = False
        if (G.flooding.get_failed()):
            repeat = False
            logging.info("Flooding protocol simulation %r: FAILED" % data["sim"])
        t += 1

    # print(G.flooding.get_list_of_informed_ndoes())
    # print(str(sim) + " represent!")
    return_dict[sim['simulation']] = final_stats


if __name__ == "__main__":
    c_list = [1.5,2,3]
    n_list = [512, 1024, 2048, 4096, 8192, 16384, 32768]
    outrate_list = [0.1,0.3,0.5,0.7,0.9]
    inrate_list = []
    for n in n_list:
        for q in outrate_list:
            inrate_list.append((n * q,q))

    #probs_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
    probs_list = [0.0,0.1,0.5,0.7,0.9]
    exponent = [2,2.3,2.5,2.7,3]

    #probs_list = [0.0]

    outPath = "./tmp_evraes/"
    for c in c_list:
        for inrate in inrate_list:
            #for outrate in outrate_list:
                for probs in probs_list:
                    for ex in exponent:
                        data = {
                            "c": c,
                            "inrate": inrate[0],
                            "outrate": inrate[1],
                            "edge_falling_rate": probs,
                            "max_iter": 100,
                            "gamma":ex
                        }
                        name = "MixedDynamic_c_" + str(c) + "_inrate_" + str(
                            inrate[0]) + "_outrate_" + str(inrate[1]) + "_p_" + str(probs)+"_g_"+str(ex)
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