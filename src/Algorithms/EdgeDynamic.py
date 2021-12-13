from src.Graphs.Objects.MultipleEdge import DynamicGraph
from src.FileOperations.WriteOnFile import create_file,create_folder,write_on_file_contents
from src.Graphs.Objects.Queue import Queue
from src.StastModules.Snapshot import get_snapshot
from src.StastModules.SpectralAnalysis import spectral_gap_sparse,spectral_gap
import networkx as nx
import time
import math as mt
import os
import logging
from itertools import count
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

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

    def __init__(self,d ,c,p,n ,outpath ,flooding = True, epsilon = 0.05 ,model ="Multiple",simNumber = 30 ,maxIter = 100,onlySpectral = False,Offline =False,GPU = False):
        """

        :param d: int, minimum degree that each node must have
        :param c: float, tolerance constant, c*d is the maximum degree that each node can have
        :param p: float, edge-falling probability
        :param n: int, number of node in the dynamic graph
        :param outpath: str, output path for the results
        :param flooding: bool, if True, simulates the flooding process
        :param epsilon: float, epsilon value for the heuristic convergence. NOTE: The algorithm will compute the best value anyway
        :param model: str, if Multiple each node will sample more than one node at each round, NOTE: Leave it as Multiple
        :param simNumber: int, number of experiments to perfom
        :param maxIter: int, maximum number of steps for the simulations
        :param onlySpectral: bool, if true will save only the spectral properties of the graph
        :param Offline: bool, if true, will simulate the model saving the adjacency list of the model at each time step without computing any statistic
        :param GPU: bool, if true, will be used the GPU instead of the CPU for solving the eigen-problem
        """
        self.d_list = d
        self.c_list = c
        self.p_list = p
        self.n_list = n
        self.flooding = flooding
        self.model = model
        self.outPath = outpath
        self.simNumber = simNumber
        self.epsilon = epsilon
        self.spectrumSim = onlySpectral
        self.MC = Offline
        self.max_iter = maxIter
        self.GPU = GPU
        self.epsilon_steps = 25
        #logging.debug("MAX ITER = %r"%(self.max_iter))
    def run(self):
        logging.info("----------------------------------------------------------------")
        logging.info("Starting simulation")
        sim_start = time.time()
        for p in self.p_list:

           for n in self.n_list:

                logging.info("----------------------------------------------------------------")
                logging.info("Number of nodes: %r Falling probability: %r Flooding: %r" % (n,p,self.flooding))
                outpath = create_folder(self.outPath,"EdgeDynamic_n_"+str(n)+"_p_"+str(p)+"_f_"+str(self.flooding))
                outpath = outpath + "results"
                os.mkdir(outpath)

                edgeDynamicStats = EdgeDynamicOutput()
                for d in self.d_list:
                    logging.info("Number of nodes: %r Falling probability: %r Flooding: %r d: %r" % (n,p,self.flooding,d))
                    for c in self.c_list:
                        logging.info(
                            "Number of nodes: %r Falling probability: %r Flooding: %r d: %d c: %r" % (n, p, self.flooding, d,c))
                        if (p != 0 and (not self.spectrumSim) and (not self.MC) and False):
                            logging.info(" Inferring epsilon , please wait")
                            epsilon = self.get_epsilon(d, c, p, n)
                        else:
                            epsilon = self.epsilon
                        logging.info("Inferred Epsilon: %r " % (epsilon))
                        for sim in range(0,self.simNumber):
                            logging.info("Simulation: %d" % (sim))
                            start_time = time.time()
                            if(self.spectrumSim):
                                stats = self.EdgeDynamicGeneratorSpectrum(d, c,p,n,sim,epsilon)
                            elif(self.MC):
                                stats = self.EdgeDynamicGeneratorMCConfigurations( d, c, p, n, outpath, sim)

                            else:
                                stats = self.EdgeDynamicFlooding(d,c,p,n,sim,epsilon)
                            edgeDynamicStats.add_stats(stats)
                            logging.info("Elapsed time %r" % (time.time()-start_time))
                self.write_info_dic_as_csv(outpath,edgeDynamicStats)
        logging.info("----------------------------------------------------------------")
        logging.info("Ending Simulation")
        logging.info("Elapsed time of the entire simulation %r" % (time.time() - sim_start))


    def EdgeDynamicGenerator(self, d, c, p,n, sim,epsilon):

        def flood():
            flood_dictionary = {}
            if (G.get_converged()):
                if (G.flooding.get_initiator() == -1):
                    G.set_flooding()
                    G.flooding.set_initiator()
                    G.flooding.update_flooding(G)
                    logging.info("Flooding Simulation : STARTED")
                else:
                    if (G.flooding.get_started() == True):
                        G.flooding.update_flooding(G)
                    G.flooding.is_informed()
                    if (G.flooding.get_converged()):
                        logging.info("ALL NODES IN THE NETWORK ARE INFORMED")
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
                    print(s_q[i])
                    spectral_differences.append(abs(s_q[i] - s_q[i + 1]))
                terminate = True
                for j in spectral_differences:
                    if (j > epsilon):
                        terminate = False
                if (terminate):
                    spectral_queue.set_converged(terminate)
                    G.set_converged(terminate)
                    G.flooding.set_converged(False)
                    logging.info("Spectral Gap converged at %r" % (spectral_gap))
            return (spectral_queue)

        t = 0
        final_stats = []

        repeat = True
        sim = {
            "simulation": sim,
            "epsilon": epsilon
        }
        if (d <= 0 or c < 0):
            logging.error("Error, input parameters must be: d>0 c>1")
            return (-1)
        spectral_queue = Queue(mt.log(n, 2))
        G = DynamicGraph(n, d, c, falling_probability = p,model = self.model)

        while(repeat):
            G.add_phase()
            G.del_phase()

            spectralGapBefore = spectral_gap_sparse(G.get_G())

            spectral_bef = {
               "spectralGapBefore": spectralGapBefore
            }
            if (p != 0):

                G.random_fall()

            spectralGapAfter = spectral_gap_sparse(G.get_G())

            spectral_aft = {
                "spectralGap":spectralGapAfter
            }
            if (G.get_converged() == False):
                stats = get_snapshot(G, p, G.get_d(), G.get_c(), t)

            if (G.get_converged() == False):
                spectral_queue = spectral_convergence( epsilon, spectralGapAfter, spectral_queue)
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
                    final_stats.append({**sim, **stats,**spectral_bef,**spectral_aft, **flood_dictionary})
                    logging.info("The graph is not connected, flooding will always fail")
                    logging.info("Exiting")
                if (repeat):

                    if (G.flooding.get_converged() == False):
                        flood_dictionary = flood()
                        final_stats.append({**sim, **stats, **flood_dictionary})

                    else:
                        repeat = False
            t+=1
        return (final_stats)


    def EdgeDynamicFlooding(self, d, c, p, n, sim, epsilon):

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



        t = 0
        final_stats = []

        repeat = True
        sim = {
            "simulation": sim,
            "epsilon": epsilon
        }
        if (d <= 0 or c < 0):
            logging.error("Error, input parameters must be: d>0 c>1")
            # print("Error, input parameters must be: d>0 c>1")
            return (-1)
        G = DynamicGraph(n, d, c, falling_probability=p, model=self.model)

        while (repeat):
            #logging.debug("ITERATION = %r"%(t))

            G.add_phase()
            G.del_phase()


            if (p != 0):
                G.random_fall()

            if (G.get_converged() == False):
                stats = get_snapshot(G, p, G.get_d(), G.get_c(), t)

            if(t==self.max_iter):

                G.set_converged(True)
                G.flooding.set_converged(False)

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
                    final_stats.append({**sim, **stats,**flood_dictionary})
                    logging.info("The graph is not connected, flooding will always fail")
                    logging.info("Exiting")
                if (repeat):

                    if (G.flooding.get_converged() == False):
                        flood_dictionary = flood()
                        final_stats.append({**sim, **stats, **flood_dictionary})

                    else:
                        repeat = False
            t += 1

        return (final_stats)

    def EdgeDynamicGeneratorMCConfigurations(self,d,c,p,n,path,sim):
        t = 0
        if (d <= 0 or c < 0):
            logging.error("Error, input parameters must be: d>0 c>1")
            return (-1)
        G = DynamicGraph(n, d, c, falling_probability = p,model = self.model)
        repeat = True
        logging.info("OFFLINE MODE")
        try:
            # Create sim Directory
            os.mkdir(path +"/"+ str(sim))
            logging.info("Directory %r sim  Created "%(path))
        except FileExistsError:
            logging.error("Directory %r sim already exists"%(path))

        try:
            # Create sim Directory
            os.mkdir(path + "/"+str(sim) + "/beforeA")
            logging.info("Directory %r sim/before Created "%(path))
        except FileExistsError:
            logging.error("Directory %r sim/before already exists"%(path))

        try:
            # Create sim Directory
            os.mkdir(path + "/"+str(sim) + "/before")
            logging.info("Directory %r sim/before Created "%(path))
        except FileExistsError:
            logging.error("Directory %r sim/before already exists"%(path))
        try:
            # Create sim Directory
            os.mkdir(path +"/"+ str(sim) + "/after")
            logging.info("Directory %r sim/after Created "%(path))
        except FileExistsError:
            logging.error("Directory %r sim/after already exists"%(path))
        stats = {"d":d,"c":c,"n":n,"p":p}
        nx.write_adjlist(G.get_G(), path=path + "/" + str(sim) +"_" + str(t) + ".adjlist")

        while (repeat):
            G.add_phase()
            nx.write_adjlist(G.get_G(), path=path +"/"+ str(sim) + "/beforeA/" + str(t) + ".adjlist")

            G.del_phase()
            nx.write_adjlist(G.get_G(), path=path +"/"+ str(sim) + "/before/" + str(t) + ".adjlist")

            if (p != 0):
                G.random_fall()
                nx.write_adjlist(G.get_G(), path=path +"/"+ str(sim) + "/after/" + str(t) + ".adjlist")

            if(t == self.max_iter):
                repeat = False
            t+=1
        stats2 = {"d":d,"c":c,"n":n,"p":p}
        stats3 = [stats,stats2]
        return stats3
    def EdgeDynamicGeneratorSpectrum(self, d, c, p,n, sim,epsilon):



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
                    logging.info("Spectral Gap converged at %r" % (spectral_gap))
            return (spectral_queue)

        t = 0
        final_stats = []

        repeat = True
        sim = {
            "simulation": sim,
            "epsilon": epsilon
        }
        if (d <= 0 or c < 0):
            logging.error("Error, input parameters must be: d>0 c>1")
            return (-1)
        spectral_queue = Queue(mt.log(n, 2))
        G = DynamicGraph(n, d, c, falling_probability = p,model = self.model)
        c = 0

        start = time.time()
        while(repeat ):
            if ( t % 50 == 0):
                partial = time.time() - start
                logging.info("Computed %r steps in %r"%(t,partial))


            G.add_phase_MT()
            G.del_phase_MT()

            #spectralGapBefore,lambda1Before,lambda2Before = spectral_gap(G.get_G())
            spectralGapBefore = spectral_gap(G.get_G())

            stats_bef = {
                "spectralGapBefore": spectralGapBefore,
            }

            if (p != 0):
                G.random_fall_MT()

            #spectralGapAfter,lambda1After,lambda2After = spectral_gap(G.get_G())
            spectralGapAfter = spectral_gap(G.get_G())

            stats_aft = {
                "spectralGapAfter": spectralGapAfter,
            }

            stats = get_snapshot(G, p, G.get_d(), G.get_c(), t)

            if (G.get_converged() == False):
                spectral_queue = spectral_convergence( epsilon, spectralGapAfter, spectral_queue)
            if (G.get_converged()):

                if(c == self.max_iter):
                    repeat = False
                else:
                    c+=1

            final_stats.append({**sim, **stats_bef,**stats_aft, **stats})
            #logging.debug("SPECTRAL BEFORE %r SPECTRAL AFTER %r"%(spectralGapBefore,spectralGapAfter))
            t+=1

        return (final_stats)




    def get_epsilon(self,d,c,p,n):
        G = DynamicGraph(n, d, c, falling_probability = p,model = self.model)
        t = 0
        spectral_list = []
        while(t<self.epsilon_steps):
            G.add_phase_MT()
            G.del_phase_MT()
            G.random_fall_MT()

            spectralGap = spectral_gap(G.get_G())
            spectral_list.append(spectralGap)
            t+=1
        filtered = list(filter(lambda x: (x != 0), spectral_list))
        if(len(filtered) == 0):
            return (self.epsilon)
        mean = sum(filtered) / len(filtered)
        sq = [abs(filtered[i] - mean) for i in range(0, len(filtered))]
        residual_mean = sum(sq) / len(sq)
        residual_std = sum([(x - residual_mean) ** 2 for x in sq]) / len(sq)
        logging.info(" Inferred epsilon %r with standard deviation of %r"%(residual_mean,residual_std))
        return(residual_mean)

    def write_info_dic_as_csv(self, outPath, results):
        create_file(outPath, list(results.get_stats()[0][0].keys()))
        for i in results.get_stats():
            write_on_file_contents(outPath, i)



