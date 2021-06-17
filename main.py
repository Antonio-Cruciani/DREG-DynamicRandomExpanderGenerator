
from src.Algorithms.VertexDynamic import VertexDynamic
from src.Algorithms.EdgeDynamic import EdgeDynamic
import sys, getopt
import logging
import json
import configparser

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

'''def main(argv):
    algorithm = ""
    model = "Multiple"
    d = []
    c = []
    p = []
    inRate = []
    outRate = []
    n = []
    flood = True
    simNumber = 30
    epsilon =0.05

    outPath = "./"
    try:
        opts, args = getopt.getopt(argv, "hg:n:d:c:p:r:q:f:x:s:m:e:o:", ["graph=","nodes=","deg=","const=","prob=","rate=","quit=","flood=","decay=","sim=","model=","epsilon=" ,"ofile="])
    except getopt.GetoptError:
        logging.error("ERROR!")
        sys.exit(2)
    for opt,arg in opts:
        if (opt == "-h"):
            logging.info("HELPER")
            logging.info("TODO")
            sys.exit()
        elif(opt in("-g","--graph")):
            algorithm = arg
        elif(opt in ("-n","--nodes")):
            splittedInput = arg.split(",")
            for elem in splittedInput:
                n.append(int(elem))
        elif(opt in ("-d","--deg")):
            splittedInput = arg.split(",")
            for elem in splittedInput:
                d.append(float(elem))
        elif(opt in ("-c","--const")):
            splittedInput = arg.split(",")
            for elem in splittedInput:
                c.append(float(elem))
        elif(opt in ("-p","--prob")):
            splittedInput = arg.split(",")
            for elem in splittedInput:
                p.append(float(elem))
        elif (opt in ("-r", "--rate")):
            splittedInput = arg.split(",")
            for elem in splittedInput:
                inRate.append(float(elem))
        elif (opt in ("-q", "--quit")):
            splittedInput = arg.split(",")
            for elem in splittedInput:

                outRate.append(float(elem))
        elif (opt in ("-f", "--flood")):
            if(arg == "False" or arg == "false"):
                flood = False
        elif (opt in ("-a", "--decay")):
            if(float(arg)>=1):
                logging.error("ERROR ! Decay must be 0<= decay <1")
            else:
                decay = float(arg)
        elif(opt in ("-s","--sim")):
            simNumber = int(arg)
        elif(opt in ("-m","--model")):
            model = arg
        elif(opt in ("-e","--epsilon")):
            epsilon = float(arg)
        elif(opt in ("-o","--outfile")):
            outPath = arg
'''


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    nodes = []
    degrees = []
    tolerances = []
    probabilities = []

    flooding = False
    simulations = 30
    only_spectral = False
    offline = False

    gpu_opt = False
    eps = 0.005
    max_iter = 100

    outPath = "./"

    in_rates = []

    if (config['advanced']['min_degree'] != "None" and config['advanced']['max_degree'] != "None" and
            config['advanced']['step_degree'] != "None"):
        min_degree = int(config['advanced']['min_degree'])
        max_degree = int(config['advanced']['max_degree'])
        step_degree = int(config['advanced']['step_degree'])
        degrees = [x + min_degree for x in range(min_degree, max_degree, step_degree)]
    else:
        string_degrees = config['model']['degree'][1:-1]
        string_degrees_split = string_degrees.split(",")
        degrees = [int(d) for d in string_degrees_split]

    if (config['advanced']['min_tolerance'] != "None" and config['advanced']['max_tolerance'] != "None" and
            config['advanced']['step_tolerance'] != "None"):
        min_tolerance = int(config['advanced']['min_tolerance'])
        max_tolerance = int(config['advanced']['max_tolerance'])
        step_tolerance = int(config['advanced']['step_tolerance'])
        tolerances = [x + min_tolerance for x in range(min_tolerance, max_tolerance, step_tolerance)]
    else:
        string_tolerances = config['model']['tolerance'][1:-1]
        string_tolerances_split = string_tolerances.split(",")
        tolerances = [float(c) for c in string_tolerances_split]

    if (config['advanced']['min_edge_node_falling_probability'] != "None" and config['advanced']['max_edge_node_falling_probability'] != "None" and
            config['advanced']['step_edge_node_falling_probability'] != "None"):
        min_probability = int(config['advanced']['min_edge_node_falling_probability'])
        max_probability = int(config['advanced']['max_edge_node_falling_probability'])
        step_probability = int(config['advanced']['step_edge_node_falling_probability'])
        probabilities = [x + min_probability for x in range(min_probability, max_probability, step_probability)]
    else:
        string_probability = config['model']['edge_node_falling_probability'][1:-1]
        string_probability_split = string_probability.split(",")
        probabilities = [float(p) for p in string_probability_split]

    flooding = config['simulations']['flooding_protocol'] in ['true', '1', 't', 'y', 'True']
    simulations = int(config['simulations']['simultaions_number'])
    only_spectral = config['simulations']['only_spectral_properties'] in ['true', '1', 't', 'y', 'True']
    offline = config['simulations']['offline_simulation'] in ['true', '1', 't', 'y', 'True']

    gpu_opt = config['other_parameters']['gpu_optimization'] in ['true', '1', 't', 'y', 'True']
    eps = float(config['other_parameters']['epsilon'])
    max_iter = int(config['other_parameters']['max_iterations'])

    if (config['advanced']['min_nodes'] != "None" and config['advanced']['max_nodes'] != "None" and config['advanced'][
        'step_nodes'] != "None"):
        min_nodes = int(config['advanced']['min_nodes'])
        max_nodes = int(config['advanced']['max_nodes'])
        step_nodes = int(config['advanced']['step_nodes'])
        nodes = [x + min_nodes for x in range(min_nodes, max_nodes, step_nodes)]
    else:
        string_nodes = config['model']['nodes'][1:-1]
        string_nodes_split = string_nodes.split(",")
        nodes = [int(n) for n in string_nodes_split]

    outPath = config['output_path']['outputpath']

    if(config['model']['graph'] == 'ED'):

        ex = EdgeDynamic(degrees, tolerances, probabilities, nodes, outPath, flooding=flooding, epsilon=eps, model="Multiple",
                         simNumber=simulations, maxIter=max_iter, onlySpectral=only_spectral, Offline=offline, GPU=gpu_opt)
        ex.run()

    elif(config['model']['graph'] == 'VD'):

        if (config['advanced']['min_nodes_poisson_rate'] != "None" and config['advanced']['max_nodes_poisson_rate'] != "None" and
                config['advanced']['step_nodes_poisson_rate'] != "None"):
            min_poisson = int(config['advanced']['min_nodes_poisson_rate'])
            max_poisson = int(config['advanced']['max_nodes_poisson_rate'])
            step_poisson = int(config['advanced']['step_nodes_poisson_rate'])
            in_rates = [x + min_poisson for x in range(min_poisson, max_poisson, step_poisson)]
            ex = VertexDynamic(degrees, tolerances, in_rates, probabilities, outPath, flooding=flooding, regular_decay=0.5,
                               model="Multiple", simNumber=simulations, maxIter=max_iter, onlySpectral=only_spectral,
                               Offline=offline, GPU=gpu_opt)
            ex.run()




        elif(config['model']['nodes_poisson_rate'] != "None"):
            string_poisson = config['model']['nodes_poisson_rate'][1:-1]
            string_poisson_split = string_poisson.split(",")
            in_rates = [float(l) for l in string_poisson_split]

            ex = VertexDynamic(degrees, tolerances, in_rates, probabilities, outPath, flooding=flooding,
                               regular_decay=0.5,
                               model="Multiple", simNumber=simulations, maxIter=max_iter, onlySpectral=only_spectral,
                               Offline=offline, GPU=gpu_opt)
            ex.run()


        else:
            inputs = []
            for n in nodes:
                for x in probabilities:
                    inputs.append([n * x, x])
            for elem in inputs:
                ex = VertexDynamic(degrees, tolerances, [elem[0]], [elem[1]], outPath, flooding=flooding, regular_decay=0.5,
                                   model="Multiple", simNumber=simulations, maxIter=max_iter, onlySpectral=only_spectral,
                                   Offline=offline, GPU=gpu_opt)
                ex.run()



def main1():
    with open('./properties.json') as f:
        properties = json.load(f)
    algorithm = properties['dynamicGraph']
    n_list = properties['n']
    d_list = properties['d']
    c_list = properties['c']
    outPath = properties['outputPath']
    flood =  properties['flooding'] in ['true', '1', 't', 'y', 'True']
    simNumber = properties['simulations']
    onlySpectral = properties["onlySpectral"] in ['true', '1', 't', 'y', 'True']
    offline = properties["offline"] in ['true', '1', 't', 'y', 'True']
    gpu = properties["gpuLinearAlgebra"] in ['true', '1', 't', 'y', 'True']
    max_iter = properties['max_iter']

    model = "Multiple"
    if(algorithm == "VD"):
        q_list = properties['q']
        if(properties['lambda']):
            inRate = properties['lambda']
            ex = VertexDynamic(d_list, c_list, inRate, q_list, outPath, flooding=flood, regular_decay=0.5,
                               model="Multiple",  simNumber=simNumber,maxIter=max_iter,onlySpectral=onlySpectral,Offline=offline,GPU=gpu)
            ex.run()

        else:
            inputs = []
            for n in n_list:
                for x in q_list:
                    inputs.append([n * x, x])
            for elem in inputs:
                ex = VertexDynamic(d_list, c_list, [elem[0]], [elem[1]], outPath, flooding=flood, regular_decay=0.5,
                                   model="Multiple", simNumber=simNumber,maxIter=max_iter,onlySpectral=onlySpectral,Offline=offline,GPU=gpu)
                ex.run()


    elif(algorithm == "ED"):
        p_list = properties['p']
        epsilon = properties['epsilon']
        ex = EdgeDynamic(d_list ,c_list,p_list,n_list ,outPath ,flooding = flood, epsilon = epsilon ,model =model,simNumber = simNumber,maxIter=max_iter,onlySpectral=onlySpectral,Offline = offline,GPU = gpu )
        ex.run()


if __name__ == "__main__":
   #main(sys.argv[1:])
   main()