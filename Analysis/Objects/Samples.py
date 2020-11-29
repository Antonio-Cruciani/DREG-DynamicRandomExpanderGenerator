import math as mt
import numpy as np
import rpy2.robjects as ro
import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

class Samples:

    # samples must be a pack of experiments regarding the same d,c,r,q,p
    def __init__(self,samples):

        #self.inputPath = inpath
        #self.outputPath = outpath
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

        # Plotting variables

        #self.nodes = []

    def percent(self,num1, num2):
        num1 = float(num1)
        num2 = float(num2)
        percentage = '{0:.2f}'.format((num1 / num2 * 100))
        return float(percentage)
    # H0 = media è esattamente log2 n
    # H1 = media non è esattamente log2 n
    def get_t_test_flooding_time(self,samples):
        x_avg_flooding_time = ro.vectors.FloatVector(samples)
        ttest = ro.r['t.test']
        result = ttest(x_avg_flooding_time, mu=self.desidered_flooding_time, paired=self.paired,
                                          alternative=self.t_test_type, conflevel=self.confidence_level)
        self.t_test_flooding_time = result.rx2('p.value')[0]

    def get_t_test_diameter(self,samples):
        x_avg_diameter = ro.vectors.FloatVector(samples)
        ttest = ro.r['t.test']
        result = ttest(x_avg_diameter, mu=self.desidered_diameter, paired=self.paired,
                                         alternative=self.t_test_type, conflevel=self.confidence_level)
        self.t_test_diameter = result.rx2('p.value')[0]

    def get_residual_flooding_time(self):
        self.residual_flooding_time = ((self.avg_flooding_time - self.desidered_flooding_time) / self.desidered_flooding_time) * 100

    def get_residual_diameter(self):
        self.residual_diameter = ((self.avg_diameter - self.desidered_diameter) / self.desidered_diameter) * 100

    def infer_experiment_infos(self):
        self.number_of_simulations = len(set(self.samples['simulation']))
        self.d = self.samples['d'].values[0]
        self.c = self.samples['c'].values[0]
        if(self.samples['lambda'].values[0]!= 0):
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
        for sim in range(0,self.number_of_simulations):
            nodes = list (self.samples[self.samples['simulation'] == sim]['n'].values)
            avg_nodes_in_network.append(sum(nodes)/len(nodes))
            regularity = list (self.samples[self.samples['simulation'] == sim]['semireg'].values)
            semiregularity.append(sum(regularity)/len(regularity))
            percentage.append(self.samples[self.samples['simulation'] == sim]['conv_percentage'].values[0])
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


    def get_flooding_stats(self):
        summation = []
        informed = []
        # Ho agigiunto un pezzo per calcolare il numero medio di nodi nella rete
        for sim in range(0,self.number_of_simulations):
            result = list(self.samples[(self.samples['simulation'] == sim) & (self.samples['flood_status'] == "True")]['t_flood'].values)
            if(result):
                summation.append(result[0])
                informed.append(self.samples[(self.samples['simulation'] == sim) & (self.samples['flood_status'] == "True")]['percentage_informed'].values[0])
        n = len(summation)
        if(n!= 0):
            self.avg_flooding_time = sum(summation) / n
            self.avg_flooding_convergence_percentage = sum(informed) / n
            self.std_flooding_time = 0
            self.std_flooding_convergence_percentage = 0
            for sim in range(0 , n):
                self.std_flooding_time += mt.pow((summation[sim]-self.avg_flooding_time) , 2)
                self.std_flooding_convergence_percentage += mt.pow((informed[sim] - self.avg_flooding_convergence_percentage), 2)
            b = (1/(n-1))
            a = (self.std_flooding_time)
            self.std_flooding_time = mt.sqrt(b*a)
            self.std_flooding_convergence_percentage = mt.sqrt(b * self.avg_flooding_convergence_percentage)
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
            b = 1/(len(diameters)-1)
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
