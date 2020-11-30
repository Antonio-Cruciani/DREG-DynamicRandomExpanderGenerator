from src.Analysis.Objects.Samples import  Samples
from src.FileOperations.WriteOnFile import create_folder,create_file,write_on_file_contents
import pandas as pd


def write_info_dic_as_csv( outPath, results):
    create_file(outPath, list(results[0].keys()))

    write_on_file_contents(outPath, results)


def process_data(inputPath,outputPath):

    file = pd.read_csv(inputPath)

    # Getting and grouping all the simulations by the parameters

    d_list = list(set(file['d'].values))
    c_list = list(set(file['c'].values))
    sim_number = len(list(set(file['simulation'].values)))
    in_rate_list = list(set(file['lambda'].values))
    out_rate_list = list(set(file['beta'].values))

    results = []

    for r in in_rate_list:
        for q in out_rate_list:
            name = str(r)+"_"+str(q)
            create_folder(outputPath,name)
            output = outputPath + name +"/"

            for d in d_list:

                for c in c_list:
                    samples = file[(file['d'] == d)&(file['c'] == c)&(file['lambda'] == r)&(file['beta'] == q)]
                    stat = Samples(samples,output)
                    stat.get_flooding_stats()
                    stat.get_structural_stats()
                    stat.get_diameter_stats()
                    stat.plot_statistics()
                    results.append(stat.pack_and_get_stats())

    write_info_dic_as_csv(output+"analyzed",results)
#input = "/home/antonio/Desktop/DynamicGraphs/SimulazioniNuovoModello/VertexDynamic_in_1_out_0.001_f_True/results.csv"

