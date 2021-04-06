from src.Graphs.Objects.MultipleEdge import DynamicGraph
from src.FileOperations.WriteOnFile import create_file, create_folder, write_on_file_contents
from src.StastModules.Snapshot import get_snapshot_dynamic,get_snapshot_dynamicND
from src.StastModules.SpectralAnalysis import get_spectral_gap_transition_matrix

import time
import math as mt
import logging
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
                 , model="Multiple", simNumber=30):
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
        self.spectrum = False

    def run(self):
        logging.info("----------------------------------------------------------------")
        logging.info("Starting simulation")
        #print("Starting simulation ")
        sim_start = time.time()
        for inrate in self.inrate_list:
            for outrate in self.outrate_list:
                logging.info("----------------------------------------------------------------")
                logging.info("Inrate: %d Outrate: %r Flooding: %r" % (inrate, outrate,self.flooding ))
                #print("Inrate: ", inrate, " Outrate: ", outrate, " Flooding: ", self.flooding)
                outpath = create_folder(self.outPath,
                                        "VertexDynamic_in_" + str(inrate) + "_out_" + str(outrate) + "_f_" + str(
                                            self.flooding))
                outpath = outpath + "results"
                vertexDynamicStats = VertexDynamicOutput()
                for d in self.d_list:
                    logging.info("Inrate: %d Outrate: %r Flooding %r d: %d" % (inrate,outrate,self.flooding,d))
                    #print("Inrate: ", inrate, " Outrate: ", outrate, " Flooding: ", self.flooding, "d: ",d)
                    for c in self.c_list:
                        logging.info("Inrate: %d Outrate: %r Flooding %r d: %d c: %r " % (inrate,outrate,self.flooding,d,c))
                        #print("Inrate: ", inrate, " Outrate: ", outrate, " Flooding: ", self.flooding, " d: ",d," c: ",c)
                        for sim in range(0, self.simNumber):
                            logging.info("Simulation %d" % (sim))
                            #print("Simulation: ", sim)
                            start_time = time.time()
                            if(self.spectrum):
                                stats = self.VertexDynamicGeneratorSpectrum(d, c, inrate, outrate, sim)
                            else:
                                stats = self.VertexDynamicGenerator(d, c, inrate, outrate, sim)
                            vertexDynamicStats.add_stats(stats)
                            # vertexDynamicStats.add_flood_infos(flood_info)
                            logging.info("Elapsed time %r" % (time.time() - start_time))
                            logging.info("----------------------------------------------------------------")
                            #print("Elapsed time: ", time.time() - start_time)
                self.write_info_dic_as_csv(outpath, vertexDynamicStats)
        logging.info("Ending simulation")
        logging.info("Total elapsed time %r" % (time.time() - sim_start))
        #print("Ending simulation")
        #print("Elapsed time : ", time.time() - sim_start)

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
                        #print("Nodi semireg = ", semireg, " Percentuale = ",G.get_semiregular_percentage(),"Nodi rete",len(nodi), " Nodi perc nodi = ",len(nodi) * G.get_semiregular_percentage())
                        if(semireg >= len(nodi) * G.get_semiregular_percentage()):
                            a = m + 1
                            #print("Increasing (d,cd)-regularity range to ", a, " - ",b, "%")
                        else:
                            b = m - 1
                            #print("Lowering (d,cd)-regularity range to ", a, " - ",b, "%")

                    logging.info("Structural convergence at %r "%(G.get_semiregular_percentage() * 100))
                    #print("Structural convergence at ", (G.get_semiregular_percentage()) * 100, "%")
                    #print("----------------------------------------------------------------")
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
                        #print("Flooding Protocol STARTED", G.flooding.get_started())
                        #print("----------------------------------------------------------------")
                    if (G.flooding.get_started() == True):
                        G.flooding.update_flooding(G)

                        if (not G.flooding.check_flooding_status()):
                            G.set_converged(True)
                            #G.flooding.set_converged(False)
                            if (G.flooding.get_number_of_restart() == 0):
                                logging.info("All the informed nodes left the network")
                                logging.info("Flooding Protocol status: Failed")
                                #logging.info("Number of attempts 1 FLOODING PROTOCOL FAILED")
                                #logging.info("END of the simulation")
                                logging.info("----------------------------------------------------------------")
                                #print("Number of attempts: ", 1, " FLOODING PROTOCOL FAILED")
                                #print("END of the simulation")
                                #print("----------------------------------------------------------------")
                                G.flooding.set_converged(False)
                                G.flooding.set_failed(True)
                        #G.flooding.terminated()
                        if (G.flooding.get_converged()):
                            #logging.info("\t FLOODING INFOS")
                            logging.info("AL NODES IN THE NETWORK ARE INFORMED")
                            logging.info("Number of informed nodes %d" % (G.flooding.get_informed_nodes()))
                            logging.info("Number of uninformed nodes %d " %(G.flooding.get_uninformed_nodes()))
                            logging.info("Percentage of informed nodes %r" % (G.flooding.get_percentage()))
                            logging.info("Informed Ratio: %r"%(G.flooding.get_last_ratio()))
                            logging.info("Flooding Protocol status: Correctly Terminated")
                            logging.info("Flooding time: %d" %(G.flooding.get_t_flood()))
                            logging.info("----------------------------------------------------------------")
                            #print("--- ALL NODES IN THE NETWORK ARE INFORMED ---")

                            #print("Flooding Protocol status : TERMINATED\n\n")
                            #print("----------------------------------------------------------------")
                        #threshold = 2* mt.floor(mt.log(G.get_target_n(),2))
                        threshold = G.get_target_n()
                        if (G.flooding.get_t_flood() > threshold):
                            logging.info("Iterations > threshold")
                            #logging.info("\t FLOODING INFOS")
                            logging.info("The Flooding protocol is too slow, stopping the simulation")
                            logging.info("Number of informed nodes %d " % (G.flooding.get_informed_nodes()))
                            logging.info("Number of uninformed nodes %d " %(G.flooding.get_uninformed_nodes()))
                            logging.info("Percentage of informed nodes %r" % (G.flooding.get_percentage()))
                            logging.info("Informed Ratio: %r"%(G.flooding.get_last_ratio()))
                            logging.info("Flooding Protocol status: Failed")
                            logging.info("Number of executed steps: %d  Step threshold: %d" % (
                            G.flooding.get_t_flood(), threshold))
                            logging.info("----------------------------------------------------------------")
                            #print("The Flooding protocol is too slow, stopping the simulation")
                            #print("Number of informed nodes: ", G.flooding.get_informed_nodes())
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
            logging.error("Input parameters must be: d>0 c>1")
            #print("Error, input parameters must be: d>0 c>1")
            return (-1)
        G = DynamicGraph(0, d, c, inrate, outrate, 0, self.model)
        while (repeat):
            G.disconnect_from_network()
            G.connect_to_network()
            #G.disconnect_from_network()
            # 1) Entrano nuovi nodi
            # 2) Escono dei nodi
            # 3) I nodi al presenti nel grafo anche al tempo I-1 fanno raes tra di loro
            # 4) I nodi che sono entrati al tempo I fanno raes verso quelli al tempo I-1
            # NOTA 3)-4) deve essere in parallelo non seriale
            # 5) Esegui flooding step sul grafo al tempo I
            G.add_phase_vd()

            #G.add_phase_MT()
            #G.del_phase_MT()

            G.del_phase_vd()

            if (not achieved):
                if (G.get_target_density()):
                    logging.info("The Graph contains the desired number of nodes")
                    #print("----------------------------------------------------------------")
                    #print("The Graph contains the desired number of nodes ")
                    #print("----------------------------------------------------------------")
                    achieved = True
                    stats = get_snapshot_dynamic(G, G.get_d(), G.get_c(), t)
                    #conv_perc = {"conv_percentage": (self.cdPercentage - (G.get_reset_number() * self.decay))}
                    flood_info = check_convergence_dynamic()
                    conv_perc = {"conv_percentage": (G.get_semiregular_percentage())}
                    final_stats.append({**sim, **conv_perc, **stats, **flood_info})
            else:
                #conv_perc = {"conv_percentage": (self.cdPercentage - (G.get_reset_number() * self.decay))}
                stats = get_snapshot_dynamic(G, G.get_d(), G.get_c(), t)
                flood_info = check_convergence_dynamic()
                conv_perc = {"conv_percentage": (G.get_semiregular_percentage())}
                final_stats.append({**sim, **conv_perc, **stats, **flood_info})
            t += 1
            #print("REP = ",repeat)
            #print("CONV = ",G.flooding.get_converged())
            #print("GET FAIL ",not(G.flooding.get_failed()))

            if (G.flooding.get_converged() and (not (G.flooding.get_failed()))):
                repeat = False
            if ((self.cdPercentage - (G.get_reset_number() * self.decay)) <= -1):
                logging.info("The graph does not converge")
                #print("The graph does not converge")
                repeat = False
            if (G.flooding.get_failed()):
                repeat = False
                logging.info("Flooding protocol: FAILED")
                #print("Flooding Protocol status : FAILED")
                #print("----------------------------------------------------------------")
        return (final_stats)


    def VertexDynamicGeneratorSpectrum(self, d, c, inrate, outrate, sim):

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
                        #print("Nodi semireg = ", semireg, " Percentuale = ",G.get_semiregular_percentage(),"Nodi rete",len(nodi), " Nodi perc nodi = ",len(nodi) * G.get_semiregular_percentage())
                        if(semireg >= len(nodi) * G.get_semiregular_percentage()):
                            a = m + 1
                            #print("Increasing (d,cd)-regularity range to ", a, " - ",b, "%")
                        else:
                            b = m - 1
                            #print("Lowering (d,cd)-regularity range to ", a, " - ",b, "%")

                    logging.info("Structural convergence at %r "%(G.get_semiregular_percentage() * 100))
                    #print("Structural convergence at ", (G.get_semiregular_percentage()) * 100, "%")
                    #print("----------------------------------------------------------------")
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
            #print("Error, input parameters must be: d>0 c>1")
            return (-1)
        G = DynamicGraph(0, d, c, inrate, outrate, 0, self.model)
        c = 0
        while (repeat):
            G.disconnect_from_network()
            if (achieved):
                Isinvertible, spectralGap, lambdaNGap = get_spectral_gap_transition_matrix(G.get_G())
                spectralGapBefore = {"SpectralGapBefore": spectralGap}

            G.connect_to_network()
            # 1) Entrano nuovi nodi
            # 2) Escono dei nodi
            # 3) I nodi al presenti nel grafo anche al tempo I-1 fanno raes tra di loro
            # 4) I nodi che sono entrati al tempo I fanno raes verso quelli al tempo I-1
            # NOTA 3)-4) deve essere in parallelo non seriale
            # 5) Esegui flooding step sul grafo al tempo I
            G.add_phase_vd()

            #G.add_phase_MT()
            #G.del_phase_MT()

            G.del_phase_vd()

            if (not achieved):
                if (G.get_target_density()):
                    logging.info("The Graph contains the desired number of nodes")
                    #print("----------------------------------------------------------------")
                    #print("The Graph contains the desired number of nodes ")
                    #print("----------------------------------------------------------------")
                    achieved = True
                    stats = get_snapshot_dynamicND(G, G.get_d(), G.get_c(), t)
                    check_convergence_dynamic()
                    #conv_perc = {"conv_percentage": (self.cdPercentage - (G.get_reset_number() * self.decay))}
                    conv_perc = {"conv_percentage": (G.get_semiregular_percentage())}
                    Isinvertible, spectralGap, lambdaNGap = get_spectral_gap_transition_matrix(G.get_G())
                    spectralGaps = {"SpectralGap":spectralGap}
                    spectralGapBefore = {'SpectralGapBefore':0}
                    final_stats.append({**sim, **conv_perc, **stats,**spectralGapBefore,**spectralGaps})

                # else:
                #     conv_perc = {"conv_percentage":-1}
                #     stats = get_snapshot_dynamicND(G, G.get_d(), G.get_c(), t)
                #
                #     Isinvertible, spectralGap, lambdaNGap = get_spectral_gap_transition_matrix(G.get_G())
                #     spectralGaps = {"SpectralGap": spectralGap}
                #     final_stats.append({**sim, **conv_perc, **stats, **spectralGaps})
            else:
                #conv_perc = {"conv_percentage": (self.cdPercentage - (G.get_reset_number() * self.decay))}
                stats = get_snapshot_dynamicND(G, G.get_d(), G.get_c(), t)
                check_convergence_dynamic()
                conv_perc = {"conv_percentage": (G.get_semiregular_percentage())}
                Isinvertible, spectralGap, lambdaNGap = get_spectral_gap_transition_matrix(G.get_G())
                spectralGaps = {"SpectralGap": spectralGap}
                final_stats.append({**sim, **conv_perc, **stats,**spectralGapBefore,**spectralGaps})
            t += 1
            if(G.get_converged()):


                if(c == 100):
                    repeat = False

                    logging.info("Graph converged and 100 more steps simulated")
                else:
                    #logging.info("Step %r "%c)

                    c+=1

        return (final_stats)


    def write_info_dic_as_csv(self, outPath, results):
        create_file(outPath, list(results.get_stats()[0][0].keys()))
        for i in results.get_stats():
            write_on_file_contents(outPath, i)