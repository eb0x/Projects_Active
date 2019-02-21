# This script checks that your Python installation will run the examples that
# will be used in the lab classes. You can install other modules, but not usually in
# the university labs. 

import unittest
import importlib
import warnings

def libcheck(lib):
    '''lib is a library name as a string. If it is imported then a
    module object is returned. If not 0. A library will not be imported if
    not installed'''
    i = 0
    try:
        i = importlib.import_module(lib)
        print('Loaded: ', lib)
    except ImportError:
        print("The library: ", lib, " could not be loaded")
    return i

## This is a unittest class. Running this checks your installation
##
class CM0645Test(unittest.TestCase):

    def setUp(self):
        pass

    def test_DB_check(self):
        '''checks DB requirements'''
        warnings.simplefilter('ignore', category=ImportWarning)
        res = libcheck('os')
        res1 = libcheck('sqlite3')
        self.assertTrue(res)
        self.assertTrue(res1)

    def test_Data_Prep_check(self):
        warnings.simplefilter('ignore', category=ImportWarning)
        res = libcheck('numpy')
        res2 = libcheck('operator')
        res3 = libcheck('matplotlib')
        res4 = libcheck('pandas')
        res5 = libcheck('re')
        self.assertTrue(res)
        self.assertTrue(res2)
        self.assertTrue(res3)
        self.assertTrue(res4)
        self.assertTrue(res5)


    def test_csawl_check(self):
        warnings.simplefilter('ignore', category=ImportWarning)
        res = libcheck('nltk')
        res2 = libcheck('pickle')
        msg = ""
        try:
            from nltk.stem.snowball import SnowballStemmer
            msg = msg + "\nLoaded SnowballStemmer"
            print(msg)
        except:
            print(msg)
            print("The supporting data: could not be loaded")
        self.assertTrue(res)
        self.assertTrue(res2)

    def test_Token_Tag_check(self):
        warnings.simplefilter('ignore', category=ImportWarning)
        res = 0
        msg = ""
        libcheck('pickle')
        libcheck('csv')
        libcheck('os')
        libcheck('spacy')
        libcheck('nltk')
        libcheck('nltk.data')
        libcheck('nltk.tokenize')
        libcheck('nltk.tag')
        libcheck('nltk.corpus')
        try:
            from nltk.stem.snowball import SnowballStemmer
            from nltk.tokenize import sent_tokenize,  word_tokenize, TreebankWordTokenizer
            msg = msg + "\nLoaded SnowballStemmer"
            msg = msg + "sent_tokenize,  word_tokenize, TreebankWordTokenizer"
            print(msg)
        except:
            print(msg)
            print("The supporting data: could not be loaded")


#Code in this block is executed when this file is loaded as the main file
# but not when the module is imported

if __name__ == '__main__':
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', category=ImportWarning)
            unittest.main()
    except SystemExit as inst:
        if inst.args[0] is True: # raised by sys.exit(True) when tests failed
            raise
