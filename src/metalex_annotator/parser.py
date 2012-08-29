# -*- coding: utf-8 -*-
'''
Created on 8 Jun 2011

@author: hoekstra
'''

from nltk.tokenize.regexp import RegexpTokenizer
# from nltk.corpus import alpino
from nltk.tag import brill
from nltk.tag import RegexpTagger
from nltk.corpus import conll2002

import nltk
import pickle
import os.path

from types import StringType
import regex
from util import Util

class Parser():


    def __init__(self):
        if not os.path.isfile('tagger.pickle') :
            print "Training tagger..."
#            train_sents = alpino.tagged_sents()
            train_sents = conll2002.tagged_sents('ned.train')
#            train_sents = conll2002.chunked_sents('ned.train')
            
            word_patterns = [ (r'\d+\.\d+\w?', 'Ref'),
                             (r'\d+\:\d+\w?', 'Ref'),
                             (r'\d+\w', 'Ref'),  
                             (r'\d+/\d+/eg', 'Ref'),
                             (r'^(18|19|20)\d\d$', 'Year'),
                             (r'(de|het|een)', 'Art'),
                             (r'(en|of)', 'EnOf'),
                             (r'^\d+', 'Index'),
                             (r'^\w+\.$', 'Index'),
                             (r'^\d+(\D|\S|\W)(\.)?$', 'DegIndex'),
                             (r'^\w$', 'Ref'),
                             (r'^;$', 'Punc'),
                             (r'^[a-zA-Z]+\d+$','Ref'),
                             (r'^\w\w+$', 'N') ]
            
            raubt_tagger = self.backoff_tagger(train_sents, [nltk.tag.AffixTagger,
            nltk.tag.UnigramTagger, nltk.tag.BigramTagger, nltk.tag.TrigramTagger],
            backoff=RegexpTagger(word_patterns))
         
            templates = [
                brill.SymmetricProximateTokensTemplate(brill.ProximateTagsRule, (1,1)),
                brill.SymmetricProximateTokensTemplate(brill.ProximateTagsRule, (2,2)),
                brill.SymmetricProximateTokensTemplate(brill.ProximateTagsRule, (1,2)),
                brill.SymmetricProximateTokensTemplate(brill.ProximateTagsRule, (1,3)),
                brill.SymmetricProximateTokensTemplate(brill.ProximateWordsRule, (1,1)),
                brill.SymmetricProximateTokensTemplate(brill.ProximateWordsRule, (2,2)),
                brill.SymmetricProximateTokensTemplate(brill.ProximateWordsRule, (1,2)),
                brill.SymmetricProximateTokensTemplate(brill.ProximateWordsRule, (1,3)),
                brill.ProximateTokensTemplate(brill.ProximateTagsRule, (-1, -1), (1,1)),
                brill.ProximateTokensTemplate(brill.ProximateWordsRule, (-1, -1), (1,1))
            ]
             
            trainer = brill.FastBrillTaggerTrainer(raubt_tagger, templates)
            braubt_tagger = trainer.train(train_sents, max_rules=100, min_score=3)
            
            self.trained_tagger = braubt_tagger
            
            pickle.dump(self.trained_tagger, open('tagger.pickle','w'))
            print "Dumped tagger to file"
        else :
            self.trained_tagger = pickle.load(open('tagger.pickle', 'r'))
            print "Loaded tagger from file"
            
            

        
    def backoff_tagger(self, tagged_sents, tagger_classes, backoff=None):
        if not backoff:
            backoff = tagger_classes[0](tagged_sents)
            del tagger_classes[0]
     
        for cls in tagger_classes:
            tagger = cls(tagged_sents, backoff=backoff)
            backoff = tagger
     
        return backoff

    def tokenizeText(self, text):
        ret = RegexpTokenizer(u"(\d+\u00B0(\.)?)|(nr\.)|(\d+/\d+/eg)|(\d+\:\d+\w*)|(\d+\.\d+\w*)+|[\w\d]+|(\s\w\.)|(\.)|\,|\t|[^ \t\n\r\f\v\w\d]")
        tokens = ret.tokenize(text)
        
        ntokens = []
        sentence = []
        i = -1
        for t in tokens[:-1] :
            i += 1
            if type(t) is StringType:
                t = t.decode('UTF-8')

                
            if (t.istitle() and tokens[i-1] == '.') or (regex.search(r'^\d+',t) and tokens[i+1].istitle()):
                ntokens.append(sentence)
                sentence = [t.lower().strip()]
            else :
                sentence.append(t.lower().strip())
        
        sentence.append(tokens[-1].lower().strip())
        ntokens.append(sentence)
        
        return ntokens

    def tagText(self, ntokens):
        ntagged = []
        if len(ntokens) > 1:
            sentences = ntokens[1:]
        else :
            sentences = ntokens
            
        for s in sentences :
            tagged = self.trained_tagger.tag(s)
            normalized_tagged = []
            for (w,t) in tagged :
                if t == None : 
                    t = 'none'
                if regex.search(r'^[a-zA-Z]$',w) :
#                    print "Replaced", w
                    normalized_tagged.append((w,u'Ref'))
                elif regex.search(r'^[a-zA-Z]\.$',w) :
#                    print "Replaced", w
                    normalized_tagged.append((w,u'Index'))
                elif regex.search(r'\d+\u00B0(\.)?',w) :
                    normalized_tagged.append((w,u'DegIndex'))
                elif regex.search(r'\(|\)',w) :
                    normalized_tagged.append((w,u'Bracket'))
                elif regex.search(r'(18|19|20)\d\d',w) :
                    normalized_tagged.append((w,u'Year'))
                elif regex.search(r'^\d+$',w) :
                    normalized_tagged.append((w,u'Ref'))
                elif regex.search(r'^�$',w) :
                    print "Removed", w
#                    ns.append((w,u'Index'))
                elif regex.search(r'^\-$', w) :
                    normalized_tagged.append((w,u'Koppel'))
                elif regex.search(r'^het$', w) :
                    normalized_tagged.append((w,u'Art'))
                elif regex.search(r'^(en|of|onderscheidenlijk)$', w) :
                    normalized_tagged.append((w,u'EnOf'))
                elif regex.search(r'^ten$', w) :
                    normalized_tagged.append((w,u'Ten'))
                elif regex.search(r'^van$', w) :
                    normalized_tagged.append((w,u'Van'))
                elif regex.search(r'^der$', w) :
                    normalized_tagged.append((w,u'Prep'))
                elif regex.search(r'^nr.$', w) :
                    normalized_tagged.append((w,u'N'))   
                # 'laste' and 'koste' are nouns, but shouldn't be treated as such, cf. 'ten laste van' is not a NP
                elif regex.search(r'^laste|koste|aanmerking|tijde|aanzien|voorzover$', w) :
                    normalized_tagged.append((w,u'None'))
                elif regex.search(r'^krachtens$', w) :
                    normalized_tagged.append((w,u'Krachtens'))
                elif regex.search(r'^aanspraken|liquidatiewaarde|persoonsgegevens|waardegegeven|ouder|verkregene|nabestaande|nabestaanden|eigenwoningschuld|overledene|nederlanden|begiftigden|begiftigde|erfgenamen|overledene|vermogensbestanddelen|goed|verkregene|rechtspersoon|mogendheden|schenker|verkrijger|registergoederen|bewijsstukken|overbedelingsschuld|geldsom|huwelijksvoorwaarden|eerststervende$', w) :
                    normalized_tagged.append((w,u'N'))
                elif regex.search(r'^ingesloten|uitgaat|aansluit|vervreemdt$', w) :
                    normalized_tagged.append((w,u'V'))
                elif regex.search(r'^ingeval|door$', w) :
                    normalized_tagged.append((w,u'Conj'))
                elif regex.search(r'^één$', w) :
                    normalized_tagged.append((w,u'Num'))
                elif regex.search(r'^waaromtrent$', w) :
                    normalized_tagged.append((w,u'Adv'))
                elif regex.search(r'^indirect$', w) :
                    normalized_tagged.append((w,u'Adj'))
                elif regex.search(r'^(wet|wetten|artikel|artikelen|hoofdstuk|hoofdstukken|boek|boeken|titeldeel|titeldelen|lid|titel|afdeling|onderdeel|volzin)$', w) :
                    normalized_tagged.append((w,u'Part'))
                else :
                    normalized_tagged.append((w,t))
            
            ntagged.append(normalized_tagged)
           
        return ntagged

    def parseText(self, ntagged):
    
        # Deze drie de gele bloemen 
        # Alle drie deze artikelen 12

#        standard_NP = "((<Art><Num>?<Adv>))?<Adj>*<V>*<N>+(<Adj>+<N>+)?(<Ref>|<Year>)?"


#        standard_NP = "(<Art>|<Pron>(<Num><Art>|<Pron>)?)?<Adv>?<Adj>*<V>*(<Conj><V>*<Adj>*?)*(<N>|<none>)+(<Ref>|<Year>)?"

#        prep_adj_V = "(<Prep><Adj>*<V><N>)"
#        prep_V_connector = "((<V><Prep>?)|<Prep>)"

#        grammar = r"NP: { ("+standard_NP + "((<Prep><Adj>*<V><N>)| ((<Pron><Prep><V><N>) | (<Pron><Prep><N><V><V>)))?)|(<Art><V><N>?)|(<N><Prep><N>) }\n REF: { <Num><N> }" # |(" + prep_V_connector + standard_NP + "))* }"
        
        grammar = """
        NREF: { (<Part><Ref|Index|DegIndex>((<Punc><Ref|Index|DegIndex>(<Punc><Num><Part>)?)|(<EnOf><Ref>(<Punc><Num><Part>)?))*)|(<Num><Part>) }
        AV:  { (<Art><Adj>*<V>((<Punc><Adj>*<V>)*<EnOf><Adj>*<V>)*<N>?) }
        AN: { (<Adj>(<Punc|EnOf><Adj>)*)?<N|Part> } 
        AP:  { <AN>(<AN>*(?!<Prep>?<V><Punc>))?<Ref|Year>? }
        MAP: { (<Art><Pron>?<AP>) }
        SAP: { <MAP|AV>(<Koppel>?<EnOf><AP|MAP|AV>)* }
        SP:  { <AP|AV>(<Koppel>?<EnOf><AP|AV>)* } 
        REF: {<NREF>(<Van><NREF>)*(<Van><SAP>)?}
        NP:  { <SAP|SP>((<Ten><SP><Van><SAP|SP>)|(<Krachtens><SAP|SP><Van><SAP|SP>)|(<Prep|Krachtens><SP>(?!<Adv>))|(<Van><Pron>?<SP|SAP|V>(<Prep|Krachtens><SP>)?))*(<Conj><V>(?!<Prep|EnOf|Art|Pron|V>))? }
        """
        
        
        cp = nltk.RegexpParser(grammar)
        # Alpino style
        # cp = nltk.RegexpParser("NP: {<det><num>*<prep>*<adj>*(<noun>|<none>)+<num>*}")
        
        nparsed = []
        for s in ntagged :
            ps = cp.parse(s)
            nparsed.append(ps)
            
        return nparsed




    


    

                





        