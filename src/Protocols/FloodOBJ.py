import logging

import networkx as nx
import random as rnd


class Flooding:

    def __init__(self):
        self.dic = {}
        self.initiator = -1
        self.started = False
        self.t_flood = None
        self.number_of_restart = -1
        self.converged = None
        self.failed = False
        self.percentage = 0
        self.informed_ratio = []
        self.stabilization = 0
        self.stop_time = None
        # self.number_informed = None
        # self.number_uninformed = None

    def set_flooding_dictionary(self, list_of_nodes):
        self.number_of_restart += 1
        for i in list_of_nodes:
            self.dic[i] = 0

    def set_initiator(self):
        self.initiator = rnd.choice(list(self.dic.keys()))
        self.dic[self.initiator] = 1
        self.started = True
        self.t_flood = 0
    # def set_informed_nodes(self, informed):
    #     self.number_informed = informed
    #
    # def set_uninformed_nodes(self, uninformed):
    #     self.number_uninformed = uninformed
    def get_initiator(self):
        return (self.initiator)
    def get_dic(self):
        return(self.dic)
    def get_informed_nodes(self):
        return (len(list(map(lambda x: x[0], list(filter(lambda elem: elem[1] == 1, self.dic.items()))))))
    def get_list_of_informed_ndoes(self):
        return (list(map(lambda x: x[0], list(filter(lambda elem: elem[1] == 1, self.dic.items())))))
    def get_uninformed_nodes(self):
        return (len(list(self.dic.items())) - (
            len(list(map(lambda x: x[0], list(filter(lambda elem: elem[1] == 1, self.dic.items())))))))

    def get_started(self):
        return (self.started)

    def get_t_flood(self):
        return(self.t_flood)

    def get_number_of_restart(self):
        return(self.number_of_restart)

    def add_nodes_to_dictionary(self, list_of_nodes):
        for i in list_of_nodes:
            self.dic[i] = 0

    def del_nodes_from_dictionary(self, list_of_nodes):
        for i in list_of_nodes:
            del self.dic[i]

    def set_converged(self,value):
        self.converged = value
    def set_percentage(self,perc):
        self.percentage = perc

    def get_percentage(self):
        return(self.percentage)
    def get_converged(self):
        return(self.converged)

    def update_flooding(self,G):
        # Filtering the dictionary getting all the informed nodes
        uninformed_neighbors = []
        for i in list(G.get_G().nodes()):
            if (self.dic[i] == 1):
                for j in list(G.get_G().neighbors(i)):
                    if (self.dic[j] == 0):
                        uninformed_neighbors.append(j)
        to_inform = list(set(uninformed_neighbors))
        for i in to_inform:
            self.dic[i] = 1
        self.t_flood += 1
        #self.incremental_convergence()
        return(len(to_inform))

    def check_flooding_status(self):
        if (not (self.initiator in list(self.dic.keys()))):
            if (self.get_informed_nodes() == 0):
                return (False)
        return (True)

    def set_stop_time(self,it):
        self.stop_time = it

    def incremental_convergence_dep(self):
        number_informed = self.get_informed_nodes()
        number_uninformed = self.get_uninformed_nodes()


        informed_ratio = number_informed/(number_uninformed+number_informed)


        self.informed_ratio.append(informed_ratio)
        if(self.t_flood>1):
            if(self.informed_ratio[-1] > self.informed_ratio[-2]):
                self.stabilization += 1
            else:
                self.stabilization -= 1
        #if(self.t_flood > number_informed+number_uninformed):
        #    logging.debug("Simulation running slow, variable Stabilization = %r"%self.stabilization)
        if(self.stabilization == 0 and self.t_flood >1):
            logging.info("++++++++++++++++++++++++++++++++++++++++")
            logging.info("++++ Flooding: Converged, alpha = %r t = %r"%(self.informed_ratio[-1],self.t_flood))
            logging.info("---- Variable Stabilization = %r"%(self.stabilization))
            logging.debug("****** Informed ratio ******")
            logging.debug("%r"%informed_ratio)
            logging.debug("*****************************")
            logging.info("++++++++++++++++++++++++++++++++++++++++")

            self.set_converged(True)
            nodes = len(list(self.dic.keys()))
            ones = (self.get_informed_nodes() / nodes) * 100
            self.set_percentage(ones)

    def incremental_convergence(self):
        number_informed = self.get_informed_nodes()
        number_uninformed = self.get_uninformed_nodes()
        if(number_uninformed != 0):

            informed_ratio = number_informed/number_uninformed
        else:
            informed_ratio = 0

        self.informed_ratio.append(informed_ratio)
        if(self.t_flood>1):
            if(self.informed_ratio[-2]<=self.informed_ratio[-1]):
                self.stabilization +=1

        if(self.stabilization == self.stop_time):

            self.set_converged(True)
            nodes = len(list(self.dic.keys()))
            ones = (self.get_informed_nodes() / nodes) * 100
            self.set_percentage(ones)

    def get_last_ratio(self):
        return(self.informed_ratio[-1])

    def terminated(self):
        nodes = len(list(self.dic.keys()))
        ones = (self.get_informed_nodes() /nodes) * 100
        #zeros = (self.get_uninformed_nodes()/nodes)*100
        if(ones == 100):
            self.set_percentage(ones)
            self.set_converged(True)
        elif(ones>= 90):
            a = 90
            b = 100
            while(a<=b):
                m = ((b + a) / 2)
                self.set_percentage(m)
                if(ones>= self.get_percentage()):
                    a = m + 1
                else:
                    b = m - 1
            self.set_converged(True)
        else:
            self.set_percentage(ones)
            self.set_converged(False)
    def is_informed(self):
        if (0 in list(self.dic.values())):
            self.set_converged(False)
        else:
            self.set_converged(True)

    def set_failed(self,result):
        self.failed = result

    def get_failed(self):
        return(self.failed)