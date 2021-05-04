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
        self.legend = True

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

        self.avg_90_flooding_time = None
        self.std_90_flooding_time = None
        self.avg_90_flooding_convergence_percentage = None
        self.std_90_flooding_convergence_percentage = None

        self.avg_decrements = None
        self.std_decrements = None

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
        self.flooding_90_in_each_sim = []
        self.semiregualrity_in_each_sim = []
        self.nodes_in_each_sim = []
        self.number_of_failed_sim = None

        # self.spectral_gaps_before = []
        # self.spectral_gaps_after = []
        # self.min_spectral_gap = []
        # self.max_spectral_gap = []

        self.stats_summary = {}
        # Plotting variables

        #self.nodes = []
        # Boolean variable for the spectral analysis
        self.spectrum = False

        self.median_spectral_gap = 0
        self.avg_spectral_gap = 0
        self.std_spectral_gap = 0

        self.mean_converged_spectral_gap = 0
        self.std_converged_spectral_gap = 0
        self.median_converged_spectral_gap = 0

        self.mean_converged_spectral_gap_logn = 0
        self.std_converged_spectral_gap_logn = 0
        self.median_converged_spectral_gap_logn = 0



        # Converged before random falling

        self.mean_converged_spectral_gap_before = 0
        self.std_converged_spectral_gap_before = 0
        self.median_converged_spectral_gap_before = 0

        self.mean_converged_spectral_gap_before_logn = 0
        self.std_converged_spectral_gap_before_logn = 0
        self.median_converged_spectral_gap_before_logn = 0



        self.residual_mean_spectral_gap_after = None
        self.residual_median_spectral_gap_after = None
        self.residual_mean_spectral_gap_before = None
        self.residual_median_spectral_gap_before = None

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
        self.residual_flooding_time = (self.desidered_flooding_time - self.avg_flooding_time)

    def get_residual_diameter(self):
        self.residual_diameter = (self.desidered_diameter - self.avg_diameter)

    def infer_experiment_infos(self):
        self.number_of_simulations = len(set(self.samples['simulation']))
        self.d = self.samples['d'].values[0]
        self.c = self.samples['c'].values[0]
        if("lambda" in list(self.samples.keys())):
            self.r = self.samples['lambda'].values[0]
            self.q = self.samples['beta'].values[0]
            self.n = self.samples['target_n'].values[0]
            self.graph = "VD"
            if ("SpectralGapBefore" in list(self.samples.keys())):
                self.spectrum = True
        else:
            if("spectralGapBefore" in list(self.samples.keys())):
                self.spectrum = True
            self.n = self.samples['n'].values[0]
            self.p = self.samples['p'].values[0]
            self.graph = "ED"
        self.desidered_flooding_time = self.desidered_diameter = mt.log(self.n, 2)

    def get_spectral_analysis(self):
        # All tuples (before,after)
        sample_medians_before = []
        sample_medians_after = []

        sample_means_before = []
        sample_means_after = []

        sample_std_bef = []
        sample_std_aft = []



        median_spectral_gap = 0
        avg_spectral_gap = 0
        std_spectral_gap = 0

        sample_convergence = []
        sample_convergence_logn = []

        sample_convergence_before = []
        sample_convergence_before_logn = []
        # Getting the medians and means

        for sim in range(0,self.number_of_simulations):
            if("spectralGapBefore" in list(self.samples.keys())):
                spectral_before = sorted(self.samples[self.samples['simulation'] == sim]['spectralGapBefore'].values)
                spectral_after = sorted(self.samples[self.samples['simulation'] == sim]['spectralGap'].values)
            else:
                spectral_before = sorted(self.samples[self.samples['simulation'] == sim]['SpectralGapBefore'].values)
                spectral_after = sorted(self.samples[self.samples['simulation'] == sim]['SpectralGap'].values)
            n_bef = len(spectral_before)
            n_aft = len(spectral_after)
            # getting median of the spectral gap before random falling
            # doing lenght % 2

            if(n_bef & 1 == 0):
                median_spectral_gap_before = ( spectral_before[int(n_bef / 2 )] + spectral_before[int((n_bef / 2 ) + 1)] ) / 2
            else:
                median_spectral_gap_before = spectral_before[int((n_bef +1 )/ 2)]
            if(n_aft % 1 == 0):
                median_spectral_gap_after = ( spectral_after[int(n_aft / 2)] + spectral_after[(int(n_aft /2)+1)] ) / 2
            else:
                median_spectral_gap_after = spectral_after[int((n_aft + 1) / 2)]
            sample_medians_before.append(median_spectral_gap_before)
            sample_medians_after.append(median_spectral_gap_after )

           # getting the means

            mean_spectral_gap_before =  sum(spectral_before) / n_bef

            mean_spectral_gap_after = sum(spectral_after) / n_aft

            sample_means_before.append( mean_spectral_gap_before )
            sample_means_after.append( mean_spectral_gap_after)

            # getting the standard deviation

            std_spectral_gap_before = mt.sqrt( (1/ n_bef ) * sum([ mt.pow(x - mean_spectral_gap_before,2) for x in spectral_before]) )

            std_spectral_gap_after = mt.sqrt( (1/ n_aft ) * sum([ mt.pow(x - mean_spectral_gap_after,2) for x in spectral_after]) )

            sample_std_bef.append(  std_spectral_gap_before )
            sample_std_aft.append( std_spectral_gap_after )

            # stats on converged spectral gap
            if(self.graph == "ED"):
                if("spectralGap" in list(self.samples.keys())):
                    sample_convergence.append(
                        self.samples[self.samples['simulation'] == sim]['spectralGap'].values[
                            self.samples[self.samples['simulation'] == sim]['t'].values[-1] -100
                        ]
                    )
                    sample_convergence_before.append(  self.samples[self.samples['simulation'] == sim]['spectralGapBefore'].values[
                            self.samples[self.samples['simulation'] == sim]['t'].values[-1] -100
                        ])
                else:

                    sample_convergence.append(
                        self.samples[self.samples['simulation'] == sim]['SpectralGap'].values[-1] -100

                    )

                    sample_convergence_before.append(
                        self.samples[self.samples['simulation'] == sim]['SpectralGapBefore'].values[
                            self.samples[self.samples['simulation'] == sim]['t'].values[-1] - 100
                            ])
            else:
                if ("spectralGap" in list(self.samples.keys())):
                    sample_convergence.append(
                        self.samples[self.samples['simulation'] == sim]['spectralGap'].values[0]

                    )
                    sample_convergence_before.append(
                        self.samples[self.samples['simulation'] == sim]['spectralGapBefore'].values[0]
                    )

                    sample_convergence_logn.append(
                        self.samples[self.samples['simulation'] == sim]['spectralGap'].values[int(mt.log(self.n,2))]

                    )
                    sample_convergence_before_logn.append(
                        self.samples[self.samples['simulation'] == sim]['spectralGapBefore'].values[int(mt.log(self.n,2))]
                    )


                else:

                    sample_convergence.append(
                        self.samples[self.samples['simulation'] == sim]['SpectralGap'].values[0]

                    )

                    sample_convergence_before.append(
                        self.samples[self.samples['simulation'] == sim]['SpectralGapBefore'].values[0]
                            )

                    sample_convergence_logn.append(
                        self.samples[self.samples['simulation'] == sim]['SpectralGap'].values[int(mt.log(self.n,2))]

                    )

                    sample_convergence_before_logn.append(
                        self.samples[self.samples['simulation'] == sim]['SpectralGapBefore'].values[int(mt.log(self.n,2))]
                    )

        # median of medians
        sample_medians_before = sorted(sample_medians_before)
        sample_medians_after = sorted(sample_medians_after)

        if(len(sample_medians_before) % 1 == 0):
                self.median_spectral_gap = (
                    (
                        (sample_medians_before[int(len(sample_medians_before) / 2 ) ] + sample_medians_before[int((len(sample_medians_before) / 2 )+1)])/2
                        ,
                        (sample_medians_after[int(len(sample_medians_after) / 2)] + sample_medians_after[
                            int((len(sample_medians_after) / 2) + 1)])/2
                    )
                )
                self.avg_spectral_gap = (
                    sum(sample_means_before) / len(sample_means_before),
                    sum(sample_means_after) / len(sample_means_after)

                )
                self.std_spectral_gap = (

                    mt.sqrt(
                        (1/len(sample_std_bef) * sum([mt.pow(x - self.avg_spectral_gap[0],2) for x in sample_means_before]))
                    )
                    ,
                    mt.sqrt(
                        (1/len(sample_std_aft) * sum([mt.pow(x - self.avg_spectral_gap[1],2) for x in sample_means_after]))
                    )
                )
                sample_convergence = sorted(sample_convergence)
                self.mean_converged_spectral_gap = sum(sample_convergence)/len(sample_convergence)
                self.std_converged_spectral_gap = mt.sqrt((1/len(sample_convergence) * sum([mt.pow(x-self.mean_converged_spectral_gap,2) for x in sample_convergence])))
                self.median_converged_spectral_gap = (sample_convergence[int(len(sample_convergence)/2)] + sample_convergence[int(len(sample_convergence)/2)+1])/2

                sample_convergence_logn = sorted(sample_convergence_logn)
                self.mean_converged_spectral_gap_logn = sum(sample_convergence_logn) / len(sample_convergence_logn)
                self.std_converged_spectral_gap_logn = mt.sqrt((1 / len(sample_convergence_logn) * sum(
                    [mt.pow(x - self.mean_converged_spectral_gap_logn, 2) for x in sample_convergence_logn])))
                self.median_converged_spectral_gap_logn = (sample_convergence_logn[int(len(sample_convergence_logn) / 2)] +
                                                      sample_convergence_logn[int(len(sample_convergence_logn) / 2) + 1]) / 2

                sample_convergence_before = sorted(sample_convergence_before)

                self.mean_converged_spectral_gap_before = sum(sample_convergence_before)/len(sample_convergence_before)
                self.std_converged_spectral_gap_before = mt.sqrt((1/len(sample_convergence_before) * sum([mt.pow(x-self.mean_converged_spectral_gap_before,2) for x in sample_convergence_before])))
                self.median_converged_spectral_gap_before = (sample_convergence_before[int(len(sample_convergence_before)/2)] + sample_convergence_before[int(len(sample_convergence_before)/2)+1])/2

                sample_convergence_before_logn = sorted(sample_convergence_before_logn)
                self.mean_converged_spectral_gap_before_logn = sum(sample_convergence_before_logn) / len(sample_convergence_before_logn)
                self.std_converged_spectral_gap_before_logn = mt.sqrt((1 / len(sample_convergence_before_logn) * sum(
                    [mt.pow(x - self.mean_converged_spectral_gap_before_logn, 2) for x in sample_convergence_before_logn])))
                self.median_converged_spectral_gap_before_logn = (sample_convergence_before_logn[
                                                                 int(len(sample_convergence_before_logn) / 2)] +
                                                             sample_convergence_before_logn[
                                                                 int(len(sample_convergence_before_logn) / 2) + 1]) / 2

        logging.info("Spectral Analysis ")
        logging.info("Median: Spectral gap before %r       Spectral gap after %r"%(self.median_spectral_gap[0],self.median_spectral_gap[0]))
        logging.info("Mean: Spectral gap before %r       Spectral gap after %r"%(self.avg_spectral_gap[0],self.avg_spectral_gap[0]))
        logging.info("STD: Spectral gap before %r       Spectral gap after %r"%(self.std_spectral_gap[0],self.std_spectral_gap[0]))

    def get_spectral_gap_residuals(self,raes_mean_spectral_gap_before,raes_mean_spectral_gap_before_after,raes_median_spectral_gap_before,raes_median_spectral_gap_after):
        self.residual_mean_spectral_gap_after = (raes_mean_spectral_gap_before_after - self.avg_spectral_gap[1])
        self.residual_median_spectral_gap_after = (raes_median_spectral_gap_after - self.median_spectral_gap[1])
        self.residual_median_spectral_gap_after = (raes_median_spectral_gap_after - self.median_spectral_gap[1])
        self.residual_mean_spectral_gap_before = (raes_mean_spectral_gap_before- self.avg_spectral_gap[0])
        self.residual_median_spectral_gap_before = (raes_median_spectral_gap_before - self.median_spectral_gap[0])
        logging.info("Residuals between RAES and Edge Dynamics")
        logging.info("Spectral gap before")
        logging.info("|RaesMean - EDMean| = %r"%(self.residual_mean_spectral_gap_before))
        logging.info("|RaesMedian - EDMedian| = %r"%(self.residual_median_spectral_gap_before))
        logging.info("Spectral gap after")
        logging.info("|RaesMean - EDMean| = %r" % (self.residual_mean_spectral_gap_after))
        logging.info("|RaesMedian - EDMedian| = %r" % (self.residual_median_spectral_gap_after))

    def get_structural_stats(self):
        avg_nodes_in_network = []
        semiregularity = []
        percentage = []
        if(self.graph == "VD"):
            for sim in range(0,self.number_of_simulations):
                nodes = list (self.samples[self.samples['simulation'] == sim]['n'].values)
                avg_nodes_in_network.append(sum(nodes)/len(nodes))
                if("semiReg" in self.samples.keys()):
                    regularity = list(self.samples[self.samples['simulation'] == sim]['semiReg'].values)
                else:
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
                if("semiReg" in self.samples.keys()):
                    regularity = list(self.samples[self.samples['simulation'] == sim]['semiReg'].values)
                else:
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
            converged_simulations = list(int(i) for i in (self.samples[self.samples['flood_status'] == "True"]['simulation'].values))
            failed_simulations = list(set([i for i in range(0, self.number_of_simulations)]) - set(converged_simulations))
            self.number_of_failed_sim = (len(failed_simulations))
            # Ho agigiunto un pezzo per calcolare il numero medio di nodi nella rete
            for sim in range(0,self.number_of_simulations):
                result = list(self.samples[(self.samples['simulation'] == sim) & (self.samples['flood_status'] == "True")]['t_flood'].values)

                if(result ):
                    summation.append(result[0])
                    convergence = self.samples[(self.samples['simulation'] == sim) & (self.samples['flood_status'] == "True")]['percentage_informed'].values[0]
                    informed.append(convergence)
                    self.flooding_convergence_percentage_in_each_sim.append(convergence/100)


                else:
                    self.flooding_convergence_percentage_in_each_sim.append(0)

                # For plotting, taking the number of informed nodes at the convergence step
                t_flood = max(self.samples[self.samples['simulation'] == sim]['t_flood'].values)
                self.flooding_in_each_sim.append(self.samples[(self.samples['simulation'] == sim)&(self.samples['t_flood'] == t_flood)]['informed_nodes'].values[0])

            # Getting the 90% convergence
            indexes_converged_simulations = sorted(list(set(self.samples[self.samples['flood_status'] == "True"]['simulation'].values)))
            #indexes_simulations = [i for i in range(0,len(list(set(self.samples['simulation'].values))))]
            informed_90_perc = []
            for sim in indexes_converged_simulations:
                experiment = self.samples[self.samples['simulation'] == sim][['informed_nodes','uninformed_nodes','t_flood']].values
                k = 0
                found = False
                while(k<len(experiment) and found == False):
                    elem = experiment[k]
                    if(elem[0]/(elem[0]+elem[1])>=0.90):
                        self.flooding_90_in_each_sim.append(elem[2])
                        informed_90_perc.append(elem[0]/(elem[0]+elem[1]))
                        found = True
                    k+=1

            n90 = len(self.flooding_90_in_each_sim)
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

                decrements = []
                for elem in summation:
                    decrements.append(
                        elem - mt.log(self.n,2)
                    )
                self.avg_decrements = sum(decrements)/n
                self.std_decrements = 0
                for sim in range(0, n):
                    self.std_decrements += mt.pow((decrements[sim] - self.avg_decrements), 2)
                if (n > 1):
                    b = (1 / (n - 1))
                else:
                    b = 0
                a = (self.std_decrements)
                self.std_decrements = mt.sqrt(b * a)
                logging.info("\t\t FLOODING INFOS")


            else:
                logging.info("Flooding never converge")

            if (n90 != 0):
                self.avg_90_flooding_time = sum(self.flooding_90_in_each_sim) / n90

                self.avg_90_flooding_convergence_percentage = (sum(informed_90_perc) / n90)
                self.std_90_flooding_time = 0
                self.std_90_flooding_convergence_percentage = 0
                for sim in range(0, n90):
                    self.std_90_flooding_time += mt.pow((self.flooding_90_in_each_sim[sim] - self.avg_90_flooding_time), 2)
                    self.std_90_flooding_convergence_percentage += mt.pow(
                        (self.flooding_90_in_each_sim[sim] - self.avg_90_flooding_convergence_percentage), 2)
                if (n90 > 1):
                    b = (1 / (n90 - 1))
                else:
                    b = 0
                a = (self.std_90_flooding_time)
                self.std_90_flooding_time = mt.sqrt(b * a)
                self.std_90_flooding_convergence_percentage = mt.sqrt(b * self.avg_90_flooding_convergence_percentage)
                #self.get_t_test_flooding_time(summation)
                #self.get_residual_flooding_time()
            else:
                logging.info("Flooding 90% never converge")

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
                self.avg_flooding_convergence_percentage = 1
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
            if(len(disconnected) ==1):
                a = 1
            else:
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
            self.stats_summary['number_failed_simulations'] = self.number_of_failed_sim

            # Flooding 90%
            # Flooding time
            self.stats_summary['avg_90_flooding_time'] = self.avg_90_flooding_time
            self.stats_summary['std_90_flooding_time'] = self.std_90_flooding_time
            self.stats_summary['avg_90_flooding_convergence'] = self.avg_90_flooding_convergence_percentage
            self.stats_summary['std_90_flooding_convergence'] = self.std_90_flooding_convergence_percentage

            # Flooding Decrements

            self.stats_summary['avg_decrements'] = self.avg_decrements
            self.stats_summary['std_decrements'] = self.std_decrements
            # Diameter
            self.stats_summary['avg_diameter'] = self.avg_diameter
            self.stats_summary['std_diameter'] = self.std_diameter
            self.stats_summary['ttest_diameter'] = self.t_test_diameter
            self.stats_summary['residual_diamter'] = self.residual_diameter
            self.stats_summary['avg_disconnected'] = self.avg_disconnected
            self.stats_summary['std_disconnected'] = self.std_disconnected

            if (self.spectrum):
                self.stats_summary['median_spectral_gap_before'] = self.median_spectral_gap[0]
                self.stats_summary['median_spectral_gap_after'] = self.median_spectral_gap[1]
                self.stats_summary['mean_spectral_gap_before'] = self.avg_spectral_gap[0]
                self.stats_summary['std_spectral_gap_before'] = self.std_spectral_gap[0]
                self.stats_summary['mean_spectral_gap_after'] = self.avg_spectral_gap[1]
                self.stats_summary['std_spectral_gap_after'] = self.std_spectral_gap[1]
                # converged spectral gap
                self.stats_summary['mean_convergence_spectral_gap'] = self.mean_converged_spectral_gap
                self.stats_summary['std_convergence_sprectral_gap'] = self.std_converged_spectral_gap
                self.stats_summary['median_convergence_spectral_gap'] = self.median_converged_spectral_gap

                self.stats_summary['mean_convergence_spectral_gap_before'] = self.mean_converged_spectral_gap_before
                self.stats_summary['std_convergence_sprectral_gap_before'] = self.std_converged_spectral_gap_before
                self.stats_summary['median_convergence_spectral_gap_before'] = self.median_converged_spectral_gap_before

                self.stats_summary['mean_convergence_spectral_gap_logn'] = self.mean_converged_spectral_gap_logn
                self.stats_summary['std_convergence_sprectral_gap_logn'] = self.std_converged_spectral_gap_logn
                self.stats_summary['median_convergence_spectral_gap_logn'] = self.median_converged_spectral_gap_logn

                self.stats_summary['mean_convergence_spectral_gap_before_logn'] = self.mean_converged_spectral_gap_before_logn
                self.stats_summary['std_convergence_sprectral_gap_before_logn'] = self.std_converged_spectral_gap_before_logn
                self.stats_summary['median_convergence_spectral_gap_before_logn'] = self.median_converged_spectral_gap_before_logn



        elif(self.graph == "ED"):
            if(self.avg_flooding_time != None):
                self.stats_summary['n'] = self.n
                self.stats_summary['p'] = self.p

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

                if (self.spectrum):
                    self.stats_summary['median_spectral_gap_before'] = self.median_spectral_gap[0]
                    self.stats_summary['median_spectral_gap_after'] = self.median_spectral_gap[1]
                    self.stats_summary['mean_spectral_gap_before'] = self.avg_spectral_gap[0]
                    self.stats_summary['std_spectral_gap_before'] = self.std_spectral_gap[0]
                    self.stats_summary['mean_spectral_gap_after'] = self.avg_spectral_gap[1]
                    self.stats_summary['std_spectral_gap_after'] = self.std_spectral_gap[1]
                    # converged spectral gap
                    self.stats_summary['mean_convergence_spectral_gap'] = self.mean_converged_spectral_gap
                    self.stats_summary['std_convergence_sprectral_gap'] = self.std_converged_spectral_gap
                    self.stats_summary['median_convergence_spectral_gap'] = self.median_converged_spectral_gap

                    self.stats_summary['mean_convergence_spectral_gap_before'] = self.mean_converged_spectral_gap_before
                    self.stats_summary['std_convergence_sprectral_gap_before'] = self.std_converged_spectral_gap_before
                    self.stats_summary['median_convergence_spectral_gap_before'] = self.median_converged_spectral_gap_before


            else:
                # Nodes and falling probability
                self.stats_summary['n'] = self.n
                self.stats_summary['p'] = self.p
                # Structure
                self.stats_summary['avg_semireg'] = self.avg_semiregularity
                self.stats_summary['std_semireg'] = self.std_semiregularity

                # Diameter
                self.stats_summary['avg_diameter'] = self.avg_diameter
                self.stats_summary['std_diameter'] = self.std_diameter
                self.stats_summary['ttest_diameter'] = self.t_test_diameter
                self.stats_summary['residual_diamter'] = self.residual_diameter
                self.stats_summary['avg_disconnected'] = self.avg_disconnected
                self.stats_summary['std_disconnected'] = self.std_disconnected
                # Spectral gap
                if(self.spectrum):
                    self.stats_summary['median_spectral_gap_before'] = self.median_spectral_gap[0]
                    self.stats_summary['median_spectral_gap_after'] = self.median_spectral_gap[1]
                    self.stats_summary['mean_spectral_gap_before'] = self.avg_spectral_gap[0]
                    self.stats_summary['std_spectral_gap_before'] = self.std_spectral_gap[0]
                    self.stats_summary['mean_spectral_gap_after'] = self.avg_spectral_gap[1]
                    self.stats_summary['std_spectral_gap_after'] = self.std_spectral_gap[1]
                    # converged spectral gap
                    self.stats_summary['mean_convergence_spectral_gap'] = self.mean_converged_spectral_gap
                    self.stats_summary['std_convergence_sprectral_gap'] = self.std_converged_spectral_gap
                    self.stats_summary['median_convergence_spectral_gap'] = self.median_converged_spectral_gap


                    self.stats_summary['mean_convergence_spectral_gap_before'] = self.mean_converged_spectral_gap_before
                    self.stats_summary['std_convergence_sprectral_gap_before'] = self.std_converged_spectral_gap_before
                    self.stats_summary['median_convergence_spectral_gap_before'] = self.median_converged_spectral_gap_before

                if(self.residual_median_spectral_gap_before != None):
                    self.stats_summary['residual_mean_before'] = self.residual_mean_spectral_gap_before
                    self.stats_summary['residual_median_before'] = self.residual_median_spectral_gap_before
                    self.stats_summary['residual_mean_after'] = self.residual_mean_spectral_gap_after
                    self.stats_summary['residual_median_after'] = self.residual_median_spectral_gap_after

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
            if("flood_status" in self.samples.keys() ):
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
        #is_converged = sum(flooding_percentage_line)
        is_converged = 0

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
        #nodes_in_each_sim_percentage = [self.percent(elem,self.n) for elem in self.nodes_in_each_sim]
        #pl.plot(nodes_in_each_sim_percentage, color = "red")
        # pl.plot(self.nodes_in_each_sim, color = "red")
        #pl.plot(self.semiregualrity_in_each_sim, color = "green")
        if(is_converged != 0):
            pl.plot(flooding_percentage_line,'--',color = "orange")
        pl.plot(target_n_percentage_line,'-.',color ="magenta")
        #pl.errorbar(converged_simultatins,flooding_percentage_line, yerr=flooding_percentage_std)
                     #pl.plot(semiregular_percentge_line,'.-', color = "pink")
        pl.xlim(xmin = -1)
        pl.xticks([i for i in range(0,self.number_of_simulations)])
        if(self.legend):
            if(converged_simulations):
                if(zero_informed_simulations):
                    if(is_converged != 0):
                        pl.legend(['Informed ','Terminated','Failed', 'Convergence %',r'$\frac{\lambda}{q}$'], title='Legend', bbox_to_anchor=(1, 1),
                          loc='upper left')
                    else:
                        pl.legend(['Informed ', 'Terminated', 'Failed',
                                   r'$\frac{\lambda}{q}$'], title='Legend', bbox_to_anchor=(1, 1),
                                  loc='upper left')
                else:
                    if (is_converged != 0):
                        pl.legend(['Informed ', 'Terminated', 'Convergence %',r'$\frac{\lambda}{q}$'], title='Legend',
                                  bbox_to_anchor=(1, 1),
                                  loc='upper left')
                    else:
                        pl.legend(['Informed ', 'Terminated', 'Failed',
                                   r'$\frac{\lambda}{q}$'], title='Legend', bbox_to_anchor=(1, 1),
                                  loc='upper left')
            else:
                if (is_converged != 0):
                    pl.legend(['Informed ', 'Failed', 'Convergence %',r'$\frac{\lambda}{q}$'], title='Legend',
                              bbox_to_anchor=(1, 1),
                              loc='upper left')
                else:
                    pl.legend(['Informed ', 'Terminated', 'Failed',
                               r'$\frac{\lambda}{q}$'], title='Legend', bbox_to_anchor=(1, 1),
                              loc='upper left')
        pl.savefig(self.outputPathPlottings+"/Flooding.png",bbox_inches="tight")
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

                # arrow_properties = dict(
                #     facecolor="black", width=0.5,
                #     headwidth=4, shrink=0.1)
                # x_arrow = self.avg_flooding_time - 1
                # y_arrow = average_flooding_vector[mt.floor(self.avg_flooding_time)-1]
                # arrow_properties = dict(
                #     facecolor="black", width=0.5,
                #     headwidth=4, shrink=0.1)
                # x_arrow = self.avg_flooding_time - 1
                # y_arrow = percentage_vector[mt.floor(self.avg_flooding_time) - 1]

            else:
                pl.plot(self.avg_flooding_time,average_flooding_vector[mt.floor(self.avg_flooding_time)],'v',color = 'red')
                #pl.plot(self.avg_flooding_time,percentage_vector[mt.floor(self.avg_flooding_time)],'v',color = 'red')

            #     arrow_properties = dict(
            #         facecolor="black", width=0.5,
            #         headwidth=4, shrink=0.1)
            #     x_arrow = self.avg_flooding_time -1
            #     y_arrow = average_flooding_vector[mt.floor(self.avg_flooding_time)]
            #     # arrow_properties = dict(
            #     #     facecolor="black", width=0.5,
            #     #     headwidth=4, shrink=0.1)
            #     # x_arrow = self.avg_flooding_time - 1
            #     # y_arrow = percentage_vector[mt.floor(self.avg_flooding_time)]
            # if(x_arrow - 3  <= 0):
            #     x_label = x_arrow - 0.5
            # elif(x_arrow > 5):
            #     x_label = x_arrow - 3
            # else:
            #     x_label = x_arrow - 1
            # y_lable = y_arrow
            # if(self.graph == "VD"):
            #     pl.annotate(
            #         str(self.avg_flooding_convergence_percentage*100)+"%",
            #         xy= (x_arrow,y_arrow),
            #         xytext=(x_label,y_lable),
            #         arrowprops=arrow_properties
            #     )
            # elif(self.graph == "ED"):
            #     pl.annotate(
            #         str(100) + "%",
            #         xy=(x_arrow, y_arrow),
            #         xytext=(x_label, y_lable),
            #         arrowprops=arrow_properties
            #     )
            pl.title("Flooding trend")
            pl.xlabel("Time")
            pl.ylabel("Nodes")
            pl.legend(['Average informed nodes ', 'Convergence at '+str(round(self.avg_flooding_convergence_percentage*100))+"%"], title='Legend',
                      loc='lower right')

            pl.savefig(self.outputPathPlottings+"/FloodingTrend.png")
            #pl.savefig("/home/antonio/Desktop/FloodingCurve.png")
            pl.close()



    def get_structural_plotting(self):
        if(self.graph == "VD"):
            semiregular_percentge_line = [self.percent(self.avg_semiregularity_convergence_percentage * self.semiregualrity_in_each_sim[i],self.nodes_in_each_sim[i]) for i in range(0,self.number_of_simulations) ]
            nodes_in_each_sim_percentage = [self.percent(self.nodes_in_each_sim[i], self.n) for i in range(0,self.number_of_simulations)]
            semireg_percentage = [self.percent(elem,self.n) for elem in self.semiregualrity_in_each_sim]
            pl.figure(figsize=(20, 4))
            pl.title("Structural properties")
            pl.xlabel("Simulations")
            pl.ylabel("Nodes %")
            pl.plot(semireg_percentage, color="blue")
            pl.plot(nodes_in_each_sim_percentage, color = "red")
            pl.plot(semiregular_percentge_line,'--',color = "orange")
            pl.xlim(xmin = -1)
            pl.xticks([i for i in range(0,self.number_of_simulations)])
            pl.legend(['(d,cd)-regular % ', 'Avg network size', 'Convergence %'], title='Legend',
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


    def get_mean_spectral_gap(self):
        return (self.avg_spectral_gap)
    def get_median_spectral_gap(self):
        return(self.median_spectral_gap)





