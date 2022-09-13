import networkx as nx

from src.Graphs.Objects.MultipleEdge import DynamicGraph
from src.FileOperations.WriteOnFile import create_file, create_folder, write_on_file_contents
from src.StastModules.Snapshot import get_snapshot_dynamic,get_snapshot_dynamicND
from src.StastModules.SpectralAnalysis import spectral_gap_sparse

import time
import math as mt
import logging
import os
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

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


class VertexDynamic:

    def __init__(self, d, c, inrate, outrate, outpath, flooding=True, regular_convergence=0.9, regular_decay=0.5
                 , model="Multiple", simNumber=30, maxIter=100, onlySpectral=False, Offline=False, GPU=False):
        """




        :param d: int, minimum degree that each node must have
        :param c: float, tolerance constant, c*d is the maximum degree that each node can have
        :param inrate: float, intensity parameter of the Poisson Process
        :param outrate: float, node-falling probability
        :param outpath: str, output path for the results
        :param flooding: bool, if True, simulates the flooding process
        :param regular_convergence: Threshold for the (d,c*d)-regularity convergence, NOTE: The Algorithm will compute the best percentage anyway.
        :param model: str, if Multiple each node will sample more than one node at each round, NOTE: Leave it as Multiple
        :param simNumber: int, number of experiments to perfom
        :param maxIter: int, maximum number of steps for the simulations
        :param onlySpectral: bool, if true will save only the spectral properties of the graph
        :param Offline: bool, if true, will simulate the model saving the adjacency list of the model at each time step without computing any statistic
        :param GPU: bool, if true, will be used the GPU instead of the CPU for solving the eigen-problem
        """
        self.d_list = d
        self.c_list = c
        self.inrate_list = inrate
        self.outrate_list = outrate
        self.flooding = flooding
        self.decay = regular_decay
        self.cdPercentage = regular_convergence
        self.model = model
        self.outPath = outpath
        self.simNumber = simNumber
        self.spectrum = onlySpectral
        self.MC = Offline
        self.max_iter = maxIter
        self.GPU = GPU

    def run(self):
        logging.info("----------------------------------------------------------------")
        logging.info("Starting simulation")
        sim_start = time.time()
        for inrate in self.inrate_list:
            for outrate in self.outrate_list:
                logging.info("----------------------------------------------------------------")
                logging.info("Inrate: %r Outrate: %r Flooding: %r" % (inrate, outrate,self.flooding ))
                outpath = create_folder(self.outPath,
                                        "VertexDynamic_in_" + str(inrate) + "_out_" + str(outrate) + "_f_" + str(
                                            self.flooding))
                path = outpath
                outpath = outpath + "results"
                vertexDynamicStats = VertexDynamicOutput()
                for d in self.d_list:
                    logging.info("Inrate: %r Outrate: %r Flooding %r d: %d" % (inrate,outrate,self.flooding,d))
                    #print("Inrate: ", inrate, " Outrate: ", outrate, " Flooding: ", self.flooding, "d: ",d)
                    for c in self.c_list:
                        logging.info("Inrate: %r Outrate: %r Flooding %r d: %d c: %r " % (inrate,outrate,self.flooding,d,c))
                        #print("Inrate: ", inrate, " Outrate: ", outrate, " Flooding: ", self.flooding, " d: ",d," c: ",c)
                        for sim in range(0, self.simNumber):
                            logging.info("Simulation %d" % (sim))
                            start_time = time.time()
                            if(self.spectrum):
                                stats = self.VertexDynamicGeneratorSpectrum(d, c, inrate, outrate, sim,path = path  )
                            elif(self.MC):
                                stats = self.VertexDynamicGeneratorMCConfigurations( d, c, inrate, outrate, sim, path=path)

                            else:
                                stats = self.VertexDynamicGenerator(d, c, inrate, outrate, sim)
                            vertexDynamicStats.add_stats(stats)
                            logging.info("Elapsed time %r" % (time.time() - start_time))
                            logging.info("----------------------------------------------------------------")
                self.write_info_dic_as_csv(outpath, vertexDynamicStats)
        logging.info("Ending simulation")
        logging.info("Total elapsed time %r" % (time.time() - sim_start))


    def VertexDynamicGenerator(self, d, c, inrate, outrate, sim):

        def check_convergence_dynamic():

            if (G.get_converged() == False):
                # Getting the number of the vertices with less than d neighbours
                # Number of the nodes with a degree >=d and <= cd
                semireg = 0
                # Number of nodes with a degree <d
                underreg = 0
                # Number of nodes with a degree >cd
                overreg = 0
                nodi = list(G.get_G().nodes())
                for u in nodi:
                    if (G.get_G().degree(u) < G.get_d()):
                        underreg += 1
                    elif (G.get_G().degree(u) > G.get_tolerance()):
                        overreg += 1
                    else:
                        semireg += 1
                G.increment_time_conv()

                # if (semireg >= len(nodi) * (self.cdPercentage - (G.get_reset_number() * self.decay))):
                percentages = [i for i in range(0,101)]
                G.set_semiregular_percentage(percentages[-1])

                if (semireg >= len(nodi) * G.get_semiregular_percentage()):
                    G.set_converged(True)
                else:
                    a = 0
                    b = 100
                    while(a<=b):
                        m = ((b+a) / 2)
                        G.set_semiregular_percentage(m)
                        if(semireg >= len(nodi) * G.get_semiregular_percentage()):
                            a = m + 1
                        else:
                            b = m - 1

                    logging.info("Structural convergence at %r "%(G.get_semiregular_percentage() * 100))
                    G.set_converged(True)



            flood_dictionary = {}
            if (G.get_converged()):
                if (G.flooding.get_initiator() == -1):
                    G.set_flooding()
                    G.flooding.set_stop_time(mt.floor(mt.log(G.get_target_n(),2)))
                    G.flooding.set_initiator()
                    G.flooding.update_flooding(G)
                else:

                    # Updating Flooding
                    if (G.flooding.get_t_flood() == 1):
                        logging.info("Flooding protocol STARTED %r"%(G.flooding.get_started()))
                    if (G.flooding.get_started() == True):
                        G.flooding.update_flooding(G)

                        if (not G.flooding.check_flooding_status()):
                            G.set_converged(True)
                            if (G.flooding.get_number_of_restart() == 0):
                                logging.info("All the informed nodes left the network")
                                logging.info("Flooding Protocol status: Failed")
                                logging.info("----------------------------------------------------------------")
                                G.flooding.set_converged(False)
                                G.flooding.set_failed(True)
                        if (G.flooding.get_converged()):
                            logging.info("AL NODES IN THE NETWORK ARE INFORMED")
                            logging.info("Number of informed nodes %d" % (G.flooding.get_informed_nodes()))
                            logging.info("Number of uninformed nodes %d " %(G.flooding.get_uninformed_nodes()))
                            logging.info("Percentage of informed nodes %r" % (G.flooding.get_percentage()))
                            logging.info("Informed Ratio: %r"%(G.flooding.get_last_ratio()))
                            logging.info("Flooding Protocol status: Correctly Terminated")
                            logging.info("Flooding time: %d" %(G.flooding.get_t_flood()))
                            logging.info("----------------------------------------------------------------")

                        threshold = G.get_target_n()
                        if (G.flooding.get_t_flood() >100* threshold):
                            logging.info("Iterations > threshold")
                            logging.info("The Flooding protocol is too slow, stopping the simulation")
                            logging.info("Number of informed nodes %d " % (G.flooding.get_informed_nodes()))
                            logging.info("Number of uninformed nodes %d " %(G.flooding.get_uninformed_nodes()))
                            logging.info("Percentage of informed nodes %r" % (G.flooding.get_percentage()))
                            logging.info("Informed Ratio: %r"%(G.flooding.get_last_ratio()))
                            logging.info("Flooding Protocol status: Failed")
                            logging.info("Number of executed steps: %d  Step threshold: %d" % (
                            G.flooding.get_t_flood(), threshold))
                            logging.info("----------------------------------------------------------------")
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
            logging.error("Input parameters must be: d>0 c>1")
            return (-1)
        G = DynamicGraph(0, d, c, inrate, outrate, 0, self.model)
        while (repeat):
            G.disconnect_from_network()
            G.connect_to_network()

            G.add_phase_vd()


            G.del_phase_vd()

            if (not achieved):
                if (G.get_target_density()):
                    logging.info("The Graph contains the desired number of nodes")
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
            if ((self.cdPercentage - (G.get_reset_number() * self.decay)) <= -1):
                logging.info("The graph does not converge")
                repeat = False
            if (G.flooding.get_failed()):
                repeat = False
                logging.info("Flooding protocol: FAILED")
        return (final_stats)

    def VertexDynamicGeneratorMCConfigurations(self, d, c, inrate, outrate, sim,path=""):
        def check_convergence_dynamic():

            if (G.get_converged() == False):
                # Getting the number of the vertices with less than d neighbours
                # Number of the nodes with a degree >=d and <= cd
                semireg = 0
                # Number of nodes with a degree <d
                underreg = 0
                # Number of nodes with a degree >cd
                overreg = 0
                nodi = list(G.get_G().nodes())
                for u in nodi:
                    if (G.get_G().degree(u) < G.get_d()):
                        underreg += 1
                    elif (G.get_G().degree(u) > G.get_tolerance()):
                        overreg += 1
                    else:
                        semireg += 1
                G.increment_time_conv()

                # if (semireg >= len(nodi) * (self.cdPercentage - (G.get_reset_number() * self.decay))):
                percentages = [i for i in range(0,101)]
                G.set_semiregular_percentage(percentages[-1])

                if (semireg >= len(nodi) * G.get_semiregular_percentage()):
                    G.set_converged(True)
                    logging.info("Structural convergence at %r "%(G.get_semiregular_percentage() * 100))

                else:
                    a = 0
                    b = 100
                    while(a<=b):
                        m = ((b+a) / 2)
                        G.set_semiregular_percentage(m)
                        if(semireg >= len(nodi) * G.get_semiregular_percentage()):
                            a = m + 1
                        else:
                            b = m - 1

                    logging.info("Structural convergence at %r "%(G.get_semiregular_percentage() * 100))
                    G.set_converged(True)

        try:
            # Create sim Directory
            os.mkdir(path + "/" + str(sim))
            logging.info("Directory %r sim  Created " % (path))
        except FileExistsError:
            logging.error("Directory %r sim already exists" % (path))

        try:
            # Create sim Directory
            os.mkdir(path + "/" + str(sim) + "/beforeA")
            logging.info("Directory %r sim/before Created " % (path))
        except FileExistsError:
            logging.error("Directory %r sim/before already exists" % (path))

        try:
            # Create sim Directory
            os.mkdir(path + "/" + str(sim) + "/before")
            logging.info("Directory %r sim/before Created " % (path))
        except FileExistsError:
            logging.error("Directory %r sim/before already exists" % (path))
        try:
            # Create sim Directory
            os.mkdir(path + "/" + str(sim) + "/afterA")
            logging.info("Directory %r sim/after Created " % (path))
        except FileExistsError:
            logging.error("Directory %r sim/after already exists" % (path))

        try:
            # Create sim Directory
            os.mkdir(path + "/" + str(sim) + "/after")
            logging.info("Directory %r sim/after Created " % (path))
        except FileExistsError:
            logging.error("Directory %r sim/after already exists" % (path))

        t = 0


        achieved = False

        repeat = True

        if (d <= 0 or c < 0):
            logging.error("Input parameters must be: d>0 c>1")
            return (-1)
        G = DynamicGraph(0, d, c, inrate, outrate, 0, self.model)
        c = 0
        stats = {"d": G.get_d(), "c": G.get_c(), "n": G.get_target_n(),"lambda":G.get_inrate(),"beta":G.get_outrate()}

        while (repeat):
            G.disconnect_from_network()
            # Saving graph
            nx.write_adjlist(G.get_G(), path=path + str(sim) + "/afterA/" + str(t) + ".adjlist")

            G.connect_to_network()
            nx.write_adjlist(G.get_G(), path=path + str(sim) + "/beforeA/" + str(t) + ".adjlist")

            G.add_phase_vd()
            nx.write_adjlist(G.get_G(), path=path + str(sim) + "/before/" + str(t) + ".adjlist")


            G.del_phase_vd()
            # Saving graph
            nx.write_adjlist(G.get_G(), path=path + str(sim) + "/after/" + str(t) + ".adjlist")



            if (not achieved):
                if (G.get_target_density()):
                    logging.info("The Graph contains the desired number of nodes")

                    achieved = True
                    check_convergence_dynamic()



            else:
                check_convergence_dynamic()
            t += 1
            if(G.get_converged()):


                if(c == self.max_iter):
                    repeat = False

                    logging.info("Graph converged and 100 more steps simulated")
                else:

                    c+=1

        stats3 = [stats, stats]
        return (stats3)







    def VertexDynamicGeneratorSpectrum(self, d, c, inrate, outrate, sim,path=""):

        def check_convergence_dynamic():

            if (G.get_converged() == False):
                # Getting the number of the vertices with less than d neighbours
                # Number of the nodes with a degree >=d and <= cd
                semireg = 0
                # Number of nodes with a degree <d
                underreg = 0
                # Number of nodes with a degree >cd
                overreg = 0
                nodi = list(G.get_G().nodes())
                for u in nodi:
                    if (G.get_G().degree(u) < G.get_d()):
                        underreg += 1
                    elif (G.get_G().degree(u) > G.get_tolerance()):
                        overreg += 1
                    else:
                        semireg += 1
                G.increment_time_conv()

                percentages = [i for i in range(0,101)]
                G.set_semiregular_percentage(percentages[-1])

                if (semireg >= len(nodi) * G.get_semiregular_percentage()):
                    G.set_converged(True)
                    logging.info("Structural convergence at %r "%(G.get_semiregular_percentage() * 100))

                else:
                    a = 0
                    b = 100
                    while(a<=b):
                        m = ((b+a) / 2)
                        G.set_semiregular_percentage(m)
                        if(semireg >= len(nodi) * G.get_semiregular_percentage()):
                            a = m + 1
                        else:
                            b = m - 1

                    logging.info("Structural convergence at %r "%(G.get_semiregular_percentage() * 100))
                    G.set_converged(True)



        t = 0


        final_stats = []
        achieved = False

        repeat = True
        sim = {
            "simulation": sim
        }
        if (d <= 0 or c < 0):
            logging.error("Input parameters must be: d>0 c>1")
            return (-1)
        G = DynamicGraph(0, d, c, inrate, outrate, 0, self.model)
        c = 0

        while (repeat):
            G.disconnect_from_network()
            if (achieved):

                spectralGapBefore = spectral_gap_sparse(G.get_G())
                spectralGapBefore = {"SpectralGapBefore": spectralGapBefore}
            else:

                spectralGapBefore = spectral_gap_sparse(G.get_G())
                spectralGapBefore = {"SpectralGapBefore": spectralGapBefore}




            G.connect_to_network()

            G.add_phase_vd()



            G.del_phase_vd()



            if (not achieved):
                if (G.get_target_density()):
                    logging.info("The Graph contains the desired number of nodes")
                    achieved = True
                    stats = get_snapshot_dynamicND(G, G.get_d(), G.get_c(), t)
                    check_convergence_dynamic()
                    conv_perc = {"conv_percentage": (G.get_semiregular_percentage())}

                    spectralGapAfter = spectral_gap_sparse(G.get_G())
                    spectralGapsAfter = {"SpectralGapAfter":spectralGapAfter}
                    #spectralGapBefore = {'SpectralGapBefore':0}
                    final_stats.append({**sim, **conv_perc, **stats,**spectralGapBefore,**spectralGapsAfter})

            else:
                stats = get_snapshot_dynamicND(G, G.get_d(), G.get_c(), t)
                check_convergence_dynamic()
                conv_perc = {"conv_percentage": (G.get_semiregular_percentage())}

                spectralGapAfter = spectral_gap_sparse(G.get_G())
                spectralGapsAfter = {"SpectralGapAfter": spectralGapAfter}
                final_stats.append({**sim, **conv_perc, **stats,**spectralGapBefore,**spectralGapsAfter})
            t += 1
            if(G.get_converged()):


                if(c == self.max_iter):
                    repeat = False

                    logging.info("Graph converged and 100 more steps simulated")
                else:
                    c+=1
            logging.info("Simulation %r | Step %r/%r | Spectral Gap converged? %r"%(sim['simulation'],t,self.max_iter,G.get_converged()))


        return (final_stats)


    def write_info_dic_as_csv(self, outPath, results):
        create_file(outPath, list(results.get_stats()[0][0].keys()))
        for i in results.get_stats():
            write_on_file_contents(outPath, i)