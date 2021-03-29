from src.Analysis.Objects.Samples import  Samples
from src.FileOperations.WriteOnFile import create_folder,create_file,write_on_file_contents
import pandas as pd

def get_id(dataframe):
    return (dataframe['p'])

def write_info_dic_as_csv( outPath, results):
    create_file(outPath, list(results[0].keys()))

    write_on_file_contents(outPath, results)


def process_data(input_file,outputPath):

    #file = pd.read_csv(inputPath)
    raes_mean_spectrals = {}
    raes_median_spectrals = {}
    packing_list = []
    for file in input_file:

        # Getting and grouping all the simulations by the parameters

        d_list = list(set(file['d'].values))
        c_list = list(set(file['c'].values))
        sim_number = len(list(set(file['simulation'].values)))


        s_analysis = True
        results = []
        if("lambda" in list(file.keys())):
            in_rate_list = list(set(file['lambda'].values))
            out_rate_list = list(set(file['beta'].values))
            for r in in_rate_list:
                for q in out_rate_list:
                    name = str(r)+"_"+str(q)
                    create_folder(outputPath,name)
                    output = outputPath + name +"/"

                    for d in d_list:

                        for c in c_list:
                            samples = file[(file['d'] == d)&(file['c'] == c)&(file['lambda'] == r)&(file['beta'] == q)]
                            stat = Samples(samples,output)
                            if(s_analysis):
                                stat.get_spectral_analysis()
                            if("flood" in list(file.keys()) or "flood_status" in list(file.keys())):
                                stat.get_flooding_stats()
                                stat.get_structural_stats()
                                stat.get_diameter_stats()
                                stat.plot_statistics()

                            results.append(stat.pack_and_get_stats())
        else:
            residual = True


            n_list = list(set(file['n'].values))
            p_list = sorted(list(set(file['p'].values)))
            s_analysis = False
            if("spectralGapBefore" in list(file.keys())):
                s_analysis = True
            raes_mean_spectral_gap = 0
            raes_median_spectral_gap = 0
            for n in n_list:
                for p in p_list:
                    name = str(n) + "_" + str(p)
                    create_folder(outputPath, name)
                    output = outputPath + name + "/"
                    for d in d_list:

                        for c in c_list:
                            if(residual):
                                samples = file[
                                    (file['d'] == d) & (file['c'] == c) & (file['n'] == n) & (file['p'] == p)]
                                stat = Samples(samples, output)
                                if(s_analysis):
                                    stat.get_spectral_analysis()
                                    if(p == 0):
                                        raes_mean_spectrals[str((n,d,c)),'before'],raes_mean_spectrals[str((n,d,c)),'after'] = stat.get_mean_spectral_gap()
                                        raes_median_spectrals[str((n,d,c)),'before'],raes_median_spectrals[str((n,d,c)),'after'] = stat.get_median_spectral_gap()
                                        #raes_mean_spectral_gap = stat.get_mean_spectral_gap()
                                        #raes_median_spectral_gap = stat.get_median_spectral_gap()
                                    else:
                                        stat.get_spectral_gap_residuals(raes_mean_spectrals[str((n,d,c)),'before'],raes_mean_spectrals[str((n,d,c)),'after'] ,raes_median_spectrals[str((n,d,c)),'before'],raes_median_spectrals[str((n,d,c)),'after'])
                                if ("flood" in list(file.keys()) or "flood_status" in list(file.keys())):
                                    stat.get_flooding_stats()
                                stat.get_structural_stats()
                                stat.get_diameter_stats()
                                stat.plot_statistics()

                            else:
                                samples = file[
                                    (file['d'] == d) & (file['c'] == c) & (file['n'] == n) & (file['p'] == p)]
                                stat = Samples(samples, output)
                                if(s_analysis):
                                    stat.get_spectral_analysis()
                                if ("flood" in list(file.keys()) or "flood_status" in list(file.keys())):
                                    stat.get_flooding_stats()
                                stat.get_structural_stats()
                                stat.get_diameter_stats()
                                stat.plot_statistics()
                            results.append(stat.pack_and_get_stats())
        packing_list.append(results)
        write_info_dic_as_csv(output+"analyzed",results)
    # grouping by d and c and writing files for this groups
    create_folder(outputPath, "grouped_results")
    outGroupPath = outputPath + 'grouped_results' + "/"
    if("p" in list(packing_list[0][0].keys())):
        for d in d_list:
            for c in c_list:
                grouped = []
                for dics in packing_list:
                    for elem in dics:
                        if(elem['d'] == d and elem['c'] == c):
                            grouped.append(
                                            elem
                            )
                grouped.sort(key = lambda x: (x['p'],x['n']) )
                write_info_dic_as_csv(outGroupPath+'grouped_d_'+str(d)+'_c_'+str(c),grouped)

    else:
        for d in d_list:
            for c in c_list:
                grouped = []
                for dics in packing_list:
                    for elem in dics:
                        if (elem['d'] == d and elem['c'] == c):
                            grouped.append(
                                elem
                            )
                grouped.sort(key = lambda x: (x['r'],x['q']) )

                write_info_dic_as_csv(outGroupPath+'grouped_d_'+str(d)+'_c_'+str(c),grouped)

def process_and_get_unique_csv(inputPath,inputPathList,outputPath,d,c):
    results = []
    create_folder(outputPath,'single')
    outputPath = outputPath +"single/"

    for dir in inputPathList:
        file = pd.read_csv(inputPath+dir+"/results.csv")
        samples = file[(file['d'] == d) & (file['c'] == c)]
        r = samples['lambda'].values[0]
        q = samples['beta'].values[0]
        name = str(r) + "_" + str(q)
        create_folder(outputPath, name)
        output = outputPath + name + "/"

        stat = Samples(samples, output)
        stat.get_flooding_stats()
        stat.get_structural_stats()
        stat.get_diameter_stats()
        stat.plot_statistics()
        results.append(stat.pack_and_get_stats())
    write_info_dic_as_csv(outputPath+"unique_table",results)


#input = "/home/antonio/Desktop/DynamicGraphs/SimulazioniNuovoModello/VertexDynamic_in_1_out_0.001_f_True/results.csv"


