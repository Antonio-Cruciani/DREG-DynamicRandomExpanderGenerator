#!/usr/bin/python
from src.Algorithms.VertexDynamic import VertexDynamic
#from src.Algorithms.EdgeDynamic import EdgeDynamic
import sys, getopt

def main(argv):
    algorithm = ""
    model = "Multiple"
    d = []
    c = []
    p = []
    inRate = []
    outRate = []
    flood = True
    simNumber = 30
    epsilon =0.05
    outPath = "./"
    try:
        opts, args = getopt.getopt(argv, "hg:d:c:p:r:q:f:x:s:m:e:o:", ["graph=","deg=","const=","prob=","rate=","quit=","flood=","decay=","sim=","model=","epsilon=" ,"ofile="])
    except getopt.GetoptError:
        print('Error!')
        sys.exit(2)
    for opt,arg in opts:
        if (opt == "-h"):
            print ("HELPER")
            print("TODO")
            sys.exit()
        elif(opt in("-g","--graph")):
            algorithm = arg
        elif(opt in ("-d","--deg")):
            splittedInput = arg.split(",")
            for elem in splittedInput:
                d.append(int(elem))
        elif(opt in ("-c","--const")):
            splittedInput = arg.split(",")
            for elem in splittedInput:
                c.append(int(elem))
        elif(opt in ("-p","--prob")):
            splittedInput = arg.split(",")
            for elem in splittedInput:
                p.append(int(elem))
        elif (opt in ("-r", "--rate")):
            splittedInput = arg.split(",")
            for elem in splittedInput:
                inRate.append(int(elem))
        elif (opt in ("-q", "--quit")):
            for elem in splittedInput:
                outRate.append(int(elem))
        elif (opt in ("-f", "--flood")):
            if(arg == "False" or arg == "false"):
                flood = False
        elif (opt in ("-d", "--decay")):
            if(float(arg)>=1):
                print(" ERROR ! Decay must be 0<= decay <1")
            else:
                decay = float(arg)
        elif(opt in ("-s","--sim")):
            simNumber = int(arg)
        elif(opt in ("-m","--model")):
            model = arg
        elif(opt in ("-e","--epsilon")):
            epsilon = float(arg)
        elif(opt in ("-0","--outfile")):
            outPath = arg

    if(algorithm == "VD"):
        ex = VertexDynamic(d,c,inRate,outRate,outPath,flooding=flood,regular_decay=decay,model = model,simNumber=simNumber)
    elif(algorithm == "ED"):
        print("TODO")


if __name__ == "__main__":
   main(sys.argv[1:])