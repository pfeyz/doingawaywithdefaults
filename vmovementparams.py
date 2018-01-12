    def ItoCEtrigger(self, s):
        sp = self.grammar['SP']
        hip = self.grammar['HIP']
        hcp = self.grammar['HCP']
        
        if s.inflection == "DEC":
            if sp < 0.5 and hip < 0.5: # (Word orders 1, 5) subject and IP initial, aux to the right of Subject
                Sindex = s.sentenceList.index("S")
                if Sindex > 0 and s.sentenceList.index("Aux") == Sindex + 1:
                    self.adjustweight("ItoC", 0, self.r)
        
            elif sp > 0.5 and hip > 0.5: # (Word orders 2, 6) #subject and IP final, aux to the left of subject
                AuxIndex = s.sentenceList.index("Aux")
                if (AuxIndex > 0 and s.sentenceList.index("S") == AuxIndex + 1):
                    self.adjustweight("ItoC", 0, self.r)
           
            elif sp > 0.5 and hip < 0.5 and hcp > 0.5: #subject and C final, IP initial, Aux immediately follows verb
                if s.sentenceList.index("Verb") == s.sentenceList.index("Aux") + 1:
                    self.adjustweight("ItoC", 0, self.conservativerate)

            elif sp < 0.5 and hip > 0.5 and hcp < 0.5: #subject and C initial, IP final, Aux immediately precedes verb
                if s.sentenceList.index("Aux") == s.sentenceList.index("Verb") + 1:
                    self.adjustweight("ItoC", 0, self.conservativerate)
  
            elif "Aux" in s.sentence and "V" in s.sentence:
                Vindex = s.sentenceList.index("V")
                Auxindex = s.sentenceList.index("Aux")
                Sindex = s.sentenceList.index ("S")
                O1index = s.sentenceList.index ("O1")
                O2index = s.sentenceList.index ("O2")
                
                indexlist = [Sindex, O1index, O2index]
                
                if abs(Vindex - Auxindex) != 1:
                    for idx in indexlist:
                        if ( Vindex < idx < Auxindex ) or (Vindex > idx > Auxindex):
                            self.adjustweight("ItoC", 1, self.r)
                            break
                            
                      
    def QInvEtrigger(self, s):
        if s.inflection == "Q" and "ka" in s.sentenceStr:
            self.adjustweight("QInv", 0, self.r)
            
        elif s.inflection == "Q"and "ka" not in s.sentenceStr and "WH" not in s.sentenceStr:
            self.adjustweight("QInv", 1, self.r)
     
                            
                    
                 
