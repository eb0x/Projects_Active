# -*- coding: utf-8 -*-

from os import listdir
from os.path import isfile, join
import re
import sys
import string
import csv
import pickle

import nltk.data
from nltk.tokenize import sent_tokenize, word_tokenize, TreebankWordTokenizer
from nltk.tag import pos_tag_sents, pos_tag
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer

from CM0645db import Db

tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))  # map punctuation to space
stemmer = SnowballStemmer("english")

# if changing the folders, please comment out these lines and add your own
# it is easier then to swap hosts
# only last one counts
# basedir = "/Users/jeremyellman/Documents/Projects_Active/CM0645_15_16/"
# basedir = "/home/izje1/Documents/Projects_Active/CM0645/"
# basedir = "/home/jeremy/Projects-Active/CM0645/"
basedir = "/Users/mhmai/Desktop/UNN Masters/Year Two/Advanced Practice/Project Files/Source_Code/Latest_Code/CM0645/"

outdir = basedir + 'taggedtxts/'
BNCfile = "BNC.pickle"


# utility function from SO gives n sized chunks of list l
def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


class TaggedText:
    mybase = ""
    token_count = 0
    sentences = 0
    word_dict = {}
    novel_words = {}
    nonword = re.compile("[\d\.]");

    def __init__(self, mypath, Db):
        self.onlyfiles = [f for f in sorted(listdir(mypath)) if isfile(join(mypath, f))]
        self.mybase = mypath
        self.DB = Db
        self.ptag = re.compile('^[A-Z]+$')
        with open(basedir + "myAWLDict.txt", "rb") as myFile:  # load Academic Word List
            self.AWLDictionary = pickle.load(myFile)
        with open(basedir + "myCSAWLDict.txt", "rb") as myFile2:
            self.CSAWLstems = pickle.load(myFile2)
        self.stopWords = set(stopwords.words('english'))
        self.prepare_BNC()

    #       self.punkt_word_tokenizer = PunktWordTokenizer()
    # prepare the BNC by loading the Pickle of raw frequences then
    # group into kilo-words. There are 822 of these.
    def prepare_BNC(self):
        fn = join(basedir, BNCfile)
        print("BNC File: ", fn)

        BNCdict = pickle.load(open(fn, "rb"))
        self.BNC = BNCdict
        # Sort by Frequency
        BNC_bv = sorted(BNCdict.items(), key=lambda kv: kv[1])
        # find 1000 word chunks
        self.kilo_words = list(chunks(BNC_bv, 1000))
        n_kilo_words = len(self.kilo_words)
        total_word_count = sum(BNCdict.values())
        # now create dicts of the kilo_word lists for quick look up
        self.kdicts = [dict(l) for l in reversed(self.kilo_words)]
        print("BNC: Total Word:", total_word_count, " # 1000 Word groups: ", n_kilo_words)
        self.BNC_info(total_word_count)

    # Print frequency characteristics from the
    def BNC_info(self, total_word_count):
        counter = 0
        cumulative = 0
        max_cumulative = 90
        for subl in reversed(self.kilo_words):
            cnt = sum([x[1] for x in subl])
            prop = (cnt * 100.0) / total_word_count
            cumulative += prop
            print(counter, ") Raw(n): ", cnt, "Proportion(%): ", prop, " Cumulative(%): ", cumulative)
            counter += 1
            if cumulative > max_cumulative:  # otherwise get 823 lines of output
                break

    # Read the filename content into one variable self.content
    #
    def process_file(self, filename):
        fname = self.mybase + filename
        self.token_count = 0
        self.sentences = 0
        self.word_dict = {}
        self.novel_words = {}

        with open(fname, 'r', encoding='utf8') as f:
            content = f.read()
            self.sent_tokenize_list = sent_tokenize(content)  # split into sentences
            self.record_basic_stats(filename, self.sent_tokenize_list)

    # Create dictionary of Basic statistics from NLTK
    # then add these to the SQLite using addTextStats
    def record_basic_stats(self, filename, sent_tokenize_list):
        token_count = 0  # num tokens
        sent_count = 0  # numsentences
        word_dict = {}  # dict of words and their raw counts
        ourTSdict = {}  # details for this file
        for line in sent_tokenize_list:
            words = []
            {(words.extend(word.lower().translate(translator).split(' '))) \
             for word in word_tokenize(line) if word and not self.nonword.search(word)}
            # print("line: ", line, " words:", words)
            for word in words:
                if word:
                    token_count += 1
                    if word in word_dict:
                        word_dict[word] += 1
                    else:
                        word_dict[word] = 1
            token_count += len(words)
            sent_count += 1
        # self.show_tokens(word_dict)     # iof detail debug

        ourTSdict['NLTK_sentences'] = len(sent_tokenize_list)
        ourTSdict['NLTK_words'] = token_count
        ourTSdict['NLTK_vocab'] = len(word_dict)
        ourTSdict['NLTK_spread'] = len(word_dict) / token_count  ##
        self.word_dict = word_dict
        dictback = self.Calculate_AWL()
        #        ourTSdict['AWL_count'] = dictback['AWL_count']
        #        ourTSdict['CSAWL_count'] = dictback['CSAWL_count']
        #        print("NLTK Results:" , ourTSdict)
        ourTSdict.update(dictback)
        self.DB.addTextStats(filename, ourTSdict)  # takes dictionary of stats and file name
        print("File: %s, Sents: %d, words: %d, Vocabulary: %d\n" %
              (filename, sent_count, token_count, len(word_dict)))

    # check the word dict for details
    def show_tokens(self, word_dict):
        s = [(k, word_dict[k]) for k in sorted(word_dict, key=word_dict.get, reverse=True)]
        for key, val in s:
            print("Token:", key, "=>", val)
            if val == 1: break

    # This takes self.content and extracts from the Abstract to the References to the outfile whilst
    #         trying to lose none text lines like headers.
    #
    def process_content(self, filename, outfilename):
        with open(outfilename, 'w', encoding='utf8') as the_file:
            wr = csv.writer(the_file)
            self.process_PoS(filename, wr)

    def process_PoS(self, filename, writer):
        profile = {}
        for sent in self.sent_tokenize_list:
            tagged_sent = pos_tag(word_tokenize(sent))
            writer.writerow(tagged_sent)
            for (word, tag) in tagged_sent:
                tag = tag.replace('$', 'D', 1)  # don't want $ in tags names
                if self.ptag.match(tag):  # alphabetic tags only
                    mtag = "tag_" + tag  # issue here with some tags being python syntax
                    if mtag in profile:
                        profile[mtag] += 1
                    else:
                        profile[mtag] = 1
        #        print(profile)
        total = sum(profile.values())  # all the tagged tokens
        profile2 = {tag: value / total for (tag, value) in profile.items()}
        #        print(profile2)
        self.DB.addTextStats(filename, profile2)

    # Calculates AWL and BNC Membership
    def Calculate_AWL(self):
        AWLtotal = 0
        CSAWLtotal = 0
        rmax = 0
        dictback = {}
        k1 = 0  # first thousand
        k2 = 0
        k3 = 0
        k4 = 0  # 4th thousand BNC freq
        kn = 0  # otherwise in BNC
        kx = 0  # not in BNC at all
        max_possible = sum(self.word_dict.values())
        for word, count in self.word_dict.items():
            rmax += count
            #           if word not in self.stopWords:
            if word in self.kdicts[0]:
                k1 += count
            elif word in self.kdicts[1]:
                k2 += count
            elif word in self.kdicts[2]:
                k3 += count
            elif word in self.kdicts[3]:
                k4 += count
            elif word in self.BNC:
                kn += count
            else:
                kx += count
                if word in self.novel_words:
                    self.novel_words[word] += 1
                else:
                    self.novel_words[word] = 1
            # CSAWL and AWL
            if word in self.AWLDictionary:
                AWLtotal += count
            stem = stemmer.stem(word)
            if stem in self.CSAWLstems:
                CSAWLtotal += count
        # normalize AWL CSAWL by document length
        AWLresult = AWLtotal / rmax
        CSAWLresult = CSAWLtotal / rmax
        dictback['AWL_count'] = AWLresult
        dictback['CSAWL_count'] = CSAWLresult
        dictback['LFP_k1'] = k1 / rmax  # in first 1000 BNC Words
        dictback['LFP_k2'] = k2 / rmax  # in 2nd 1000 BNC Words
        dictback['LFP_k3'] = k3 / rmax  # in 3rd 1000 BNC Words
        dictback['LFP_k4'] = k4 / rmax  # in 4th 1000 BNC Words
        dictback['LFP_kn'] = kn / rmax  # not in first 4000 BNC Words, but in BNC
        dictback['LFP_kx'] = kx / rmax  # not in the BNC
        print("AWL: %d/%d: %4.3f" % (AWLtotal, rmax, AWLresult))
        print("CSAWL: %d/%d: %4.3f" % (CSAWLtotal, rmax, CSAWLresult))
        print("LFP: k1:%4.3f, k2:%4.3f,  k3:%4.3f k4: %4.3f, kn: %4.3f, kx: %4.3f" %
              (k1 * 100 / rmax, k2 * 100 / rmax, k3 * 100 / rmax, k4 * 100 / rmax, kn * 100 / rmax, kx * 100 / rmax))
        #        for key,val in self.novel_words.items():   # for debug
        #            print("Novel:", key, "=>", val)
        print("Novel Words: {0} \n".format(len(self.novel_words)))
        return (dictback)

    def process_Dir(self, outdir):
        for file in self.onlyfiles:
            try:
                if not self.DB.check_processed(file, 'NLTK_sentences'):  # expensive op --don't repeat if done
                    self.process_file(file)
                    self.process_content(file, outdir + file)
            except Exception as e:
                print("Token Tag: process_Dir: {} file: {}".format(e, file))

    def Describe(self):
        print(self.onlyfiles)


if __name__ == "__main__":
    dbfile = 'CM0645.sqlite'

    DB = Db(basedir + dbfile)
    JustOne = False  # False  #
    if JustOne:
        tagger0 = TaggedText(basedir + 'CM0645_Projects_16_17/' + 'ptxts/', DB)  # tag the extracted texts
        file1 = tagger0.onlyfiles[165]
        tagger0.process_file(file1)
        tagger0.process_content(file1, outdir + file1)
    else:
        tagger1 = TaggedText(basedir + 'CM0645_Projects_15_16/' + 'ptxts/', DB)  # tag the extracted texts
        tagger1.process_Dir(basedir + 'CM0645_Projects_15_16/' + 'taggedtxts/')
        tagger2 = TaggedText(basedir + 'CM0645_Projects_16_17/' + 'ptxts/', DB)  # tag the extracted texts
        tagger2.process_Dir(basedir + 'CM0645_Projects_16_17/' + 'taggedtxts/')
        tagger3 = TaggedText(basedir + 'CM0645_Projects_17_18/' + 'ptxts/', DB)  # tag the extracted texts
        tagger3.process_Dir(basedir + 'CM0645_Projects_17_18/' + 'taggedtxts/')
    # tagger1.Describe()

# content = [x.strip() for x in content]

