import random as rnd
import statistics as stat

class Consensus:
    def __init__(self,number_of_byzantine_nodes = 0,update_rule = "3M"):
        # Coloring values are integers from 0 to k
        self.coloring = {}
        self.t_consensus = None
        self.converged = None
        self.started = False
        self.update_r = update_rule
        if(number_of_byzantine_nodes != 0):
            # The byzantine version must be implemented
            self.byzantine_number = number_of_byzantine_nodes
            self.byzantines = True
        else:
            self.byzantine_number = 0
            self.byzantines = False

    def get_consensus_status(self):
        return (self.coloring,self.t_consensus,self.converged)

    def get_t_consensus(self):
        return(self.t_consensus)

    def get_started(self):
        return(self.started)

    def get_coloring(self):
        return(self.coloring)

    def get_converged(self):
        return (self.converged)

    def start_consensus(self,G,initial_coloring):
        self.started = True
        j=0
        for u in list(G.nodes()):
            self.coloring[u] = initial_coloring[j]
            j+=1
        self.converged, a = self.check_convergence()

    def check_convergence(self):
        actual_coloring = list(self.coloring.values())
        result = False;
        if (len(actual_coloring) > 0):
            result = all(elem == actual_coloring[0] for elem in actual_coloring)
        if (result):
            self.converged = True
        else:
            self.converged = False
        print(actual_coloring[0])
        return self.converged, actual_coloring[0]

    def update_consensus(self,G):
        new_coloring = {}
        if(self.update_r == '3M'):
            for u in list(G.nodes()):
                neig = [n for n in G.neighbors(u)]

                # Sampling a node from the neighborhood
                if(len(neig) != 0):

                    sample = rnd.choices(neig, k=3)


                sample_colors = [self.coloring[sample[0]],self.coloring[sample[1]],self.coloring[sample[2]]]
                #sample_colors = map(lambda x, y:y[x],sample,self.coloring.values() )
                # Calculating the mode of the sample
                color = stat.mode(sample_colors)
                new_coloring[u] = color
            # Updating the stats of the network
            self.coloring = new_coloring

        self.converged, a = self.check_convergence()

    def add_nodes_to_dictionary(self, list_of_nodes,list_of_colors):
        j = 0
        for i in list_of_nodes:
            self.coloring[i] = list_of_colors[j]
            j+=1

    def del_nodes_from_dictionary(self, list_of_nodes):
        for i in list_of_nodes:
            del self.coloring[i]
