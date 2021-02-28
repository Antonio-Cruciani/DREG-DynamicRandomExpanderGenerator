from src.Analysis.Analyze import process_data,process_and_get_unique_csv
import sys,getopt,logging
from os import walk
import os
import pandas as pd
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

def get_id(dataframe):
    return (dataframe['p'].values[0])

def main(argv):
    outputPath = "./"
    inputPath =" "
    all = True
    constrained = False
    #print(output,input)
    try:
        opts,args = getopt.getopt(argv,"hi:o:a:c:",["--input","--output","--all","--const"])
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
        if(opt == "-c"):
            if(arg == 'True'):
                constrained = True
    if(all):
        f = []
        filelist = []
        for (dirpath, dirnames, filenames) in walk(inputPath):
            f.append(dirnames)
            break

        for dir in f[0]:
            filelist.append(pd.read_csv(inputPath+dir+"/results.csv"))
        filelist.sort(key = lambda x: get_id(x) )
        process_data(filelist,outputPath)
        #process_data(inputPath+dir+"/results.csv",outputPath)
    elif(not(constrained)):
        process_data(inputPath,outputPath)
    else:
        f = []
        for (dirpath, dirnames, filenames) in walk(inputPath):
            f.append(dirnames)
            break

        d = 4
        c = 3
        process_and_get_unique_csv(inputPath, f[0], outputPath, d, c)


if __name__ == "__main__":
    main(sys.argv[1:])

#  input = "/home/antonio/Desktop/DynamicGraphs/SimulazioniNuovoModello/VertexDynamic_in_1_out_0.01_f_True/results.csv"
#     output = "/home/antonio/Desktop/Analizzati/"

# -i "/home/antonio/Desktop/DynamicGraphs/SimulazioniNuovoModello/VertexDynamic_in_1_out_0.01_f_True/results.csv" -o "/home/antonio/Desktop/Analizzati/"