from src.Analysis.Analyze import process_data
import sys,getopt,logging
from os import walk
import os
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


def main(argv):
    outputPath = "./"
    inputPath =" "
    all = True
    #print(output,input)
    try:
        opts,args = getopt.getopt(argv,"hi:o:",["--input","--output"])
    except getopt.GetoptError:
        logging.error("ERROR!")
        sys.exit(2)
    for opt,arg in opts:
        if(opt == "-i"):
            inputPath = arg
        if(opt == "-o"):
            outputPath = arg
        if(opt == "-a"):
            if(arg == "False"):
                all = False
    if(all):
        f = []
        for (dirpath, dirnames, filenames) in walk(inputPath):
            f.append(dirnames)
            break

        for dir in f[0]:

            process_data(inputPath+dir+"/results.csv",outputPath)
    else:
        process_data(inputPath,outputPath)




if __name__ == "__main__":
    main(sys.argv[1:])

#  input = "/home/antonio/Desktop/DynamicGraphs/SimulazioniNuovoModello/VertexDynamic_in_1_out_0.01_f_True/results.csv"
#     output = "/home/antonio/Desktop/Analizzati/"

# -i "/home/antonio/Desktop/DynamicGraphs/SimulazioniNuovoModello/VertexDynamic_in_1_out_0.01_f_True/results.csv" -o "/home/antonio/Desktop/Analizzati/"