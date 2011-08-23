# -*- coding: utf-8 -*-
'''
Created on 8 Jun 2011

@author: hoekstra
'''

from SPARQLWrapper import SPARQLWrapper, XML
from rdflib import ConjunctiveGraph, Namespace, Literal, RDF, RDFS, URIRef
from string import Template
import urllib
import sys

class ConceptLinker:
    '''
    Links noun phrases to concepts in Cornetto Wordnet
    '''
    
    direct_match_query = Template("""SELECT ?c WHERE {
   ?c <http://purl.org/vocabularies/cornetto/synonym> ?l .
   FILTER( str(?l) = \"$term\" )
}""")

    

    DCTERMS = Namespace('http://purl.org/dc/terms/')
    SKOS = Namespace('http://www.w3.org/2004/02/skos/core#')
    WN = Namespace('http://purl.org/vocabularies/cornetto/')
    MC = Namespace('http://doc.metalex.eu/id/concept/')


    target_scheme = MC['metalex_vocabulary']
    
    graph = ConjunctiveGraph()
    
    visited = []

    def __init__(self, sparql_endpoint = "http://localhost:3020/sparql/"):
        self.sparql = SPARQLWrapper(sparql_endpoint)
        
        # Bind namespaces to graph
        self.graph.namespace_manager.bind('dcterms',self.DCTERMS)
        self.graph.namespace_manager.bind('skos',self.SKOS)
        self.graph.namespace_manager.bind('wn',self.WN)
        self.graph.namespace_manager.bind('mc',self.MC)
        
        self.graph.add((URIRef(self.target_scheme), RDF.type, self.SKOS['ConceptScheme']))
        self.graph.add((self.MC['Concept'], RDF.type, RDFS.Class))
        self.graph.add((self.MC['Concept'], RDFS.subClassOf , self.SKOS['Concept']))
        self.graph.add((self.MC['Term'], RDF.type, RDFS.Class))
        self.graph.add((self.MC['Term'], RDFS.subClassOf , self.SKOS['Concept']))
        
        self.graph.add((self.MC['cooccursWith'], RDF.type, RDF.Property))
        self.graph.add((self.MC['cooccursWith'], RDFS.subPropertyOf, self.SKOS['related']))
        
        
    def findMatches(self, term, term_uri, nouns):
        print "Finding close matches for '{}' ({})".format(term, term_uri)


        
        self.graph.commit()
        
        uris = self.match(term)
        self.addMatches(term_uri, self.SKOS['closeMatch'], uris)
        self.graph.commit()

        if len(nouns) > 1 :
            print "Finding broader matches for '{}' ({})".format(term, term_uri)
            for t in nouns :
                try:
                    try :
                        t_uri = self.mintURI(t)
                    except Exception as e:
                        print "Error in minting URI for noun {}: {}".format(term, e)
                        break
                    
                    self.graph.add((term_uri, self.SKOS['broader'], t_uri))
                    
                    if not(t in self.visited) :
                        t = t.encode('utf-8')
                        print "Finding close matches for '{}' ({})".format(t, t_uri)
                        self.graph.add((t_uri, self.SKOS['prefLabel'], Literal(t)))
                        self.graph.add((t_uri, RDF.type, self.MC['Term']))
                        self.graph.add((t_uri, self.SKOS['inScheme'], URIRef(self.target_scheme)))     
                        
                        self.graph.commit()
                                           
                        uris = self.match(t)
                        self.addMatches(t_uri, self.SKOS['closeMatch'], uris)
                        self.addMatches(term_uri, self.SKOS['relatedMatch'], uris)
                        
                        self.graph.commit()
                except Exception as e :
                    print "Problem in adding matches for noun {}".format(t)
                    

        print "No additional nouns identified in '{}'".format(term)  
  
    def match(self, term):
        self.visited.append(term)
        q = self.direct_match_query.substitute(term=term)
        
        self.sparql.setQuery(q)
        self.sparql.setReturnFormat(XML)
        try :
            sparql_results = self.sparql.query()
        except Exception as (errno, strerror) :
            print "Error ({0}): {1}".format(errno, strerror)
            raise           
        
        uri_elements = sparql_results.convert().getElementsByTagName("uri") 
        uris = []
        
        for uri_element in uri_elements :
            for child in uri_element.childNodes :
                uris.append(child.nodeValue)
                
        return uris

    
    def mintURI(self, term):
        term_underscored = term.replace(' ','_')
        term_encoded = urllib.quote(term_underscored)
        return self.MC[term_encoded]

            

    def addMatches(self, concept_uri, match_type, matched_uris):
        for m_uri in matched_uris :
            self.graph.add((URIRef(concept_uri),match_type,URIRef(m_uri)))
    
    def link(self, metalex_id, nps):
        print "\n\nMetaLex Element URI: {}".format(metalex_id)
        for np in nps :
            term = np['concept'].encode('utf-8')
            if term != '':
                try :
                    
                    try :
                        term_uri = self.mintURI(term)
                    except Exception as e:
                        print "Error in minting URI for concept {}: {}".format(np['concept'], e)
                        break
                        
                    # Add a dcterms:subject relation between Metalex identifier and noun phrase
                    self.graph.add((URIRef(metalex_id), self.DCTERMS['subject'], term_uri))
                    self.graph.add((term_uri, self.SKOS['prefLabel'], Literal(term)))
                    self.graph.add((term_uri, RDF.type, self.MC['Concept']))
                    self.graph.add((term_uri, self.SKOS['inScheme'], URIRef(self.target_scheme)))
                    self.graph.add((URIRef(metalex_id), RDF.type, self.SKOS['Collection']))
                    self.graph.add((URIRef(metalex_id), self.SKOS['member'], term_uri))
                    
                    self.graph.commit()
                    
                    for other_np in nps :
                        if other_np['concept'].encode('utf-8') != '' and term != other_np['concept'].encode('utf-8') :
                            other_np_uri = self.mintURI(other_np['concept'].encode('utf-8'))
    #                            print "{} cooccurs with {}".format(term_uri, other_np_uri)
                            self.graph.add((term_uri, self.MC['cooccursWith'], URIRef(other_np_uri)))
                    
                    self.graph.commit()
                    
                    # If the noun phrase has not yet been encountered before, try to match it to Cornetto concepts
                    if not(term in self.visited):
                        self.findMatches(term, term_uri, np['nouns'])
                        self.graph.commit()
                except Exception as e :
                    print "Problem in adding matches for concept {}: {}".format(term, e)

        
        self.graph.commit()
                    
                    
    def serialize(self, destination=None):
        return self.graph.serialize(destination, format='turtle')
