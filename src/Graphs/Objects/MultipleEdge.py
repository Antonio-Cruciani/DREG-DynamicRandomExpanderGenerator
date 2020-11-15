import networkx as nx
import random as rnd
import numpy as np
import math as mt
import scipy
import scipy.sparse

from src.MathModules.MathTools import flip
from src.Protocols.FloodOBJ import Flooding
from src.Protocols.Consensus import Consensus
class DynamicGraph:
    # Aggiungere lista di archi iniziale del grafo

    def __init__(self,n = 0,d = 4,c = 1.5,lam = 1 ,beta = 1,falling_probability = 0,model = None ,starting_edge_list = [],edge_birth_rate = None, edge_death_rate = None):
        self.G = nx.Graph()
        self.G.add_nodes_from([i for i in range(0,n)])
        self.n = n
        self.d = d
        self.tolerance = int(c*d)
        self.c = c
        self.inrate = lam
        self.outrate = beta
        self.target_n = self.set_target_size(lam,beta)
        self.p = falling_probability
        self.flooding = Flooding()
        self.consensus = Consensus()
        self.initial_colors = 2
        self.consensus_bias = [0.5,0.5]
        self.number_of_exiting_nodes_at_each_round = []
        self.number_of_entering_nodes_at_each_round = []
        self.type_of_dynamic_graph = model
        self.converged = False
        self.target_density = self.target_size_achieved()
        self.max_label = n
        self.birth_rate = edge_birth_rate
        self.death_rate = edge_death_rate
        self.semiregular_percentage = 100
        self.aolds = [0]
        self.bolds = [100]
        self.a = 0
        self.b = 100

        self.time_conv = 0
        self.reset_number = 0
        if(starting_edge_list):
            self.G.add_edges_from(starting_edge_list)
        if(model == "EdgeMarkovian"):
            kn = nx.complete_graph(n)
            self.kn_edges = []
            for e in nx.generate_edgelist(kn,data=False):
                if(int(e.split(" ")[0])<int(e.split(" ")[1])):

                    self.kn_edges.append((int(e.split(" ")[0]),int(e.split(" ")[1])))
                else:
                    self.kn_edges.append((int(e.split(" ")[1]), int(e.split(" ")[0])))
        else:
            self.kn_edges = []

    def set_target_size(self,lam, beta):
        if(beta == 0):
            print("Error, beta = 0 ")
            exit(-1)
        else:
            return(lam/beta)


    def set_flooding(self):
        #istanzia il flood
        self.flooding.set_flooding_dictionary(self.get_list_of_nodes())

    def set_number_of_exiting_nodes_at_each_round(self,number_of_nodes):
        self.number_of_exiting_nodes_at_each_round.append(number_of_nodes)

    def set_number_of_entering_nodes_at_each_round(self,number_of_nodes):
        self.number_of_entering_nodes_at_each_round.append(number_of_nodes)

    def set_converged(self,value):
        self.converged = value

    def set_max_label(self,new_label):
        self.max_label += new_label
    def set_semiregular_percentage(self,perc):
        self.semiregular_percentage = perc
    def increment_time_conv(self):
        self.time_conv += 1
    def reset_time_conv(self):
        self.time_conv = 0
        self.reset_number +=1
    def get_reset_number(self):
        return(self.reset_number)

    def start_flooding(self):
        self.flooding.set_initiator()

    def update_flooding(self):
        self.flooding.update_flooding()

    def get_number_of_exiting_nodes_at_each_round(self):
        return(self.number_of_exiting_nodes_at_each_round)

    def get_number_of_entering_nodes_at_each_round(self):
        return(self.number_of_entering_nodes_at_each_round)
    def get_target_density(self):
        return(self.target_density)
    def get_target_n(self):
        return(self.target_n)
    def get_n(self):
        return(self.n)
    def get_G(self):
        return(self.G)
    def get_degree(self):
        return(self.G.degree())
    def get_target(self):
        return(self.d)
    def get_tolerance(self):
        return(self.tolerance)
    def get_d(self):
        return(self.d)
    def get_c(self):
        return(self.c)
    def get_p(self):
        return(self.p)
    def get_inrate(self):
        return(self.inrate)
    def get_outrate(self):
        return(self.outrate)
    def get_semiregular_percentage(self):
        return(self.semiregular_percentage/100)
    def get_time_conv(self):
        return(self.time_conv)
    def get_list_of_nodes(self):
        return(list(self.G.nodes()))
    def get_list_of_edges(self):
        edge_list_tuples = []
        for edge in nx.generate_edgelist(self.G, data=False):
            if(int(edge.split(" ")[0])<int(edge.split(" ")[1])):
                edge_list_tuples.append((int(edge.split(" ")[0]),int(edge.split(" ")[1])))
            else:
                edge_list_tuples.append((int(edge.split(" ")[1]), int(edge.split(" ")[0])))

        return(edge_list_tuples)

    def get_converged(self):
        return(self.converged)
    def get_max_label(self):
        return(self.max_label)
    def get_target_n(self):
        return(self.target_n)
    def get_sample_add_phase(self,neigh):
        if(self.type_of_dynamic_graph == "Single" ):
            return(1)
        elif(self.type_of_dynamic_graph == "Multiple"):
            return(self.d-len(neigh))

    def get_type_of_dynamic_graph(self):
        return(self.type_of_dynamic_graph)

    def get_sample_del_phase(self,neigh):
        if(self.type_of_dynamic_graph == "Single" ):
            return(1)
        elif(self.type_of_dynamic_graph == "Multiple"):
            return(len(neigh)-self.tolerance)

    def add_phase(self):
        nodes = list(self.G.nodes())
        edge_list = []
        for i in nodes:
            neighbors = [n for n in self.G.neighbors(i)]
            if (len(neighbors) < self.d):
                # Calculating the set of the elements over random sampling
                if (len(neighbors) > 0):
                    app = list(set(nodes) - set(neighbors) - set([i]))
                else:
                    app = list(set(nodes) - set([i]))
                if (app):
                    # Converting in int the element sampled over the list
                    # Calculating the sample size
                    sample_size = self.get_sample_add_phase(neighbors)
                    v_sample = rnd.choices(app,k=sample_size)
                    # Adding the edge (i,v) to the graph
                    edge_list.append((i, int(v_sample[0])))
        # Now we have to transform the directed edge list in ad undirected edge list
        preprocessed = []
        for i in edge_list:
            if i[0] > i[1]:
                preprocessed.append((i[1], i[0]))
            else:
                preprocessed.append((i[0], i[1]))
        # Adding the undirected edge list to the graph
        self.G.add_edges_from(list(set(preprocessed)))

    # Del phase where nodes with |N(u)|>c*d choose u.a.r. a list of nodes in there Neighborhood and disconnect from it
    def del_phase(self):
        nodes = list(self.G.nodes())
        edge_list = []
        for i in nodes:
            neig = [n for n in self.G.neighbors(i)]
            if (len(neig) > self.tolerance):
                # Calculating the sample size

                sample_size = self.get_sample_del_phase(neig)

                # Sampling a node from the neighborhood
                v_sample = rnd.choices(neig,k=sample_size)
                # Adding the samples to the list of nodes to remove
                edge_list.append((i, int(v_sample[0])))
        # Now we have to transform the directed edge list in ad undirected edge list
        preprocessed = []
        for i in edge_list:
            if i[0] > i[1]:
                preprocessed.append((i[1], i[0]))
            else:
                preprocessed.append((i[0], i[1]))
        # Removing the undirected edge list from the graph
        self.G.remove_edges_from(list(set(preprocessed)))

    # Check function that return True if exist u in V s.t. [ d > |N(u)| or |N(u)|> c*d ]
    # This function return True if the graph is not regular and False otherwise
    def isregular(self):
        for u in list(self.G.nodes()):
            # If that controls the degree of each node in the graph
            # If there is a node with |N(u)|< d or |N(u)|> c*d
            # the generating process can't stop, so we return True
            if (self.d > self.G.degree(u) or self.G.degree(u) >self.tolerance):
                return True
        # If all nodes have degree d <=|N(u)| <= c*d  then the process can stop
        # so we return False
        return False

    # Check function that return True if exist u in V s.t. [ d > |N(u)| or |N(u)|> c*d ]
    # This function return True if the graph is not regular and False otherwise
    def is_strictly_regular(self):
        for u in list(self.G.nodes()):
            # If that controls the degree of each node in the graph
            # If there is a node with |N(u)|< d or |N(u)|> c*d
            # the generating process can't stop, so we return True
            if (self.d != self.G.degree(u)):
                return True
        # If all nodes have degree d <=|N(u)| <= c*d  then the process can stop
        # so we return False
        return False

    # Function that iterate on all edges in the graph and delete them with probability p
    def random_fall(self):
        for e in list(self.G.edges()):
            if (flip(self.p) == 'H'):
                self.G.remove_edge(e[0], e[1])

    # Function for nodes accessing the network following a Poisson Flow
    def connect_to_network(self):
        # Poisson Process of parameter Lambda for the number of nodes accessing in the network
        X_t = np.random.poisson(self.inrate)
        # Getting the maximum label in the Graph
        nodes = self.get_list_of_nodes()
        if(nodes):
            max_label = max(nodes)
        else:
            max_label = -1
        # Defining labels of the new nodes
        entering_nodes = []
        for i in range(X_t):
            entering_nodes.append(max_label + 1)
            max_label += 1
        # Adding the list of nodes in the Graph
        self.G.add_nodes_from(entering_nodes)
        if (self.flooding.get_started() ):
            self.flooding.add_nodes_to_dictionary(entering_nodes)

        if(self.consensus.get_started()):
            new_nodes_colors = []
            for i in entering_nodes:
                if (flip(self.consensus_bias[0]) == 'H'):
                    new_nodes_colors.append(0)
                else:
                    new_nodes_colors.append(1)
            self.consensus.add_nodes_to_dictionary(entering_nodes,new_nodes_colors)
        if(not self.target_density):
            self.target_density = self.target_size_achieved()
        self.set_max_label(X_t)
        self.set_number_of_entering_nodes_at_each_round(X_t)

    # Function that delete agets from the network with probability q
    def disconnect_from_network(self):
        # Random variable that counts the number of nodes that exits the network
        Z_t = 0
        # List of exiting nodes
        exiting_nodes = []
        # Doing a Bernoulli experiment for each node of the network
        # With probability q a node leave the Graph
        nodes = self.get_list_of_nodes()
        for u in nodes:
            if (flip(self.outrate) == "H"):
                self.G.remove_node(u)
                exiting_nodes.append(u)
                Z_t += 1
        if (self.flooding.get_started()):
            self.flooding.del_nodes_from_dictionary(exiting_nodes)

        if(self.consensus.get_started()):
            self.consensus.del_nodes_from_dictionary(exiting_nodes)
        self.set_number_of_exiting_nodes_at_each_round(Z_t)


    def target_size_achieved(self):
        if(len(self.G.nodes()) >=self.target_n ):
            return True
        return False


    def get_percentage(self,bool):
        # a = self.range_percentage[0]
        # b = self.range_percentage[1]
        m = mt.ceil((self.b - self.a) / 2)
        # print("M=",m)
        # print("B= ",self.b)
        # print("A = ",self.a)
        if(bool):
            self.a = mt.ceil( (self.b-self.a ) / 2) + self.a

            self.aolds.append(self.a)
        else:
            self.b = m
            self.a = self.aolds[-1]
            #self.aolds.pop()
        self.bolds.append(self.b)
        self.semiregular_percentage = self.b




    def edge_markovian(self):

        edges = self.get_list_of_edges()
        new_edges = []
        falling_edges = []
        # Falling phase
        for e in edges:
            if(flip(self.death_rate) == 'H'):
                falling_edges.append(e)
        # Birth phase

        birth_candidates = set(self.kn_edges) - set(edges)
        for e in birth_candidates:
            if(flip(self.birth_rate) == 'H'):
                new_edges.append(e)
        # Updating the graph
        self.G.remove_edges_from(falling_edges)
        self.G.add_edges_from(new_edges)




    def get_a(self):
        return(self.a)
    def get_b(self):
        return(self.b)