
import sys,getopt,logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


def DataAnalysis(argv):
    outputPath = "./"
    inputPath =""
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




if __name__ == "__DataAnalysis__":
    DataAnalysis(sys.argv[1:])
