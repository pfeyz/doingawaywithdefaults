from time import time

def timefn(fun):
    """A decorator that wraps a function and causes it to print out its
    runtime when executed."""
    def wrapper(*args, **kwargs):
        start = time()
        val = fun(*args, **kwargs)
        print "{}({}, {}) took {}".format(fun.__name__,
                                          args, kwargs,
                                          time() - start)
        return val
    return wrapper

def cache_trigger(param):
    def wrapper(method):
        def wrapped(self, s):
            key = (param, s.sentenceStr)
            try:
                change_list = self.cache[key]
            except:
                change_list = method(self, s) or []
            for change in change_list:
                self.adjustweight(*change)
            self.cache[key] = change_list

        return wrapped
    return wrapper

class NDChild(object):
    def __init__ (self, learningrate, conslearningrate,language, cache):
        self.cache = cache
        print len(cache)
        self.grammar = {"lang":language,"SP": .5, "HIP": .5, "HCP": .5, "OPT": .5, "NS": .5, "NT": .5,"WHM": .5, "PI": .5, "TM": .5, "VtoI": .5, "ItoC": .5,"AH": .5, "QInv": .5}
        self.r = learningrate #simulation will pass child a learning rate
        self.conservativerate = conslearningrate

    def consumeSentence(self, s): #child is fed a list containing [lang, inflec, sentencestring]
        self.spEtrigger(s)    #parameter 1
        self.hipEtrigger(s)   #parameter 2
        self.hcpEtrigger(s)   #parameter 3
        #self.optEtrigger(s)   #parameter 4
        self.nsEtrigger(s)    #parameter 5
        self.ntEtrigger(s)    #parameter 6
        self.whmEtrigger(s)   #parameter 7
        self.piEtrigger(s)    #parameter 8
        self.tmEtrigger(s)    #parameter 9
        self.VtoIEtrigger(s)  #parameter 10
        self.ItoCEtrigger(s)  #parameter 11
        self.ahEtrigger(s)    #parameter 12
        self.QInvEtrigger(s)  #parameter 13

    #etriggers for parameters
    # first parameter Subject Position
    @cache_trigger('sp')
    def spEtrigger(self, s):
        # Check if O1 and S are in the sentence and sent is declarative
        if "O1" in s.sentenceList and "S" in s.sentenceList and s.inflection == "DEC":
            O1index = s.sentenceList.index("O1")
            Sindex = s.sentenceList.index("S") # Sindex is position of S in sentList
            # Make sure O1 is non-sentence-initial and before S
            if O1index > 0 and O1index < s.sentenceList.index("S"):
                # set towards Subject final
                return (("SP",1, self.r),)
            # S occurs before 01
            elif Sindex > 0 and O1index > s.sentenceList.index("S"): # S cannot be Sent initial
                # set towards Subject initial
                return (("SP",0,self.r),)

    # second parameter Head IP, VP, PP, etc
    @cache_trigger('hip')
    def hipEtrigger(self, s):
        if "O3" in s.sentenceList and "P" in s.sentenceList:
            O3index = s.sentenceList.index("O3")
            Pindex = s.sentenceList.index("P")
            # O3 followed by P and not topicalized
            if O3index > 0 and Pindex == O3index + 1:
                return (("HIP", 1, self.r),)
            elif O3index > 0 and Pindex == O3index - 1:
                return (("HIP", 0, self.r),)

        # If imperative, make sure Verb directly follows O1
        elif s.inflection == "IMP" and "O1" in s.sentenceList and "Verb" in s.sentenceList:
            if s.sentenceList.index("O1") == s.sentenceList.index("Verb") - 1:
                return (("HIP", 1, self.r),)
            elif s.sentenceList.index("Verb") == (s.sentenceList.index("O1") - 1):
                return (("HIP", 0, self.r),)

    # third parameter Head in CP
    @cache_trigger('hcp')
    def hcpEtrigger(self, s):
        if s.inflection == "Q":
            # ka or aux last in question
            if s.sentenceList[-1] == 'ka' or ("ka" not in s.sentenceList and s.sentenceList[-1] == "Aux"):
                return(("HCP", 1, self.r),)
            # ka or aux first in question
            elif s.sentenceList[0] == "ka" or ("ka" not in s.sentenceList and s.sentenceList[0]=="Aux"):
                return(("HCP", 0, self.r),)


    #fourth parameter Optional Topic (0 is obligatory,  1 is optional)
    def optEtrigger(self, s):
        if self.grammar["TM"] > 0.5 and "[+WA]" not in s.sentenceStr:
            self.adjustweight("OPT",1,self.r)



    @cache_trigger('ns')
    def nsEtrigger(self, s):
        if s.inflection == "DEC" and "S" not in s.sentenceStr and s.outOblique():
            return(("NS",1,self.r),)
        elif s.inflection == "DEC" and "S" in s.sentenceStr and s.outOblique():
           return(("NS",0,self.conservativerate),)

    @cache_trigger('nt')
    def ntEtrigger(self, s):
        if s.inflection == "DEC" and "O2" in s.sentenceStr and "O1" not in s.sentenceStr:
            return (
                ("NT",1,self.r),
                ("OPT", 0, self.r)
                )

        elif s.inflection == "DEC" and "O2" in s.sentenceStr and "O1" in s.sentenceStr and "O3" in s.sentenceStr and "S" in s.sentenceStr and "Adv" in s.sentenceStr:
            return(("NT",0,self.conservativerate),)
        #if all possible complements of VP are in sentence, then the sentence is not Null Topic

    @cache_trigger('whm')
    def whmEtrigger(self, s):
        if s.inflection == "Q" and "+WH" in s.sentenceStr:
            if ("+WH" in s.sentenceList[0]) or ("P" in s.sentenceList[0] and "O3[+WH]" == s.sentenceList[1]):
                return(("WHM",1,self.conservativerate),)
            else:
                return(("WHM",0,self.r),)

    @cache_trigger('pi')
    def piEtrigger(self, s):
        pIndex = s.indexString("P")
        O3Index = s.indexString("O3")
        if pIndex > -1 and O3Index > -1:
            if abs(pIndex - O3Index) > 1:
                return (("PI", 1, self.r), )

            elif ((pIndex + O3Index) == 1):
                return(("PI",0,self.conservativerate),)

    @cache_trigger('tm')
    def tmEtrigger(self, s):
        if "[+WA]" in s.sentenceStr:
            return(("TM",1,self.r),)
        elif "O1" in s.sentenceList and "O2" in s.sentenceList and (abs(s.sentenceList.index("O1")-s.sentenceList.index("O2")) > 1):
            return(("TM",0,self.r),)

    @cache_trigger('VtoI')
    def VtoIEtrigger(self, s):
        if "Verb" in s.sentenceStr and "O1" in s.sentenceStr:
            o1index = s.indexString("O1")
            if o1index != 0 and abs(s.indexString("Verb") - o1index) > 1:
                return (("VtoI", 1, self.r), ("AH", 0, self.r))

        #no need to explicitly check inflection because only Q and DEC have AUX
        elif "Aux" in s.sentenceList:
            return (("VtoI", 0, self.conservativerate),)


    def ItoCEtrigger(self, s):
        sp = self.grammar['SP']
        hip = self.grammar['HIP']
        hcp = self.grammar['HCP']


        if s.inflection == "DEC" and "S" in s.sentenceList and "Aux" in s.sentenceList:
            if sp < 0.5 and hip < 0.5: # (Word orders 1, 5) subject and IP initial, aux to the right of Subject
                Sindex = s.sentenceList.index("S")
                if Sindex > 0 and s.sentenceList.index("Aux") == Sindex + 1:
                    self.adjustweight("ItoC", 0, self.r)

            elif sp > 0.5 and hip > 0.5: # (Word orders 2, 6) #subject and IP final, aux to the left of subject
                AuxIndex = s.sentenceList.index("Aux")
                if (AuxIndex > 0 and s.sentenceList.index("S") == AuxIndex + 1):
                    self.adjustweight("ItoC", 0, self.r)

            elif sp > 0.5 and hip < 0.5 and hcp > 0.5 and "Verb" in s.sentenceList: #subject and C final, IP initial, Aux immediately follows verb
                if s.sentenceList.index("Verb") == s.sentenceList.index("Aux") + 1:
                    self.adjustweight("ItoC", 0, self.conservativerate)

            elif sp < 0.5 and hip > 0.5 and hcp < 0.5 and "Verb" in s.sentenceList: #subject and C initial, IP final, Aux immediately precedes verb
                if s.sentenceList.index("Aux") == s.sentenceList.index("Verb") + 1:
                    self.adjustweight("ItoC", 0, self.r)
                else:
                    self.adjustweight("ItoC", 1, self.conservativerate)
                    #will experiment with aggressive rate

            elif "Aux" in s.sentenceStr and "Verb" in s.sentenceList: #check if aux and verb in sentence and something comes between them
                Vindex = s.sentenceList.index("Verb")
                Auxindex = s.sentenceList.index("Aux")
                indexlist = [] #tokens that would shed light if between
                if "S" in s.sentenceList:
                    Sindex = s.sentenceList.index ("S")
                    indexlist.append(Sindex)

                if "O1" in s.sentenceList:
                    O1index = s.sentenceList.index ("O1")
                    indexlist.append(O1index)

                if "O2" in s.sentenceList:
                    O2index = s.sentenceList.index ("O2")
                    indexlist.append(O2index)

                if abs(Vindex - Auxindex) != 1: #if verb and aux not adjacent
                    for idx in indexlist:
                        if ( Vindex < idx < Auxindex ) or (Vindex > idx > Auxindex): #if item in index list between them
                            self.adjustweight("ItoC", 1, self.r) #set toward 1
                            break

    def ahEtrigger(self, s):
        if (s.inflection == "DEC" or s.inflection == "Q") and ("Aux" not in s.sentenceStr and "Never" in s.sentenceStr and "Verb" in s.sentenceStr and "O1" in s.sentenceStr):
            neverPos = s.indexString("Never")
            verbPos = s.indexString("Verb")
            O1Pos = s.indexString("O1")

            if (neverPos > -1 and verbPos == neverPos+1 and O1Pos == verbPos+1) or (O1Pos > -1 and verbPos == O1Pos+1 and neverPos == verbPos + 1):
                self.adjustweight("AH", 1, self.r)
                self.adjustweight("VtoI", 0, self.r)

        elif "Aux" in s.sentenceStr and self.grammar["AH"] <= 0.5:
            self.adjustweight ("AH",0,self.conservativerate)
            #if self.grammar["VtoI"] > 0.5: #If not affix hopping language, vtoi is either 0 or 1, but if evidence of vtoi towards 1 has alreadybeen observed, increase confidence 1VtoI given 0AH
            #   self.adjustweight("VtoI", 1, self.conservativerate)

    @cache_trigger('qinv')
    def QInvEtrigger(self, s):
        if s.inflection == "Q" and "ka" in s.sentenceStr:
            return(
                ("QInv", 0, self.r),
                ("ItoC",0, self.r)
                )

        elif s.inflection == "Q"and "ka" not in s.sentenceStr and "WH" not in s.sentenceStr:
            return(("QInv", 1, self.r),)



    def adjustweight(self, parameter, direction, rate):
        if direction == 0:
            self.grammar[parameter] -= rate*self.grammar[parameter]
        elif direction == 1:
            self.grammar[parameter] += rate*(1-self.grammar[parameter])
