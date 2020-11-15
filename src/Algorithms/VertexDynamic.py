from src.Graphs.Objects.MultipleEdge import DynamicGraph
from src.FileOperations.WriteOnFile import create_file, create_folder, write_on_file_contents
from src.StastModules.Snapshot import get_snapshot_dynamic
import time
import math as mt


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

    def run(self):
        print("Starting simulation ")
        sim_start = time.time()
        for inrate in self.inrate_list:
            for outrate in self.outrate_list:
                print("Inrate: ", inrate, " Outrate: ", outrate, " Flooding: ", self.flooding)
                outpath = create_folder(self.outPath,
                                        "VertexDynamic_in_" + str(inrate) + "_out_" + str(outrate) + "_f_" + str(
                                            self.flooding))
                outpath = outpath + "results"
                vertexDynamicStats = VertexDynamicOutput()
                for d in self.d_list:
                    for c in self.c_list:
                        for sim in range(0, self.simNumber):
                            print("Simulation: ", sim)
                            start_time = time.time()
                            stats = self.VertexDynamicGenerator(d, c, inrate, outrate, sim)
                            vertexDynamicStats.add_stats(stats)
                            # vertexDynamicStats.add_flood_infos(flood_info)
                            print("Elapsed time: ", time.time() - start_time)
                self.write_info_dic_as_csv(outpath, vertexDynamicStats)
        print("Ending simulation")
        print("Elapsed time : ", time.time() - sim_start)

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
                if (semireg >= len(nodi) * G.get_semiregular_percentage()):

                    if (G.get_a() == 0 and G.get_b() == 100):
                        G.set_converged(True)
                        print(" Structural convergence at ", (G.get_semiregular_percentage())*100, "%")
                    else:
                        # print("(d,cd)-regular = ", semireg, " perc of vertices = ",
                        #     len(nodi) * (self.cdPercentage - (G.get_reset_number() * self.decay)))
                        a = G.get_a()
                        b = G.get_b()

                        if (a == b):
                            G.set_converged(True)
                            print("----------------------------------------------------------------")
                            print(" Structural convergence at ", (G.get_semiregular_percentage())*100, "%")
                            print("----------------------------------------------------------------")
                        else:

                            G.get_percentage(True)
                            print("Increasing (d,cd)-regularity range to ", G.get_a()  ," - ", G.get_b(), "%")
                        # G.set_semiregular_percentage((self.cdPercentage - (G.get_reset_number() * self.decay)))
                elif (G.get_time_conv() > 2 * G.get_target_n()):
                    a = G.get_a()
                    b = G.get_b()
                    if (a == b):
                        G.set_converged(True)
                        print("----------------------------------------------------------------")
                        print(" Structural convergence at " , (G.get_semiregular_percentage())*100, "%")
                        print("----------------------------------------------------------------")
                    else:
                        G.get_percentage(False)

                    #print(mt.floor(mt.log(G.get_target_n())))
                    G.reset_time_conv()


                    # print("Lowering (d,cd)-regularity to ", (self.cdPercentage - (G.get_reset_number() * self.decay)))
                    print("Lowering (d,cd)-regularity range to ", G.get_a() ," - ", G.get_b(), "%")

            flood_dictionary = {}
            if (G.get_converged()):
                if (G.flooding.get_initiator() == -1):
                    G.set_flooding()
                    G.flooding.set_initiator()
                    G.flooding.update_flooding(G)
                else:
                    # Updating Flooding
                    if (G.flooding.get_t_flood() == 1):
                        print(" Flooding Protocol STARTED", G.flooding.get_started())
                    if (G.flooding.get_started() == True):
                        G.flooding.update_flooding(G)

                        if (not G.flooding.check_flooding_status()):
                            G.set_converged(True)
                            G.flooding.set_converged(False)
                            if (G.flooding.get_number_of_restart() == 0):
                                print(" Number of attempts: ", 1, " FLOODING PROTOCOL FAILED")
                                print("END of the simulation")
                                G.flooding.set_converged(False)
                                G.flooding.set_failed(True)
                        G.flooding.is_informed()
                        if (G.flooding.get_converged()):
                            print("--- ALL NODES IN THE NETWORK ARE INFORMED ---\n\n")

                        if (G.flooding.get_t_flood() > G.get_target_n()):
                            print(" The Flooding protocol is too slow, stopping the simulation")
                            print("Number of informed nodes: ", G.flooding.get_informed_nodes())
                            G.set_converged(True)
                            G.flooding.set_converged(False)
                            G.flooding.set_failed(True)

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
        achieved = False

        repeat = True
        sim = {
            "simulation": sim
        }
        if (d <= 0 or c < 0):
            print("Error, input parameters must be: d>0 c>1")
            return (-1)
        G = DynamicGraph(0, d, c, inrate, outrate, 0, self.model)
        while (repeat):
            G.connect_to_network()
            G.add_phase()
            G.del_phase()
            G.disconnect_from_network()
            if (not achieved):
                if (G.get_target_density()):
                    print("----------------------------------------------------------------")
                    print(" The Graph contains the desired number of nodes ")
                    print("----------------------------------------------------------------")
                    achieved = True
                    stats = get_snapshot_dynamic(G, G.get_d(), G.get_c(), t)
                    #conv_perc = {"conv_percentage": (self.cdPercentage - (G.get_reset_number() * self.decay))}
                    conv_perc = {"conv_percentage": (G.get_semiregular_percentage())}
                    flood_info = check_convergence_dynamic()
                    final_stats.append({**sim, **conv_perc, **stats, **flood_info})
            else:
                #conv_perc = {"conv_percentage": (self.cdPercentage - (G.get_reset_number() * self.decay))}
                conv_perc = {"conv_percentage": (G.get_semiregular_percentage())}
                stats = get_snapshot_dynamic(G, G.get_d(), G.get_c(), t)
                flood_info = check_convergence_dynamic()
                final_stats.append({**sim, **conv_perc, **stats, **flood_info})
            t += 1

            if (G.flooding.get_converged() and (not (G.flooding.get_failed()))):
                repeat = False
            # if ((self.cdPercentage - (G.get_reset_number() * self.decay)) <= -1):
            #     print("The graph does not converge")
            #     repeat = False
            if (G.flooding.get_failed()):
                repeat = False
                print("Flooding Protocol status : FAILED")
        return (final_stats)

    def write_info_dic_as_csv(self, outPath, results):
        create_file(outPath, list(results.get_stats()[0][0].keys()))
        for i in results.get_stats():
            write_on_file_contents(outPath, i)
