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
        self.number_of_simulations = self.get_number_of_simulations()
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

    def get_t_test_flooding_time(self):
        x_avg_flooding_time = ro.vectors.FloatVector(self.avg_flooding_time)
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
        if(self.samples['r'].values[0]!= 0):
            self.r = self.samples['r'].values[0]
            self.q = self.samples['q'].values[0]
            self.n = self.target['n'].values[0]
            self.graph = "VD"
        else:
            self.n = self.samples['n'].values[0]
            self.p = self.samples['p'].values[0]
            self.graph = "ED"
        self.desidered_flooding_time = self.desidere_diameter = mt.floor(mt.log(self.n, 2))


    def get_flooding_time_stats(self):
        summation = []
        for sim in range(0,self.number_of_simulations):
            summation.append(self.samples[(self.samples['simulation'] == sim) & (self.samples['flood_status'] == True)]['t_flood'].values)
        self.avg_flooding_time = sum(summation) / self.number_of_simulations
        self.std_flooding_time = 0
        for sim in range(0 , self.number_of_simulations):
            self.std_flooding_time += mt.pow((summation[sim]-self.avg_flooding_time) , 2)
        self.std_flooding_time = mt.sqrt((1/self.number_of_simulations-1) * self.std_flooding_time)