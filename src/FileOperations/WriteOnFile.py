import os
import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

def create_folder(path, dirname):
    path = path+"/"+dirname + "/"
    try:
        # Create target Directory
        os.mkdir(path)
        logging.info("Directory %s created" % (dirname))
        #print("Directory ", dirname, " Created ")
        return(path)
    except FileExistsError:
        logging.error("Directory %s already exists" % (dirname))
        #print("Directory ", dirname, " already exists")

def create_file(path,keys):
    file = open(path + '.csv', 'w+')
    for key in keys:
        file.write(str(key))
        file.write(",")
    file.write("\n")
    file.close()

def write_on_file_contents(filePath,dictionary_list):
    file = open(filePath + '.csv', 'a')
    for dictionary in dictionary_list:
        for key,value in dictionary.items():
            file.write(str(value))
            file.write(",")
        file.write("\n")
    file.close()

