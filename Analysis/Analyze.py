from Objects.Samples import Samples
import pandas as pd

def process_data(inputPath,outputPath=""):

    file = pd.read_csv(inputPath)

    # Getting and grouping all the simulations by the parameters

    d_list = list(set(file['d'].values))
    c_list = list(set(file['c'].values))
    sim_number = len(list(set(file['simulation'].values)))
    in_rate_list = list(set(file['lambda'].values))
    out_rate_list = list(set(file['beta'].values))

    results = {}

    for r in in_rate_list:
        for q in out_rate_list:
            for d in d_list:
                for c in c_list:
                    samples = file[(file['d'] == d)&(file['c'] == c)&(file['lambda'] == r)&(file['beta'] == q)]
                    stat = Samples(samples,"mario")
                    stat.get_flooding_stats()
                    stat.get_structural_stats()
                    stat.get_diameter_stats()
                    stat.plot_statistics()
                    exit(1)

#input = "/home/antonio/Desktop/DynamicGraphs/SimulazioniNuovoModello/VertexDynamic_in_1_out_0.001_f_True/results.csv"

input = "/home/antonio/Desktop/DynamicGraphs/SimulazioniNuovoModello/VertexDynamic_in_1_out_0.01_f_True/results.csv"

process_data(input)