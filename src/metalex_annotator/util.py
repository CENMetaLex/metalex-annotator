# -*- coding: utf-8 -*-
'''
Created on 8 Jun 2011

@author: hoekstra
'''
import re

class Util:

    @classmethod
    def flattenNP(cls, subtree, strip = False):
        n = ""
        nouns = []
        (w,t) = subtree.leaves()[0]
        # If strip=True, strip articles and pronouns from the start of the noun phrase (no differation between de, het and een)
        if (t != 'Art' and t != 'Pron') or not(strip) :
            n += cls.flattenLeaf((w,t), strip)
        for node in subtree.leaves()[1:] :
            n += cls.flattenLeaf(node, strip)
        

        
        for (w,t) in subtree.leaves() :
            if t == 'N' and w != n.lstrip():
                nouns.append(w)
            
            
        return n.lstrip(), nouns
    
    @classmethod
    def flattenLeaf(cls, node, strip = False):
        (w,t) = node
        if strip :
            return " " + w
        else :
            return " " + w + "/" + t
    
    @classmethod    
    def extractConcepts(cls, parsed_text):
        concepts = []
        for token in parsed_text :    
            for subtree in token.subtrees(filter=lambda t: t.node == 'NP') :
                
                concept, concept_nouns = Util.flattenNP(subtree, strip = True)
                if len(concept) > 1 :
                    concepts.append({'concept': concept, 'nouns': concept_nouns })
                    
                
        
#        print concepts
        return concepts
    
