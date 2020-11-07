from src.Graphs.Objects.MultipleEdge import DynamicGraph
from src.FileOperations.WriteOnFile import create_file,create_folder,write_on_file_contents
from src.Graphs.Objects.Queue import Queue
from src.StastModules.Snapshot import get_snapshot
from src.StastModules.SpectralAnalysis import get_spectral_gap_transition_matrix
import networkx as nx

import time
import math as mt

class EdgeDynamicOutput:
    def __init__(self):
        self.stats = []
        #self.flood_infos = []
    def add_stats(self,new_stats):
        self.stats.append(new_stats)
    # def add_flood_infos(self,new_flood_infos):
    #     self.flood_info.append(new_flood_infos)
    def get_stats(self):
        return(self.stats)
    # def get_flood_infos(self):
    #     return(self.flood_infos)


class EdgeDynamic:

    def __init__(self,d ,c,p,n ,outpath ,flooding = True, epsilon = 0.05 ,model ="Multiple",simNumber = 30 ):
        self.d_list = d
        self.c_list = c
        self.p_list = p
        self.n_list = n
        self.flooding = flooding
        self.model = model
        self.outPath = outpath
        self.simNumber = simNumber
        self.epsilon = epsilon

    def run(self):
        print("Starting simulation ")
        sim_start = time.time()
        for p in self.p_list:
           for n in self.n_list:
                print("Number of nodes ",n," Falling probability: ",p," Flooding: ",self.flooding)
                outpath = create_folder(self.outPath,"EdgeDynamic_n_"+str(n)+"_p_"+str(p)+"_f_"+str(self.flooding))
                outpath = outpath + "results"
                edgeDynamicStats = EdgeDynamicOutput()
                for d in self.d_list:
                    for c in self.c_list:
                        for sim in range(0,self.SimNumber):
                            print("Simulation: ",sim)
                            start_time = time.time()
                            stats = self.EdgeDynamicGenerator(d, c,p,n,sim)
                            edgeDynamicStats.add_stats(stats)
                            #vertexDynamicStats.add_flood_infos(flood_info)
                            print("Elapsed time: ",time.time()-start_time)
                self.write_info_dic_as_csv(outpath,edgeDynamicStats)
        print("Ending simulation")
        print("Elapsed time : ", time.time() - sim_start)

    def EdgeDynamicGenerator(self, d, c, p,n, sim):

        def flood():
            flood_dictionary = {}
            if (G.get_converged()):
                if (G.flooding.get_initiator() == -1):
                    G.set_flooding()
                    G.flooding.set_initiator()
                    G.flooding.update_flooding(G)
                    print("----- Flooding Simulation: STARTED -----\n")
                else:
                    if (G.flooding.get_started() == True):
                        G.flooding.update_flooding(G)
                    G.flooding.is_informed()
                    if (G.flooding.get_converged()):
                        print("--- ALL NODES IN THE NETWORK ARE INFORMED ---\n\n")
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

        def spectral_convergence( epsilon, spectral_gap, spectral_queue):
            if (spectral_gap == "Null"):
                new_spectral_gap = 0
            else:
                new_spectral_gap = spectral_gap
            spectral_queue.add_element_to_queue(new_spectral_gap)

            # Check the convergence of the spectral gap

            if (
                    spectral_queue.get_queue_lenght() == spectral_queue.get_max_lenght() and spectral_queue.get_converged() == False):
                spectral_differences = []
                s_q = spectral_queue.get_queue()
                for i in range(0, spectral_queue.get_queue_lenght() - 1):
                    spectral_differences.append(abs(s_q[i] - s_q[i + 1]))
                terminate = True
                for j in spectral_differences:
                    if (j > epsilon):
                        terminate = False
                if (terminate):
                    spectral_queue.set_converged(terminate)
                    G.set_converged(terminate)
                    G.flooding.set_converged(False)
                    print("----- Spectral Gap Converged at: ", spectral_gap, " -----\n")
            return (spectral_queue)

        t = 0
        final_stats = []

        repeat = True
        sim = {
            "simulation": sim
        }
        if (d <= 0 or c < 0):
            print("Error, input parameters must be: d>0 c>1")
            return (-1)
        spectral_queue = Queue(mt.log(n, 2))
        G = DynamicGraph(n, d, c, falling_probability = p,model = self.model)

        while(repeat):
            G.add_phase()
            G.del_phase()
            Isinvertible, spectralGap, lambdaNGap = get_spectral_gap_transition_matrix(G.get_G())
            if (G.get_converged() == False):
                stats_bef = {
                    "spectralGapBefore": spectralGap,
                    "lambdaNGapBefore": lambdaNGap
                }

            if (p != 0):

                G.random_fall()
            Isinvertible, spectralGap, lambdaNGap = get_spectral_gap_transition_matrix(G.get_G())
            if (G.get_converged() == False):
                stats = get_snapshot(G, p, G.get_d(), G.get_c(), t)
            # if (G.get_converged() == False):
            #
            #     stats_aft = {
            #         "spectralGapAfter": spectralGap,
            #         "lambdaNGapAfter": lambdaNGap
            #     }
            if (G.get_converged() == False):
                spectral_queue = spectral_convergence( self.epsilon, spectralGap, spectral_queue)
            if (G.get_converged()):
                if (nx.is_connected(G.get_G()) == False and p == 0):
                    flood_dictionary = {
                        'informed_nodes': 0,
                        'uninformed_nodes': len(G.get_list_of_nodes()),
                        't_flood': 0,
                        'process_status': G.get_converged(),
                        'flood_status': False,
                        'initiator': G.flooding.get_initiator()
                    }

                    repeat = False
                    # final_stats.append({**sim, **stats_bef,**stats_aft, **stats, **flood_dictionary})
                    final_stats.append({**sim, **stats_aft, **stats, **flood_dictionary})
                    print("THE GRAPH IS NOT CONNECTED, flooding will always fail, exiting ")
                if (repeat):

                    if (G.flooding.get_converged() == False):
                        flood_dictionary = flood()
                        print("NUMERO DI NODI INFORMATI :", G.flooding.get_informed_nodes())
                        print("NUMERO DI NODI NON INFORMATI:", G.flooding.get_uninformed_nodes())
                        print("CONVERGENZA GRAFO DINAMICO:", G.get_converged())
                        # print({**sim,**stats_bef ,**stats_aft,**stats, **flood_dictionary}.keys())
                        # final_stats.append({**sim,**stats_bef ,**stats_aft,**stats, **flood_dictionary})
                        print("MAIOO")
                        final_stats.append({**sim, **stats_bef, **stats, **flood_dictionary})
                        # print(final_stats)
                    else:
                        repeat = False
            t+=1
        return (final_stats)




    def write_info_dic_as_csv(self, outPath, results):
        print( list(results.get_stats()[0][0].keys()))
        create_file(outPath, list(results.get_stats()[0][0].keys()))
        for i in results.get_stats():
            write_on_file_contents(outPath, i)