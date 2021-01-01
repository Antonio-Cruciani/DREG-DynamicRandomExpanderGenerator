import math as mt
import numpy as np
import rpy2.robjects as ro
import matplotlib.ticker as mtick
import matplotlib.pyplot as pl
from itertools import groupby
import os
from src.FileOperations.WriteOnFile import create_folder
import logging
#logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

class Samples:

    # samples must be a pack of experiments regarding the same d,c,r,q,p
    def __init__(self,samples,outpath):

        #self.inputPath = inpath
        self.outputPathPlottings = outpath
        self.outputPathCSV = outpath
        self.samples = samples

        self.graph = None
        self.d = None
        self.c = None
        self.r = None
        self.q = None
        self.p = None
        self.number_of_simulations = None
        self.n = None

        # Must be set to log2 n
        self.desidered_flooding_time = None
        self.desidered_diameter = None


        self.infer_experiment_infos()


        # Averages, standard deviations, residual values and t tests

        self.avg_n = None
        self.std_n = None

        self.avg_flooding_time = None
        self.std_flooding_time = None
        self.avg_flooding_convergence_percentage = None
        self.std_flooding_convergence_percentage = None

        self.avg_diameter = None
        self.std_diameter = None
        self.avg_disconnected = None
        self.std_disconnected = None

        self.avg_semiregularity = None
        self.std_semiregularity = None
        self.avg_semiregularity_convergence_percentage = None
        self.std_semiregularity_convergence_percentage = None

        self.residual_flooding_time = None
        self.residual_diameter = None

        self.confidence_level = 95
        self.t_test_type = "two.sided"
        self.paired = False
        self.t_test_flooding_time = None
        self.t_test_diameter = None

        self.flooding_convergence_percentage_in_each_sim = []
        self.flooding_in_each_sim = []
        self.semiregualrity_in_each_sim = []
        self.nodes_in_each_sim = []

        self.stats_summary = {}
        # Plotting variables

        #self.nodes = []


    def all_equal(self,iterable):
        g = groupby(iterable)
        return next(g, True) and not next(g, False)

    def percent(self,num1, num2):
        num1 = float(num1)
        num2 = float(num2)
        percentage = '{0:.2f}'.format((num1 / num2 * 100))
        return float(percentage)
    # H0 = media è esattamente log2 n
    # H1 = media non è esattamente log2 n
    def get_t_test_flooding_time(self,samples):
        if(len(samples)>1):
            if (self.all_equal(samples)):
                self.t_test_diameter = 1
            else:
                x_avg_flooding_time = ro.vectors.FloatVector(samples)
                ttest = ro.r['t.test']
                result = ttest(x_avg_flooding_time, mu=self.desidered_flooding_time, paired=self.paired,
                                                  alternative=self.t_test_type, conflevel=self.confidence_level)
                self.t_test_flooding_time = result.rx2('p.value')[0]
        else:
            self.t_test_flooding_time = 0
    def get_t_test_diameter(self,samples):
        if(len(samples)>1):
            if(self.all_equal(samples)):
                self.t_test_diameter = 1
            else:
                x_avg_diameter = ro.vectors.FloatVector(samples)
                ttest = ro.r['t.test']
                result = ttest(x_avg_diameter, mu=self.desidered_diameter, paired=self.paired,
                                                 alternative=self.t_test_type, conflevel=self.confidence_level)
                self.t_test_diameter = result.rx2('p.value')[0]
        else:
            self.t_test_diameter = 0

    def get_residual_flooding_time(self):
        self.residual_flooding_time = ((self.avg_flooding_time - self.desidered_flooding_time) / self.desidered_flooding_time) * 100

    def get_residual_diameter(self):
        self.residual_diameter = ((self.avg_diameter - self.desidered_diameter) / self.desidered_diameter) * 100

    def infer_experiment_infos(self):
        self.number_of_simulations = len(set(self.samples['simulation']))
        self.d = self.samples['d'].values[0]
        self.c = self.samples['c'].values[0]
        if("lambda" in list(self.samples.keys())):
            self.r = self.samples['lambda'].values[0]
            self.q = self.samples['beta'].values[0]
            self.n = self.samples['target_n'].values[0]
            self.graph = "VD"
        else:
            self.n = self.samples['n'].values[0]
            self.p = self.samples['p'].values[0]
            self.graph = "ED"
        self.desidered_flooding_time = self.desidered_diameter = mt.log(self.n, 2)


    def get_structural_stats(self):
        avg_nodes_in_network = []
        semiregularity = []
        percentage = []
        if(self.graph == "VD"):
            for sim in range(0,self.number_of_simulations):
                nodes = list (self.samples[self.samples['simulation'] == sim]['n'].values)
                avg_nodes_in_network.append(sum(nodes)/len(nodes))
                regularity = list (self.samples[self.samples['simulation'] == sim]['semireg'].values)
                semiregularity.append(sum(regularity)/len(regularity))
                percentage.append(self.samples[self.samples['simulation'] == sim]['conv_percentage'].values[0])
                # For plotting, taking average number of nodes and average semiregularity at each time step
                self.nodes_in_each_sim.append(sum(nodes)/len(nodes))
                self.semiregualrity_in_each_sim.append(sum(regularity)/len(regularity))

            self.avg_semiregularity = sum(semiregularity) / self.number_of_simulations
            self.avg_n = (sum(avg_nodes_in_network) / self.number_of_simulations)
            self.avg_semiregularity_convergence_percentage = sum(percentage) / self.number_of_simulations
            self.std_n = 0
            self.std_semiregularity = 0
            self.std_semiregularity_convergence_percentage = 0
            for sim in range(0,self.number_of_simulations):
                self.std_n += mt.pow((avg_nodes_in_network[sim] - self.avg_n), 2)
                self.std_semiregularity += mt.pow((semiregularity[sim] - self.avg_semiregularity), 2)
                self.std_semiregularity_convergence_percentage += mt.pow((percentage[sim] - self.avg_semiregularity_convergence_percentage),2)
            b = 1/(self.number_of_simulations-1)
            self.std_n = mt.sqrt(b * self.std_n)
            self.std_semiregularity = mt.sqrt(b * self.std_semiregularity)
            self.std_semiregularity_convergence_percentage = mt.sqrt(b * self.std_semiregularity_convergence_percentage)
            logging.debug("\t\t STRUCTURAL INFOS")
            logging.debug("avg n = %r   std = %r" %( self.avg_n,self.std_n))
            logging.debug("avg semiregular = %r  std = %r"%(self.avg_semiregularity, self.std_semiregularity))
            logging.debug("avg conv = %r   std = %r"%(self.avg_semiregularity_convergence_percentage,self.std_semiregularity_convergence_percentage))
        elif(self.graph == "ED"):
            for sim in range(0, self.number_of_simulations):
                nodes = list(self.samples[self.samples['simulation'] == sim]['n'].values)
                avg_nodes_in_network.append(sum(nodes) / len(nodes))
                regularity = list(self.samples[self.samples['simulation'] == sim]['semireg'].values)

                semiregularity.append(sum(regularity) / len(regularity))

                # For plotting, taking average number of nodes and average semiregularity at each time step
                self.nodes_in_each_sim.append(sum(nodes) / len(nodes))
                self.semiregualrity_in_each_sim.append(sum(regularity) / len(regularity))

            self.avg_semiregularity = sum(semiregularity) / self.number_of_simulations
            self.avg_n = (sum(avg_nodes_in_network) / self.number_of_simulations)

            self.std_n = 0
            self.std_semiregularity = 0

            for sim in range(0, self.number_of_simulations):
                self.std_n += mt.pow((avg_nodes_in_network[sim] - self.avg_n), 2)
                self.std_semiregularity += mt.pow((semiregularity[sim] - self.avg_semiregularity), 2)

            b = 1 / (self.number_of_simulations - 1)
            self.std_n = mt.sqrt(b * self.std_n)
            self.std_semiregularity = mt.sqrt(b * self.std_semiregularity)

            logging.debug("\t\t STRUCTURAL INFOS")
            logging.debug("avg n = %r   std = %r" % (self.avg_n, self.std_n))
            logging.debug("avg semiregular = %r  std = %r" % (self.avg_semiregularity, self.std_semiregularity))


    def get_flooding_stats(self):
        summation = []
        informed = []
        if(self.graph == "VD"):
            # Ho agigiunto un pezzo per calcolare il numero medio di nodi nella rete
            for sim in range(0,self.number_of_simulations):
                result = list(self.samples[(self.samples['simulation'] == sim) & (self.samples['flood_status'] == "True")]['t_flood'].values)
                if(result):
                    summation.append(result[0])
                    convergence = self.samples[(self.samples['simulation'] == sim) & (self.samples['flood_status'] == "True")]['percentage_informed'].values[0]
                    informed.append(convergence)
                    self.flooding_convergence_percentage_in_each_sim.append(convergence/100)
                else:
                    self.flooding_convergence_percentage_in_each_sim.append(0)

                # For plotting, taking the number of informed nodes at the convergence step
                t_flood = max(self.samples[self.samples['simulation'] == sim]['t_flood'].values)
                self.flooding_in_each_sim.append(self.samples[(self.samples['simulation'] == sim)&(self.samples['t_flood'] == t_flood)]['informed_nodes'].values[0])

            n = len(summation)

            if (n != 0):
                self.avg_flooding_time = sum(summation) / n
                self.avg_flooding_convergence_percentage = (sum(informed) / n) / 100
                self.std_flooding_time = 0
                self.std_flooding_convergence_percentage = 0
                for sim in range(0, n):
                    self.std_flooding_time += mt.pow((summation[sim] - self.avg_flooding_time), 2)
                    self.std_flooding_convergence_percentage += mt.pow(
                        (informed[sim] - self.avg_flooding_convergence_percentage), 2)
                if (n > 1):
                    b = (1 / (n - 1))
                else:
                    b = 0
                a = (self.std_flooding_time)
                self.std_flooding_time = mt.sqrt(b * a)
                self.std_flooding_convergence_percentage = mt.sqrt(b * self.avg_flooding_convergence_percentage)
                self.get_t_test_flooding_time(summation)
                self.get_residual_flooding_time()
            else:
                logging.info("Flooding never converge")
        elif(self.graph == "ED"):
            for sim in range(0, self.number_of_simulations):
                result = list(
                    self.samples[(self.samples['simulation'] == sim) & (self.samples['flood_status'] == True)][
                        't_flood'].values)
                if (result):
                    summation.append(result[0])

                # For plotting, taking the number of informed nodes at the convergence step
                t_flood = max(self.samples[self.samples['simulation'] == sim]['t_flood'].values)
                self.flooding_in_each_sim.append(
                    self.samples[(self.samples['simulation'] == sim) & (self.samples['t_flood'] == t_flood)][
                        'informed_nodes'].values[0])
            n = len(summation)

            if (n != 0):
                self.avg_flooding_time = sum(summation) / n
                self.std_flooding_time = 0
                for sim in range(0, n):
                    self.std_flooding_time += mt.pow((summation[sim] - self.avg_flooding_time), 2)

                if (n > 1):
                    b = (1 / (n - 1))
                else:
                    b = 0
                a = (self.std_flooding_time)
                self.std_flooding_time = mt.sqrt(b * a)
                self.get_t_test_flooding_time(summation)
                self.get_residual_flooding_time()
            else:
                logging.info("Flooding never converge")



        # Define the plottings

    def get_diameter_stats(self):
        diameters = []
        disconnected = []

        for sim in range(0,self.number_of_simulations):
            diam = list(self.samples[(self.samples['simulation'] == sim) & (self.samples['diameter'] != "Null")]['diameter'].values)

            disc = len(self.samples[self.samples['simulation'] == sim]['diameter'].values) - len(diam)

            if(diam):
                integers_diam = [int(element) for element in diam]
                diameters.append(sum(integers_diam) / len(diam))

            if(disc):
                disconnected.append(disc /len(self.samples[self.samples['simulation'] == sim]['diameter'].values))

        if(diameters):
            self.avg_diameter = sum(diameters) / len(diameters)
            self.std_diameter = 0
            for elem in range(0,len(diameters)):
                self.std_diameter += mt.pow((diameters[elem]-self.avg_diameter),2)
            if(len(diameters)>1):
                b = 1/(len(diameters)-1)
            else:
                b = 1
            self.std_diameter = mt.sqrt(b * self.std_diameter)
        else:
            self.avg_diameter = np.inf
            self.std_diameter = np.inf
        if(disconnected):
            self.avg_disconnected = sum(disconnected) / len(disconnected)
            self.std_disconnected = 0
            for elem in range(0,len(disconnected)):
                self.std_disconnected += mt.pow((disconnected[elem]-self.avg_disconnected),2)
            a = 1/(len(disconnected)-1)
            self.std_disconnected = mt.sqrt(a * self.std_disconnected)
        else:
            self.avg_disconnected = 0
            self.std_disconnected = 0

        self.get_t_test_diameter(diameters)
        self.get_residual_diameter()
        logging.debug("\t\t DIAMETER INFOS")
        logging.debug("avg diameter = %r   std = %r" % (self.avg_diameter, self.std_diameter))
        logging.debug("avg disconnected = %r  std = %r" % (self.avg_disconnected, self.std_disconnected))
        logging.debug("Deisdered diameter = %r" % self.desidered_diameter)
        logging.debug("T-Test pval = %r     Residual = %r "%(self.t_test_diameter,self.residual_diameter))

    def pack_and_get_stats(self):
        logging.info("Packing infos for d = %r  c = %r  " % (self.d, self.c))
        self.stats_summary['d'] = self.d
        self.stats_summary['c'] = self.c
        self.stats_summary['#simulations'] = self.number_of_simulations

        if(self.graph == "VD"):
            # In rate and outrate
            self.stats_summary['r'] = self.r
            self.stats_summary['q'] = self.q
            self.stats_summary['E[n]'] = self.n
            # Structure
            self.stats_summary['avg_n'] = self.avg_n
            self.stats_summary['std_n'] = self.std_n
            self.stats_summary['avg_semireg'] = self.avg_semiregularity
            self.stats_summary['std_semireg'] = self.std_semiregularity
            self.stats_summary['avg_smireg_convergence'] = self.avg_semiregularity_convergence_percentage
            self.stats_summary['std_smireg_convergence'] = self.std_semiregularity_convergence_percentage
            # Flooding time
            self.stats_summary['avg_flooding_time'] = self.avg_flooding_time
            self.stats_summary['std_flooding_time'] = self.std_flooding_time
            self.stats_summary['ttest_flooding_time'] = self.t_test_flooding_time
            self.stats_summary['residual_flooding_time'] = self.residual_flooding_time
            self.stats_summary['avg_flooding_convergence'] = self.avg_flooding_convergence_percentage
            self.stats_summary['std_flooding_convergence'] = self.std_flooding_convergence_percentage
            # Diameter
            self.stats_summary['avg_diameter'] = self.avg_diameter
            self.stats_summary['std_diameter'] = self.std_diameter
            self.stats_summary['ttest_diameter'] = self.t_test_diameter
            self.stats_summary['residual_diamter'] = self.residual_diameter
            self.stats_summary['avg_disconnected'] = self.avg_disconnected
            self.stats_summary['std_disconnected'] = self.std_disconnected

        elif(self.graph == "ED"):
            # Structure
            self.stats_summary['avg_semireg'] = self.avg_semiregularity
            self.stats_summary['std_semireg'] = self.std_semiregularity
            # Flooding time
            self.stats_summary['avg_flooding_time'] = self.avg_flooding_time
            self.stats_summary['std_flooding_time'] = self.std_flooding_time
            self.stats_summary['ttest_flooding_time'] = self.t_test_flooding_time
            self.stats_summary['residual_flooding_time'] = self.residual_flooding_time
            # Diameter
            self.stats_summary['avg_diameter'] = self.avg_diameter
            self.stats_summary['std_diameter'] = self.std_diameter
            self.stats_summary['ttest_diameter'] = self.t_test_diameter
            self.stats_summary['residual_diamter'] = self.residual_diameter
            self.stats_summary['avg_disconnected'] = self.avg_disconnected
            self.stats_summary['std_disconnected'] = self.std_disconnected
        elif(self.graph == "EM"):
            # TO DO
            logging.debug("MUST BE DONE")
        return (self.stats_summary)

    def plot_statistics(self):
        logging.info("Creating folder for d = %r c = %r " % (self.d,self.c))
        create_folder(self.outputPathPlottings,"plottings")
        self.outputPathPlottings = self.outputPathPlottings + "plottings/"
        folderName = str(self.d)+"_"+str(self.c)
        create_folder(self.outputPathPlottings,folderName)
        self.outputPathPlottings = self.outputPathPlottings + folderName
        if(self.graph == "VD"):
            # Aggiungere controllo sul se il flooding termina
            logging.info("Plotting flooding stats")
            # Funzione plotting flooding trend
            logging.info("Plotting structural stats and flooding")
            # Plottare l'andamento delle simulazioni e dei nodi informati
            self.get_flooding_behaviour_plotting()
            self.get_flooding_average_trend()
            self.get_structural_plotting()
        elif(self.graph == "ED"):
            # Aggiungere controllo sul se il flooding termina
            logging.info("Plotting flooding stats")
            # Funzione plotting flooding trend
            logging.info("Plotting structural stats and flooding")
            # Plottare l'andamento delle simulazioni e dei nodi informati
            self.get_flooding_average_trend()
            self.get_structural_plotting()
        return(self.stats_summary)


    def get_flooding_behaviour_plotting(self):
        # using the average nodes in the network at each simulation
        # the number of informed nodes at each simulation
        # the average (d,cd)-regular nodes at each simulation
        #for sim in range(0,self.number_of_simulations):
        converged_simulations = list(int(i) for i in (self.samples[self.samples['flood_status'] == "True"]['simulation'].values))
        failed_simulations = list(set([i for i in range(0,self.number_of_simulations)]) - set(converged_simulations))
        #flooding_percentage_line = [self.flooding_convergence_percentage_in_each_sim[i] * self.nodes_in_each_sim[i] for i in range(0,self.number_of_simulations)]

        flooding_percentage_line = [self.percent(self.flooding_convergence_percentage_in_each_sim[i] * self.nodes_in_each_sim[i],self.n )for i in range(0,self.number_of_simulations)]
        target_n_percentage_line = [self.percent(self.n,self.n) for i in range(0,self.number_of_simulations)]
        zero_informed_simulations = []
        for fail in failed_simulations:
            if(len(self.samples[self.samples['simulation'] == fail]['informed_nodes']) <= 10):
                zero_informed_simulations.append(fail)
        failed_simulations = list(set(failed_simulations) - set(zero_informed_simulations))
        #flooding_percentage_std = [self.std_flooding_convergence_percentage  for i in range(0,self.number_of_simulations)]
        semiregular_percentge_line = [self.avg_semiregularity_convergence_percentage * self.nodes_in_each_sim[i] for i in range(0,self.number_of_simulations) ]
        pl.figure(figsize=(20, 4))
        pl.title("Flooding")
        pl.xlabel("Simulations")
        pl.ylabel("Nodes %")
        # percentages
        flooding_in_each_sim_percentage = []
        for flood in self.flooding_in_each_sim:
            flooding_in_each_sim_percentage.append(self.percent(flood,self.n))
        # pl.plot(self.flooding_in_each_sim, color = "blue")
        pl.plot(flooding_in_each_sim_percentage, color="blue")
        converged_simulations.extend(failed_simulations)
        if(converged_simulations):

            flooding_plot = [self.flooding_in_each_sim[elem] for elem in converged_simulations]
            flooding_plot_percentage = [ self.percent(elem,self.n) for elem in flooding_plot]
            pl.plot(converged_simulations,flooding_plot_percentage,'o',color = "green")
            # pl.plot(converged_simulations,flooding_plot,'o',color = "green")
        if(zero_informed_simulations):

            failed_plot = [self.flooding_in_each_sim[elem] for elem in zero_informed_simulations]
            failed_plot_percentage = [self.percent(elem,self.n) for elem in failed_plot]
            pl.plot(zero_informed_simulations,failed_plot_percentage, 'x', color="red")
            # pl.plot(zero_informed_simulations,failed_plot, 'x', color="red")
        nodes_in_each_sim_percentage = [self.percent(elem,self.n) for elem in self.nodes_in_each_sim]
        pl.plot(nodes_in_each_sim_percentage, color = "red")
        # pl.plot(self.nodes_in_each_sim, color = "red")
        #pl.plot(self.semiregualrity_in_each_sim, color = "green")
        pl.plot(flooding_percentage_line,'--',color = "orange")
        pl.plot(target_n_percentage_line,'-.',color ="magenta")
        #pl.errorbar(converged_simultatins,flooding_percentage_line, yerr=flooding_percentage_std)
                     #pl.plot(semiregular_percentge_line,'.-', color = "pink")
        pl.xlim(xmin = -1)
        pl.xticks([i for i in range(0,self.number_of_simulations)])
        if(converged_simulations):
            if(zero_informed_simulations):
                pl.legend(['Informed ','Terminated','Failed', 'Avg network size', 'Convergence %',r'$\frac{\lambda}{q}$'], title='Legend', bbox_to_anchor=(1, 1),
                  loc='upper left')
            else:
                pl.legend(['Informed ', 'Terminated', 'Avg network size', 'Convergence %',r'$\frac{\lambda}{q}$'], title='Legend',
                          bbox_to_anchor=(1, 1),
                          loc='upper left')
        else:
            pl.legend(['Informed ', 'Failed', 'Avg network size', 'Convergence %',r'$\frac{\lambda}{q}$'], title='Legend',
                      bbox_to_anchor=(1, 1),
                      loc='upper left')
        pl.savefig(self.outputPathPlottings+"/Flooding.png")
        #pl.savefig("/home/antonio/Desktop/Flooding.png")
        pl.close()


    def get_flooding_average_trend(self):
        if(self.graph == "VD"):
            converged_simulations = list(int(i) for i in (self.samples[self.samples['flood_status'] == "True"]['simulation'].values))
        elif(self.graph == "ED"):
            converged_simulations = list(int(i) for i in (self.samples[self.samples['flood_status'] == True]['simulation'].values))


        if(converged_simulations):
            informed_nodes =[]
            max = 0
            # Normalizing the experiments
            for sim in converged_simulations:
                informed = list(self.samples[(self.samples['simulation'] == sim) ]['informed_nodes'].values)
                informed_nodes.append(informed)
                if(max<len(informed)):
                    max = len(informed)
            for i in range(0,len(informed_nodes)):
                m = len(informed_nodes[i])
                if(m<max):
                    for j in range(m,max):
                        informed_nodes[i].append(informed_nodes[i][m-1])

            average_flooding_vector = [0 for i in range(0, len(informed_nodes[0][:]))]
            for i in range(0,len(informed_nodes[0][:])):
                for j in range(0,len(converged_simulations)):
                    average_flooding_vector[i] += informed_nodes[j][i]
                average_flooding_vector[i] = average_flooding_vector[i] / len(converged_simulations)

            # Transforming values to percentage
            # percentage_vector = []
            # for elem in average_flooding_vector:
            #     percentage_vector.append(self.percent(elem,self.n))

            pl.figure(figsize=(10, 5))

            pl.ylim(top = average_flooding_vector[-1]+30)
            #pl.ylim(top = percentage_vector[-1]+30)

            pl.plot([i for i in range(1,len(average_flooding_vector)+1)],average_flooding_vector)
            #pl.plot([i for i in range(1,len(percentage_vector)+1)],percentage_vector)
            if(mt.floor(self.avg_flooding_time) == len(average_flooding_vector)):
                pl.plot(self.avg_flooding_time,average_flooding_vector[mt.floor(self.avg_flooding_time)-1],'v',color = 'red')
                #pl.plot(self.avg_flooding_time,percentage_vector[mt.floor(self.avg_flooding_time)-1],'v',color = 'red')

                arrow_properties = dict(
                    facecolor="black", width=0.5,
                    headwidth=4, shrink=0.1)
                x_arrow = self.avg_flooding_time - 1
                y_arrow = average_flooding_vector[mt.floor(self.avg_flooding_time)-1]
                # arrow_properties = dict(
                #     facecolor="black", width=0.5,
                #     headwidth=4, shrink=0.1)
                # x_arrow = self.avg_flooding_time - 1
                # y_arrow = percentage_vector[mt.floor(self.avg_flooding_time) - 1]

            else:
                pl.plot(self.avg_flooding_time,average_flooding_vector[mt.floor(self.avg_flooding_time)],'v',color = 'red')
                #pl.plot(self.avg_flooding_time,percentage_vector[mt.floor(self.avg_flooding_time)],'v',color = 'red')

                arrow_properties = dict(
                    facecolor="black", width=0.5,
                    headwidth=4, shrink=0.1)
                x_arrow = self.avg_flooding_time -1
                y_arrow = average_flooding_vector[mt.floor(self.avg_flooding_time)]
                # arrow_properties = dict(
                #     facecolor="black", width=0.5,
                #     headwidth=4, shrink=0.1)
                # x_arrow = self.avg_flooding_time - 1
                # y_arrow = percentage_vector[mt.floor(self.avg_flooding_time)]
            if(x_arrow - 3  <= 0):
                x_label = x_arrow - 0.5
            elif(x_arrow > 5):
                x_label = x_arrow - 3
            else:
                x_label = x_arrow - 1
            y_lable = y_arrow
            if(self.graph == "VD"):
                pl.annotate(
                    str(self.avg_flooding_convergence_percentage*100)+"%",
                    xy= (x_arrow,y_arrow),
                    xytext=(x_label,y_lable),
                    arrowprops=arrow_properties
                )
            elif(self.graph == "ED"):
                pl.annotate(
                    str(100) + "%",
                    xy=(x_arrow, y_arrow),
                    xytext=(x_label, y_lable),
                    arrowprops=arrow_properties
                )
            pl.title("Flooding trend")
            pl.xlabel("Time")
            pl.ylabel("Nodes")
            pl.legend(['Average informed nodes ', 'Convergence'], title='Legend',
                      loc='lower right')

            pl.savefig(self.outputPathPlottings+"/FloodingTrend.png")
            #pl.savefig("/home/antonio/Desktop/FloodingCurve.png")
            pl.close()



    def get_structural_plotting(self):
        if(self.graph == "VD"):
            semiregular_percentge_line = [self.avg_semiregularity_convergence_percentage * self.semiregualrity_in_each_sim[i] for i in range(0,self.number_of_simulations) ]

            pl.figure(figsize=(20, 4))
            pl.title("Structural properties")
            pl.xlabel("Simulations")
            pl.ylabel("Nodes")
            pl.plot(self.semiregualrity_in_each_sim, color="blue")
            pl.plot(self.nodes_in_each_sim, color = "red")
            pl.plot(semiregular_percentge_line,'--',color = "orange")
            pl.xlim(xmin = -1)
            pl.xticks([i for i in range(0,self.number_of_simulations)])
            pl.legend(['(d,cd)-regular ', 'Avg network size', 'Convergence %'], title='Legend',
                      bbox_to_anchor=(1, 1),
                      loc='upper left')
        elif(self.graph == "ED"):
            pl.figure(figsize=(20, 4))
            pl.title("Structural properties")
            pl.xlabel("Simulations")
            pl.ylabel("Nodes")
            pl.plot(self.semiregualrity_in_each_sim, color="blue")
            pl.plot(self.nodes_in_each_sim, color="red")
            pl.xlim(xmin=-1)
            pl.xticks([i for i in range(0, self.number_of_simulations)])
            pl.legend(['(d,cd)-regular ', 'Avg network size'], title='Legend',
                      bbox_to_anchor=(1, 1),
                      loc='upper left')
        pl.savefig(self.outputPathPlottings+"/Structural.png")
        #pl.savefig("/home/antonio/Desktop/Structural.png")
        pl.close()



