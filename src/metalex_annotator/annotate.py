# -*- coding: utf-8 -*-

from cornetto.linker import ConceptLinker
from definition.matcher import DefinitionMatcher
from util import Util
from parser import Parser
from sys import stdout
import math

class Annotator():

    counter = 0

    def __init__(self):
        self.parser = Parser()
        self.np_tf = {}
        self.np_itf = {}
        self.tfidf = {}
        self.definitions = []
        
        
 

    def indexConcepts(self, id, nps):
        if not id in self.np_tf.keys() :
            self.np_tf[id] = {}       
        
        for entry in nps :
            nouns = entry['nouns']
            concept = entry['concept']
            
            nouns.append(concept)
            for np in nouns :
                if np in self.np_tf[id].keys() :
                    self.np_tf[id][np] += 1
                else :
                    self.np_tf[id][np] = 1
                    
                if not np in self.np_itf.keys():
                    self.np_itf[np] = {}
                   
                if id in self.np_itf[np].keys():
                    self.np_itf[np][id] += 1
                else :
                    self.np_itf[np][id] = 1 
                
    def scoreConcepts(self):
        # Get the total number of documents
        doc_count = len(self.np_tf.keys())
        
        self.tfidf['count'] = doc_count
        self.tfidf['nps'] = {}
        self.tfidf['docs'] = {}
        # For every noun phrase in the inverse term frequency dictionary
        for np in self.np_itf :
            # Get the total number of documents (articles) in which this noun phrase occurs 
            np_total_doc_count = len(self.np_itf[np].keys())
            
            # Calculate the inverse document frequency (IDF) as the natural logarithm of the total 
            # number of documents divided by the number of documents containing this noun phrase
            idf = math.log(float(doc_count)/float(np_total_doc_count))
            print np,idf
            
            # Initialise the TFIDF for this noun phrase
            self.tfidf['nps'][np] = {}
            
            # For every document in which this noun phrase occurs
            for doc_id in self.np_itf[np] :
                # Initialise the TFIDF per noun phrase for this document
                self.tfidf['nps'][np][doc_id] = {}
                
                # Initialise the TFIDF per document
                if not doc_id in self.tfidf['docs'].keys() :
                    self.tfidf['docs'][doc_id] = {}
                
                # Initialise the TFIDF per document for this noun phrase
                self.tfidf['docs'][doc_id][np] = {}
                
                # Get the number of times this noun phrase occurs in the document
                np_occ_count = self.np_itf[np][doc_id]
                
                # Get the count for the noun phrase that occurs the most in this document.
                max_np_count = 0
                for onp in self.np_tf[doc_id] :
                    if self.np_tf[doc_id][onp] > max_np_count :
                        max_np_count = self.np_tf[doc_id][onp]
                

                # Calculate the normalized term frequency as the number of times the noun phrase occurs, divided by the maximum 
                # number of times any noun phrase occurs in this document
                tf = float(np_occ_count) / float(max_np_count)
                
                # Calculate TFIDF
                tfidf = tf*idf

                self.tfidf['nps'][np][doc_id]['tc'] = np_occ_count
                self.tfidf['nps'][np][doc_id]['tf'] = tf
                self.tfidf['nps'][np][doc_id]['idf'] = idf
                self.tfidf['nps'][np][doc_id]['max'] = max_np_count
                self.tfidf['nps'][np][doc_id]['tfidf'] = tfidf
                self.tfidf['nps'][np][doc_id]['dc'] = doc_count
                self.tfidf['nps'][np][doc_id]['ndc'] = np_total_doc_count
                
                self.tfidf['docs'][doc_id][np]['tc'] = np_occ_count
                self.tfidf['docs'][doc_id][np]['tf'] = tf
                self.tfidf['docs'][doc_id][np]['idf'] = idf
                self.tfidf['docs'][doc_id][np]['max'] = max_np_count
                self.tfidf['docs'][doc_id][np]['tfidf'] = tfidf          
                self.tfidf['docs'][doc_id][np]['dc'] = doc_count
                self.tfidf['docs'][doc_id][np]['ndc'] = np_total_doc_count 
                
    def getConcepts(self, definitions):
        concepts = []
        for (id, num, scope, term, mod, definition, stext) in definitions :
            concepts.append(term)
        
        return concepts
                
    def annotate(self, id, text):
        print "== Annotating {} ==".format(id)
        print "Tokenizing..."
        tokenized = self.parser.tokenizeText(text)
        print "Tagging..."
        tagged = self.parser.tagText(tokenized)
        print "Parsing..."
        parsed = self.parser.parseText(tagged)
        
        stdout.write("Scanning for definitions...")
        dm = DefinitionMatcher()
        definitions_for_id = dm.match(id, tagged)
        stdout.write(" {} found.\n".format(len(definitions_for_id)))
        self.definitions.extend(definitions_for_id)
            
        stdout.write("Extracting concepts...")
        concepts = Util.extractConcepts(parsed)
        stdout.write(" {} found.\n".format(len(concepts)))
        
#        NB: This does not currently work, as the concepts from definitions should be in a dictionary      
#        stdout.write("Appending concepts from definitions to concept list...")
#        concepts.extend(self.getConcepts(self.definitions))
#        stdout.write(" {} total.\n".format(len(definitions_for_id)))

        if len(concepts) < 1 :
            print "No concepts found..."
        else :
            print "Adding concepts to index..."
            self.indexConcepts(id, concepts)
#            print "Linking concepts to Cornetto Wordnet..."
#            cl = ConceptLinker()
#            cl.link(id, concepts)

        print "=== NEXT ===\n\n"
        return definitions_for_id





if __name__ == '__main__' :
    a = Annotator()
    print "Initialised"
    raw = u"""De bezittingen en de schulden van een afgezonderd particulier vermogen als bedoeld in artikel 2.14a, tweede lid, van de Wet inkomstenbelasting 2001, die tot het overlijden van een erflater ingevolge dat artikel zijn toegerekend aan die erflater, en met ingang van zijn overlijden aan zijn erfgenamen, worden voor de toepassing van deze wet en de daarop berustende bepalingen geacht door die erfgenamen krachtens erfrecht te zijn verkregen en wel per erfgenaam voor het deel dat ingevolge dat artikel aan de erfgenaam wordt toegerekend. De eerste volzin is van overeenkomstige toepassing met betrekking tot bezittingen en schulden als bedoeld in artikel 2.14a, zevende lid, van de Wet inkomstenbelasting 2001 die zonder toepassing van dat lid tot het overlijden van de erflater zouden zijn toegerekend aan die erflater, en met ingang van zijn overlijden aan zijn erfgenamen. Onder hetgeen krachtens erfrecht wordt verkregen, wordt voor de toepassing van deze wet en de daarop berustende bepalingen mede verstaan het ten gevolge van het overlijden van een erflater verkrijgen van een in rechte vorderbare aanspraak op een afgezonderd particulier vermogen als bedoeld in artikel 2.14a van de Wet inkomstenbelasting 2001.Bij ministeriele regeling kunnen regels worden gesteld ter zake van de in dit artikel bedoelde verkrijging. Al wat wordt verkregen van een afgezonderd particulier vermogen als bedoeld in artikel 2.14a, tweede lid, van de Wet inkomstenbelasting 2001, op andere wijze dan bedoeld in artikel 16, wordt voor de toepassing van deze wet en de daarop berustende bepalingen, geacht door schenking te zijn verkregen van de persoon of personen waaraan de bezittingen en schulden van het afgezonderd particulier vermogen ingevolge artikel 2.14a van de Wet inkomstenbelasting 2001 worden toegerekend. De eerste volzin is van overeenkomstige toepassing met betrekking tot al wat wordt verkregen, op andere wijze dan bedoeld in artikel 16, ten laste van bezittingen als bedoeld in artikel 2.14a, zevende lid, van de Wet inkomstenbelasting 2001, met dien verstande dat in dat geval wordt geacht te zijn verkregen van de persoon of personen waaraan die bezittingen zonder toepassing van dat lid zouden zijn toegerekend. Onder vruchtgebruik worden, voor de toepassing van deze wet, mede verstaan vruchtgenot, gebruik en bewoning, vruchten en inkomsten, jaarlijkse opbrengst en soortgelijke uitkeringen uit daartoe aangewezen goederen. Onder periodieke uitkering wordt, voor de toepassing van deze wet, behalve de uitkering in geld, mede verstaan elke andere, voortdurende, of op vastgestelde tijdstippen terugkerende, prestatie. Als pleegkinderen worden aangemerkt zij, die voor het tijdstip waarop zij de leeftijd van 21 jaar hebben bereikt dan wel het tijdstip waarop zij voor die leeftijd in het huwelijk zijn getreden, gedurende ten minste vijf jaren uitsluitend door de pleegouder - dan wel uitsluitend door hem en zijn echtgenoot tezamen - als een eigen kind zijn onderhouden en opgevoed."""

    a.process('http://foo.bar/test',raw)
    
    print ConceptLinker.serialize()

