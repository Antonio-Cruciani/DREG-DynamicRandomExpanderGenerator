#!/usr/bin/python
from src.Algorithms.VertexDynamic import VertexDynamic
from src.Algorithms.EdgeDynamic import EdgeDynamic
import sys, getopt
import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

def main(argv):
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
                d.append(int(elem))
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
                inRate.append(int(elem))
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


    if(algorithm == "VD"):

        ex = VertexDynamic(d,c,inRate,outRate,outPath,flooding=flood,regular_decay=0.5,model = model,simNumber=simNumber)
        ex.run()
    elif(algorithm == "ED"):

        ex = EdgeDynamic(d ,c,p,n ,outPath ,flooding = flood, epsilon = epsilon ,model =model,simNumber = simNumber )
        ex.run()


if __name__ == "__main__":
   main(sys.argv[1:])