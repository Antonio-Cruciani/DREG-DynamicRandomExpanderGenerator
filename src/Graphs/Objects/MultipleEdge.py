import networkx as nx
import random as rnd
import numpy as np
import math as mt
import scipy
import scipy.sparse
import threading
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor

from src.MathModules.MathTools import flip
from src.Protocols.FloodOBJ import Flooding
from src.Protocols.Consensus import Consensus
class DynamicGraph:

    def __init__(self,n = 0,d = 4,c = 1.5,lam = 1 ,beta = 1,falling_probability = 0,model = None ,starting_edge_list = [],edge_birth_rate = None, edge_death_rate = None):
        """

        :param n: int, number of nodes.
        :param d: int, minimum degree that each node must have
        :param c: float, tolerance constant d*c defines the maximum degree that each node can have
        :param lam: float, intensity parameter of the Poisson process
        :param beta: float, node-falling probability of each node
        :param falling_probability: float, edge-falling probability
        :param model: string, model type
        :param starting_edge_list: list, edge list of the graph at time 0
        :param edge_birth_rate:
        :param edge_death_rate:
        """
        self.G = nx.Graph()
        self.entering_nodes =[]
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
        self.time_conv = 0
        self.reset_number = 0
        self.t = 0
        self.max_label = -1
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

    def add_MT(self,u):
        nodes = list(self.G.nodes())
        neighbors = [n for n in self.G.neighbors(u)]
        edge_list = []

        if (len(neighbors) < self.d):
            # Calculating the set of the elements over random sampling
            if (len(neighbors) > 0):
                app = list(set(nodes) - set(neighbors) - set([u]))
            else:
                app = list(set(nodes) - set([u]))
            if (app):
                # Converting in int the element sampled over the list
                # Calculating the sample size
                sample_size = self.get_sample_add_phase(neighbors)
                v_sample = np.random.choice(app, size=sample_size)
                # Adding the edge (i,v) to the graph
                for x in v_sample:
                    edge_list.append((u, int(x)))


        return(edge_list)


    def add_phase_MT(self):
        nodes = list(self.G.nodes())
        edge_list = []

        with ThreadPoolExecutor(32) as executor:
            results = executor.map(self.add_MT, nodes)

        for result in results:
            edge_list.extend(result)
        # Adding the undirected edge list to the graph
        self.G.add_edges_from(list(set(edge_list)))

    def del_MT(self,u):

        edge_list = []
        neig = [n for n in self.G.neighbors(u)]


        if (len(neig) > self.tolerance):
            # Calculating the sample size

            sample_size = self.get_sample_del_phase(neig)

            # Sampling a node from the neighborhood
            v_sample = np.random.choice(neig, size=sample_size)
            # Adding the samples to the list of nodes to remove
            for x in v_sample:
                edge_list.append((u, int(x)))

        return (edge_list)

    def del_phase_MT(self):
        nodes = list(self.G.nodes())
        edge_list = []
        with ThreadPoolExecutor(32) as executor:
            results = executor.map(self.del_MT, nodes)
        for result in results:
            edge_list.extend(result)

        # Removing the undirected edge list from the graph
        # Now we have to transform the directed edge list in ad undirected edge list
        for edge in edge_list:
            try:
                self.G.remove_edge(edge)
            except:
                continue

    def fall_MT(self,e):
        if (flip(self.p) == 'H'):
            return [(e[0], e[1])]
        return [None]
    def random_fall_MT(self):
        edges = list(self.G.edges())
        edge_list = []
        with ThreadPoolExecutor(32) as executor:
            results = executor.map(self.fall_MT, edges)
        for result in results:
            edge_list.extend(result)
        for edge in edge_list:
            if edge != None:
                try:
                    self.G.remove_edge(edge[0],edge[1])
                except:
                    continue


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
                    v_sample = np.random.choice(app, size=sample_size)
                    # Adding the edge (i,v) to the graph
                    for x in v_sample:
                        edge_list.append((i, int(x)))
        # Now we have to transform the directed edge list in ad undirected edge list
        '''preprocessed = []
        for i in edge_list:
            if i[0] > i[1]:
                preprocessed.append((i[1], i[0]))
            else:
                preprocessed.append((i[0], i[1]))'''
        # Adding the undirected edge list to the graph
        self.G.add_edges_from(edge_list)

    def add_phase_dep(self):
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
                    v_sample = np.random.choice(app,size=sample_size)
                    # Adding the edge (i,v) to the graph
                    for x in v_sample:
                        edge_list.append((i, int(x)))
        # Now we have to transform the directed edge list in ad undirected edge list
        preprocessed = []
        for i in edge_list:
            if i[0] > i[1]:
                preprocessed.append((i[1], i[0]))
            else:
                preprocessed.append((i[0], i[1]))
        # Adding the undirected edge list to the graph
        self.G.add_edges_from(list(set(preprocessed)))


    def del_phase(self):
        self.t +=1
        nodes = list(self.G.nodes())
        edge_list = []
        for i in nodes:
            neig = [n for n in self.G.neighbors(i)]
            if (len(neig) > self.tolerance):
                # Calculating the sample size

                sample_size = self.get_sample_del_phase(neig)

                # Sampling a node from the neighborhood
                v_sample = np.random.choice(neig,size=sample_size)
                # Adding the samples to the list of nodes to remove
                for x in v_sample:
                    edge_list.append((i, int(x)))
        # Now we have to transform the directed edge list in ad undirected edge list
        for edge in edge_list:
            try:
                self.G.remove_edge(edge)
            except:
                continue

    # Del phase where nodes with |N(u)|>c*d choose u.a.r. a list of nodes in there Neighborhood and disconnect from it
    def del_phase_dep(self):
        self.t +=1
        nodes = list(self.G.nodes())
        edge_list = []
        for i in nodes:
            neig = [n for n in self.G.neighbors(i)]
            if (len(neig) > self.tolerance):
                # Calculating the sample size

                sample_size = self.get_sample_del_phase(neig)

                # Sampling a node from the neighborhood
                v_sample = np.random.choice(neig,size=sample_size)
                # Adding the samples to the list of nodes to remove
                for x in v_sample:
                    edge_list.append((i, int(x)))
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

    def random_fall_dep(self):
        removed = []
        survived = []
        for e in list(self.G.edges()):
            if (flip(self.p) == 'H'):
                removed.append(e)
            else:
                survived.append(e)
        if(len(survived)<=len(removed)):
            G = nx.Graph()
            G.add_nodes_from([i for i in range(0, self.n)])
            for e in survived:
                G.add_edge(e[0],e[1])
            self.G = G
        else:
            for e in removed:
                self.G.remove_edge(e[0], e[1])

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
        #nodes = self.get_list_of_nodes()
        # if(nodes):
        #     max_label = max(nodes)
        # else:
        #     max_label = -1
        # Defining labels of the new nodes
        entering_nodes = []
        # for i in range(X_t):
        #     entering_nodes.append(max_label + 1)
        #     max_label += 1
        for i in range(X_t):
            #entering_nodes.append(str(self.max_label + 1))
            entering_nodes.append(self.max_label + 1)

            self.max_label += 1
        # Adding the list of nodes in the Graph
        self.G.add_nodes_from(entering_nodes)
        self.entering_nodes = entering_nodes
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

    def get_nodes_t(self):
        return(len(self.G.nodes()))
    def target_size_achieved(self):
        if(len(self.G.nodes()) >=self.target_n ):
            return True
        return False

    # Struttura del nuovo modello vertex dynamic:
    # 1) Entrano nuovi nodi
    # 2) Escono dei nodi
    # 3) I nodi al presenti nel grafo anche al tempo I-1 fanno raes tra di loro
    # 4) I nodi che sono entrati al tempo I fanno raes verso quelli al tempo I-1
    # NOTA 3)-4) deve essere in parallelo non seriale
    # 5) Esegui flooding step sul grafo al tempo I
    # Nota parametro di convergenza del flooding alpha

    #def vertex_dynamic_add(self):
        # RAES ESEGUITO TRA I NODI AL TEMPO I-1
        # RAES ESEGUITO TRA I NODI ENTRANTI VERSO QUELLI AL TEMPO I-1

    def add_phase_vd(self):
        nodes = list(set(self.G.nodes())-set(self.entering_nodes))
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
                    v_sample = np.random.choice(app,size=sample_size)
                    # Adding the edge (i,v) to the graph
                    edge_list.append((i, int(v_sample[0])))
        # If is not the first round and there are nodes in the network,
        # then the new nodes sample d vertices in the network

        if (self.t > 0 and len(nodes) > 0):

            # New nodes are connecting to the network
            survived_entering_nodes = list(set(self.entering_nodes).intersection(set(self.G.nodes())))
            if (len(survived_entering_nodes) > 0):

                for i in survived_entering_nodes:
                    sample_size = self.get_sample_add_phase([])

                    v_sample = np.random.choice(nodes, size=sample_size)
                    for x in v_sample:
                        #edge_list.append((i, str(x)))
                        edge_list.append((i, int(x)))



                #print(edge_list)
        # Now we have to transform the directed edge list in ad undirected edge list
        preprocessed = []
        for i in edge_list:
            if int(i[0] )> int(i[1]):
                preprocessed.append((i[1], i[0]))
            else:
                preprocessed.append((i[0], i[1]))
        # Adding the undirected edge list to the graph
        self.G.add_edges_from(list(set(preprocessed)))


        # Del phase where nodes with |N(u)|>c*d choose u.a.r. a list of nodes in there Neighborhood and disconnect from it

    def del_phase_vd(self):
        self.t += 1
        nodes = list(set(self.G.nodes())-set(self.entering_nodes))
        edge_list = []
        lista_rimozioni = []
        for i in nodes:
            neig = [n for n in self.G.neighbors(i)]
            if (len(neig) > self.tolerance):
                # Calculating the sample size
                sample_size = self.get_sample_del_phase(neig)
                # Sampling a node from the neighborhood
                v_sample = np.random.choice(neig, size=sample_size)

                lista_rimozioni.append(i)
                # Adding the samples to the list of nodes to remove
                for x in v_sample:
                    #edge_list.append((str(i), str(x)))
                    edge_list.append((int(i), int(x)))

        # Now we have to transform the directed edge list in ad undirected edge list
        #preprocessed = []
        #set_preprocessed = list(set(edge_list))
        preprocessed = edge_list
                # Removing the undirected edge list from the graph
        #print(list(set(preprocessed)))
        to_delete  =list(set(preprocessed))

        self.G.remove_edges_from(to_delete)
        #self.G.remove_edges_from(list(preprocessed))


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


