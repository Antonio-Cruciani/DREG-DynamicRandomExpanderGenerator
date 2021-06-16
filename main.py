#!/usr/bin/python
from src.Algorithms.VertexDynamic import VertexDynamic
from src.Algorithms.EdgeDynamic import EdgeDynamic
import sys, getopt
import logging
import json
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