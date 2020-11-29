import math as mt
import rpy2.robjects as ro

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
        self.desidere_diameter = None


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

    def get_t_test_diameter(self):
        x_avg_diameter = ro.vectors.FloatVector(self.avg_diameter)
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
        self.desidered_flooding_time = self.desidere_diameter = mt.log(self.n, 2)


    def get_flooding_stats(self):
        summation = []
        informed = []
        avg_nodes_in_network = []
        # Ho agigiunto un pezzo per calcolare il numero medio di nodi nella rete
        for sim in range(0,self.number_of_simulations):
            summation.append(self.samples[(self.samples['simulation'] == sim) & (self.samples['flood_status'] == "True")]['t_flood'].values[0])
            informed.append(self.samples[(self.samples['simulation'] == sim) & (self.samples['flood_status'] == "True")]['percentage_informed'].values[0])
            nodes =list (self.samples[(self.samples['simulation'] == sim) & (self.samples['flood_status'] == "True")]['n'].values)
            avg_nodes_in_network.append(sum(nodes)/len(nodes))
        self.avg_flooding_time = sum(summation) / self.number_of_simulations
        self.avg_flooding_convergence_percentage = sum(informed) / self.number_of_simulations
        self.std_flooding_time = 0
        self.std_flooding_convergence_percentage = 0
        for sim in range(0 , self.number_of_simulations):
            self.std_flooding_time += mt.pow((summation[sim]-self.avg_flooding_time) , 2)
            self.std_flooding_convergence_percentage += mt.pow((informed[sim] - self.avg_flooding_convergence_percentage), 2)
        b = (1/(self.number_of_simulations-1))
        a = (self.std_flooding_time)
        self.std_flooding_time = mt.sqrt(b*a)
        self.std_flooding_convergence_percentage = mt.sqrt(b * self.avg_flooding_convergence_percentage)
        #self.std_flooding_time = mt.pow(((1.0/(self.number_of_simulations-1.0)) * self.std_flooding_time),1/2)
        #self.std_flooding_convergence_percentage = mt.pow((((1.0/self.number_of_simulations-1.0)) * self.std_flooding_convergence_percentage),1/2)
        print("Avg nodi",sum(avg_nodes_in_network)/self.number_of_simulations)
        print(self.std_flooding_time)
        print("avg",self.avg_flooding_time)
        print(self.std_flooding_convergence_percentage)
        print("avgc",self.avg_flooding_convergence_percentage)
        self.get_t_test_flooding_time(summation)
        self.get_residual_flooding_time()
        # Define the plottings
        print(self.n)
        print(self.desidered_flooding_time)
        print(self.avg_flooding_time)
        print(self.residual_flooding_time)
        print(self.t_test_flooding_time)
        print(self.avg_flooding_convergence_percentage)
        exit(1)
    def get_diameter_stats(self):
        return(0)
