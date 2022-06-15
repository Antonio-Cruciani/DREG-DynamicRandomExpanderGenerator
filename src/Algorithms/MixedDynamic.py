#import logging
import concurrent
from multiprocessing import Pool,set_start_method,Process
import os
import time
import math as mt
import networkx as nx
from src.Graphs.Objects.MultipleEdge import DynamicGraph
from src.FileOperations.WriteOnFile import create_file, create_folder, write_on_file_contents
from src.StastModules.Snapshot import get_snapshot_dynamic,get_snapshot_dynamicND
class VertexDynamicOutput:
    def __init__(self):
        self.stats = []
        # self.flood_infos = []

    def add_stats(self, new_stats):
        self.stats.append(new_stats)

    # def add_flood_infos(self,new_flood_infos):
    #     self.flood_info.append(new_flood_infos)
    def get_stats(self):
        return (self.stats)
    # def get_flood_infos(self):
    #     return(self.flood_infos)

class MixedDynamic:

    def __init__(self, d, c, inrate, outrate, falling_probababilities, outpath, flooding=True, regular_convergence=0.9, regular_decay=0.5
                 , model="Multiple", simNumber=100, maxIter=100):
        self.d_list = d
        self.c_list = c
        self.inrate_list = inrate
        self.outrate_list = outrate
        self.edge_disappearance_rate = falling_probababilities
        self.flooding = flooding
        self.decay = regular_decay
        self.cdPercentage = regular_convergence
        self.model = model
        self.outPath = outpath
        self.simNumber = simNumber

        self.max_iter = maxIter
    def get_data(self,data,sim):
        data['sim'] = sim
        return sim
    def run(self):
        print("----------------------------------------------------------------")
        print("Starting simulation Mixed Dynamics")
        set_start_method('spawn',force=True)
        os.nice(10)


        sim_start = time.time()
        experiments = []
        for inrate in self.inrate_list:
            for outrate in self.outrate_list:
                for p in self.edge_disappearance_rate:
                    print("----------------------------------------------------------------")
                    print("Inrate: %r Outrate: %r Edge Disappearance Rate: %r Flooding: %r" % (inrate, outrate,p, self.flooding))
                    #outpath = create_folder(self.outPath,
                    #                        "VertexDynamic_in_" + str(inrate) + "_out_" + str(outrate) + "_ep_"+str(p) + "_f_"+str(
                    #                            self.flooding))
                    #path = outpath
                    #outpath = outpath + "results"
                    vertexDynamicStats = VertexDynamicOutput()
                    for d in self.d_list:
                        print("Inrate: %r Outrate: %r Flooding %r d: %d" % (inrate, outrate, self.flooding, d))
                        # print("Inrate: ", inrate, " Outrate: ", outrate, " Flooding: ", self.flooding, "d: ",d)
                        for c in self.c_list:
                            print(
                                "Inrate: %r Outrate: %r Flooding %r d: %d c: %r " % (inrate, outrate, self.flooding, d, c))
                            # print("Inrate: ", inrate, " Outrate: ", outrate, " Flooding: ", self.flooding, " d: ",d," c: ",c)

                            for sim in range(0, self.simNumber):
                            #print("Simulation %d" % (sim))

                                data = {
                                    "d":d,
                                    "c":c,
                                    "inrate":inrate,
                                    "outrate":outrate,
                                    "edge_falling_rate":p,
                                    "sim" : sim
                                }
                                experiments.append(data)



                            #p = Pool()
                            #for stats in p.map(self.MixedDynamicGenerator, data):
                            #    vertexDynamicStats.add_stats(stats)





                            #sprint("Elapsed time %r" % (time.time() - start_time))
                            print("----------------------------------------------------------------")
                #self.write_info_dic_as_csv(outpath, vertexDynamicStats)

        start_time = time.time()
        #pool = Pool()

        max_workers = 3

        with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:

            results = [executor.submit(self.MixedDynamicGenerator, data) for i in range(max_workers)]

            for f in concurrent.futures.as_completed(results):
                if f:
                    print(f)
                    break

        print("Ending simulation")
        print("Total elapsed time %r" % (time.time() - sim_start))

    def MixedDynamicGenerator(self, data):

        d= data['d']
        c = data['c']
        inrate = data['inrate']
        outrate = data['outrate']
        edge_falling_rate = data['edge_falling_rate']
        sim = data['sim']
        def check_convergence_dynamic():
            flood_dictionary = {}
            if (G.get_converged()):
                if (G.flooding.get_initiator() == -1):
                    G.set_flooding()
                    G.flooding.set_stop_time(mt.floor(mt.log(G.get_target_n(), 2)))
                    G.flooding.set_initiator()
                    G.flooding.update_flooding(G)
                else:

                    # Updating Flooding
                    #if (G.flooding.get_t_flood() == 1):
                    #    print("Flooding protocol STARTED %r" % (G.flooding.get_started()))
                    if (G.flooding.get_started() == True):
                        G.flooding.update_flooding(G)

                        if (not G.flooding.check_flooding_status()):
                            G.set_converged(True)
                            if (G.flooding.get_number_of_restart() == 0):
                                #print("All the informed nodes left the network")
                                #print("Flooding Protocol status: Failed")
                                #print("----------------------------------------------------------------")
                                G.flooding.set_converged(False)
                                G.flooding.set_failed(True)
                        #if (G.flooding.get_converged()):
                            #print("AL NODES IN THE NETWORK ARE INFORMED")
                            #print("Number of informed nodes %d" % (G.flooding.get_informed_nodes()))
                            #print("Number of uninformed nodes %d " % (G.flooding.get_uninformed_nodes()))
                            #print("Percentage of informed nodes %r" % (G.flooding.get_percentage()))
                            #print("Informed Ratio: %r" % (G.flooding.get_last_ratio()))
                            #print("Flooding Protocol status: Correctly Terminated")
                            #print("Flooding time: %d" % (G.flooding.get_t_flood()))
                            #print("----------------------------------------------------------------")

                        threshold = G.get_target_n()
                        if (G.flooding.get_t_flood() > 100 * threshold):
                            #print("Iterations > threshold")
                            #print("The Flooding protocol is too slow, stopping the simulation")
                            #print("Number of informed nodes %d " % (G.flooding.get_informed_nodes()))
                            #print("Number of uninformed nodes %d " % (G.flooding.get_uninformed_nodes()))
                            #print("Percentage of informed nodes %r" % (G.flooding.get_percentage()))
                            #print("Informed Ratio: %r" % (G.flooding.get_last_ratio()))
                            #print("Flooding Protocol status: Failed")
                            #print("Number of executed steps: %d  Step threshold: %d" % (
                            #G.flooding.get_t_flood(), threshold))
                            #print("----------------------------------------------------------------")
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




        t = 0

        final_stats = []
        achieved = False

        repeat = True
        sim = {
            "simulation": sim
        }


        if (d <= 0 or c < 0):
            print("Input parameters must be: d>0 c>1")
            return (-1)
        if (edge_falling_rate<0 or edge_falling_rate>1):
            print("p must be a probability")
            return (-1)


        G = DynamicGraph(0, d, c, inrate, outrate, edge_falling_rate, self.model)


        while (repeat):
            G.disconnect_from_network()
            G.connect_to_network()

            G.add_phase_vd()

            G.random_fall()

            G.del_phase_vd()

            if (not achieved):
                if (G.get_target_density()):
                    #print("The Graph contains the desired number of nodes")
                    achieved = True
                    stats = get_snapshot_dynamic(G, G.get_d(), G.get_c(), t)
                    flood_info = check_convergence_dynamic()
                    conv_perc = {"conv_percentage": (G.get_semiregular_percentage())}
                    final_stats.append({**sim, **conv_perc, **stats, **flood_info})
            else:
                stats = get_snapshot_dynamic(G, G.get_d(), G.get_c(), t)
                flood_info = check_convergence_dynamic()
                conv_perc = {"conv_percentage": (G.get_semiregular_percentage())}
                final_stats.append({**sim, **conv_perc, **stats, **flood_info})
            t += 1

            if (G.flooding.get_converged() and (not (G.flooding.get_failed()))):
                repeat = False

            if (G.flooding.get_failed()):
                repeat = False
                print("Flooding protocol: FAILED")

            if t == self.max_iter:
                repeat = False
        print("_--------------Converged--------------")

        #return (final_stats)
        return True


    def write_info_dic_as_csv(self, outPath, results):
        res = []
        for elem in results.get_stats():
            for stat in elem:
                res.append(stat)
        print("--------------")
        print(res)
        create_file(outPath, list(res[0][0].keys()))
        for i in results.get_stats():
            write_on_file_contents(outPath, i)


