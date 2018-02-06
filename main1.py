from time import time
from random import choice, shuffle
from argparse import ArgumentParser
from NDresults import NDresults
from NDChild import NDChild
from Sentence import Sentence
from sys import exit
import csv
from csv import writer
import multiprocessing
from multiprocessing import Queue, Pool
#GLOBALS
rate = 0.02
conservativerate = 0.001
threshold = .001
results=[]
def pickASentence(languageDomain):
    return choice(languageDomain)

def timefn(fun):
    def wrapper(*args, **kwargs):
        start = time()
        val = fun(*args, **kwargs)
        print "{}({}, {}) took {}".format(fun.__name__,
                                          args, kwargs,
                                          time() - start)
        return val
    return wrapper

@timefn
def readLD(path):
    domain = {}
    with open(path, 'r') as infoFile:
        for line in infoFile:
            [grammStr, inflStr, sentenceStr] = line.split("\t")
            sentenceStr = sentenceStr.rstrip()
            inflStr=inflStr.replace(" ","")
            #print(sentenceStr)
            # constructor creates sentenceList
            s = Sentence([grammStr, inflStr, sentenceStr])
            try:
                domain[grammStr].append(s)
            except:
                domain[grammStr] = [s]
    return domain

start = time()
COLAG_DOMAIN = readLD('COLAG_2011_flat_formatted.txt')

def createLD(language):
    #languageDict = {'english': '611', 'french': '584', 'german': '2253', 'japanese': '3856'}
    langNum = language
    #print "type langnum"
    #print type(langNum)
    langNum=bin(int(langNum))[2:].zfill(13)
    #print(langNum)
    return COLAG_DOMAIN[langNum]

def childLearnsLanguage(ndr, languageDomain,language,numberofsentences):
    ndr.resetThresholdDict()
    aChild = NDChild(rate, conservativerate, language)

    #print numberofsentences
    for j in xrange(numberofsentences):
        s = pickASentence(languageDomain)
        aChild.consumeSentence(s)
        # If a parameter value <= to the threshold for the first time,
        # this is recorded in ndr for writing output
        ndr.checkIfParametersMeetThreshold(threshold, aChild.grammar, j)

    return [aChild.grammar, ndr.thresholdDict]

def runSingleLearnerSimulation(languageDomain, numLearners, numberofsentences, language):
    # Make an instance of NDresults and write the header for the output file
    ndr = NDresults()
    #ndr.writeOutputHeader(language, numLearners, numberofsentences)
    # Create an array to store the simulation
    # results to write to a csv after its ended

    print("Starting the simulation...")
    result = [childLearnsLanguage(ndr, languageDomain,language,numberofsentences) for x in range(numLearners)]
    return result

@timefn
def runOneLanguage(numLearners, numberofsentences, language):
    if numLearners < 1 or numberofsentences < 1:
        print('Arguments must be positive integers')
        exit(2)

    LD = createLD(language)

    return runSingleLearnerSimulation(LD, numLearners, numberofsentences, language)

# Run random 100 language speed run
def runSpeedTest(numLearners, numberofsentences):
    # Make dictionary containing first 100
    # language IDs from the full CoLAG domain

    languageDict = {}
    with open('COLAG_Flat_GrammID_Binary_List.txt','r') as myfile:
        head = [next(myfile) for x in xrange(3)]

    for line in head:
        binaryId, decimalId = line.split('\t')
        languageDict[binaryId] = []

    # Collect the corresponding sentences for each language
    with open('COLAG_2011_flat_formatted.txt', 'r') as infoFile:
        for line in infoFile:
            [grammStr, inflStr, sentenceStr] = line.split("\t")

            if grammStr in languageDict:
                sentenceStr = sentenceStr.rstrip()
                # constructor creates sentenceList
                s = Sentence([grammStr, inflStr, sentenceStr])
                languageDict[grammStr].append(s)

    # Run 100 eChildren for each language
    for key, value in languageDict.iteritems():
        language = str(int(key, 2))
        runSingleLearnerSimulation(value, numLearners, numberofsentences, language)

def runAllCoLAGLanguages(numLearners, numberofsentences):
    # Build a dictionary that contains the sentences that
    # correspond to every language
    languageDict = {}
    with open('COLAG_2011_flat_formatted.txt', 'r') as sentencesFile:
        for line in sentencesFile:
            [grammStr, inflStr, sentenceStr] = line.split("\t")

            sentenceStr = sentenceStr.rstrip()
            # constructor creates sentenceList
            s = Sentence([grammStr, inflStr, sentenceStr])
            languageDict[grammStr].append(s)

    # Iterate therough the dictionary and run a simulation for each language
    for key, value in languageDict.iteritems():
        language = str(int(key, 2))
        runSingleLearnerSimulation(value, numLearners, numberofsentences, language)

def runLangWrapper(args):
    return runOneLanguage(*args)

if __name__ == '__main__':
    q=Queue()
    parser = ArgumentParser(prog='Doing Away With Defaults', description='Set simulation parameters for learners')
    parser.add_argument('integers', metavar='int', type=int, nargs=2,
                        help='(1) The number of learners (2) The number of '
                         'sentences consumed')

    args = parser.parse_args()
    numLearners = 0

    # Test whether certain command line arguments
    # can be converted to positive integers
    numLearners = args.integers[0]
    numberofsentences = args.integers[1]
    #language = str(args.strings[0]).lower()

    languages=[]
    with open('COLAG_Flat_GrammID_Binary_List.tsv', 'rb') as tsvin:
        tsvin = csv.reader(tsvin, delimiter='\t')
        for row in tsvin:
            languages.append(row.pop(0))
    pool = Pool(4)
    arguments = [(numLearners, numberofsentences, lang)
                     for lang in languages]
    results = pool.map(runLangWrapper, arguments)

    outputfile = 'simulation-output3.csv'
    with open(outputfile, "a+b") as outFile:
        outWriter = writer(outFile)
        pList = ["lang", "SP", "HIP", "HCP", "OPT", "NS", "NT", "WHM", "PI", "TM", "VtoI", "ItoC", "AH", "QInv"]
        for result in results:
            for index, r in enumerate(result):
                str1 = 'eChild {}'.format(index)
                r1 = []
                for p in pList:
                    r1.append(r[0][p])
                    r1.append(r[1][p])
                outWriter.writerow(r1)

print("--- %s seconds ---" % (time() - start))
