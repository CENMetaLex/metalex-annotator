# -*- coding: utf-8 -*-
'''
Created on 27 Apr 2011

@author: hoekstra
'''

from annotate import Annotator
import csv
from cornetto.linker import ConceptLinker
from definition.matcher import DefinitionMatcher
from string import Template
import pickle
import sys
import regex
import locale
from util import Util
from nltk.tree import Tree
import argparse
import os



def prettify_id(id):
    docid = regex.sub(r'/id/','/doc/',regex.sub('$','/data.xml',id))
    
    bwb = regex.search('BWB(?P<bwb>\w+?)/',id).group('bwb')
    docstring = 'BWB{} : '.format(bwb)
    for m in regex.finditer(r'/(?P<part>(hoofdstuk|artikel|paragraaf|sectie|lid|onderdeel|afdeling)?)/(?P<index>([ivclmxIVCLMX0-9\:\.\-\s]+([a-z]+)?))',id) :
        docstring = docstring + "{} {}, ".format(m.group('part').capitalize(),m.group('index')) 
    
    docstring = docstring.rstrip(', ')
    return docid, docstring

def write_definition_report(indexed_definitions, definitions, outprefix):
    fn = "{}_definitions.csv".format(outprefix)
    fn_html = "{}_definitions.html".format(outprefix)
    def_writer = csv.writer(open(fn, 'wb'), delimiter=';')
    def_writer.writerow(['ID','Type','Scope','Concept','Modifier', 'Def','Context'])
    
    print "Writing to {}".format(fn)
    for d in definitions :
        (id, type, scope, concept, modifier, definition, context) = d
        def_writer.writerow([id.encode('UTF-8'),type.encode('UTF-8'),scope.encode('UTF-8'),concept.encode('UTF-8'),modifier.encode('UTF-8'),definition.encode('UTF-8'),context.encode('UTF-8')])
    print "Done"
    
    
    t = Template("""
    <h2>$concept</h2>
    <div class="ui-widget">
        <div class="ui-widget-header">Definitie</div>
        <div class="ui-widget-content"><p>$definition_text</p></div>
        <div class="ui-widget-header">Scope</div>
        <div class="ui-widget-content"><p>$scope</p></div>
        <div class="ui-widget-header">Vindplaats</div>
        <div class="ui-widget-content" style="text-align: middle;"><p><img src="img/link.png">&nbsp;&nbsp;<a href="$docid">$docstring</a></p></div>
    </div>
    <div class="accordion">
        <h3><a href="#">Context</a></h3><div><p>$context_clean</span></p></div>
        <h3><a href="#">Details</a></h3><div>
            <p><table>
                <tr><th>Definition type</th><td>$type</td></tr>
                <tr><th>Regular expression</th><td>$regex</td></tr>
                <tr><th>Tagged context</th><td>$context</td></tr>
            </table></p>
        </div>
    </div>""")

    print "Writing to {}".format(fn_html)
    f = open(fn_html,"w")
    f.write("""<html>
        <head>
            <title>Definities</title>
            <link type="text/css" rel="stylesheet" media="all" href="css/ui-lightness/jquery-ui-1.8.14.custom.css" />
            <link type="text/css" rel="stylesheet" media="all" href="css/definitions.css" />
        </head>
        <body>
            <script src="js/jquery-1.5.1.min.js"></script> 
            <script src="js/jquery-ui-1.8.14.custom.min.js"></script>
            <script>
                $(function() {
                    $( ".accordion" ).accordion({
                        autoHeight: false,
                        collapsible: true,
                        navigation: true
                    });
                });
            </script>
        """)
    
    f.write("<p><strong>Number of definitions found: </strong>{}</p>".format(len(definitions)))
    
    #print indexed_definitions
    
    for id, deftextdict in indexed_definitions.items():
        
        docid, docstring = prettify_id(id)
        f.write("<h2>{}</h2>".format(docstring))
        f.write("<p>{}</p>".format(deftextdict['text'].encode('utf-8')))
        for d in deftextdict['definitions'] :
            
            (id, type, scope, concept, modifier, definition, context) = d
            if modifier == 'none' :
                modifier = '' 
                
            if scope == 'none' :
                scope = '(niet aangegeven)'
            
            context_clean = regex.sub(r'/\w+','',context)
            
            definition_text = "<strong>{modifier}</strong> {definition}".format(modifier=modifier.encode('UTF-8'), definition=definition.encode('UTF-8')).lstrip().capitalize()
            
            f.write(t.substitute(type=type.encode('UTF-8'), regex=DefinitionMatcher.def_expressions[type],docid=docid.encode('UTF-8'),docstring=docstring.encode('UTF-8'), scope=scope.encode('UTF-8'), concept=concept.encode('UTF-8').capitalize(), definition_text=definition_text, context=context.encode('UTF-8'), context_clean=context_clean.encode('UTF-8')))
    
    f.write("</body></html>")
    f.close()
    
    
def write_concept_scores(a, outprefix):
    locale.setlocale(locale.LC_NUMERIC,'NL_nl')
    
    npbdfn = "{}_nps_by_doc.csv".format(outprefix)
    dbnpfn = "{}_docs_by_np.csv".format(outprefix)
    nps_writer = csv.writer(open(npbdfn, 'wb'), delimiter=';')
    nps_writer.writerow(['Document ID','Noun Phrase','TC','TF','IDF','MAX TC in Doc','TFIDF','Total Docs','Docs with NP'])
    
    print "Writing to {}".format(npbdfn)
    for doc in a.tfidf['docs'] :
        doc_string = doc
        for term in a.tfidf['docs'][doc] :
            nps_writer.writerow([doc_string,term.encode('UTF-8'), a.tfidf['docs'][doc][term]['tc'], locale.str(a.tfidf['docs'][doc][term]['tf']), locale.str(a.tfidf['docs'][doc][term]['idf']), a.tfidf['docs'][doc][term]['max'], locale.str(a.tfidf['docs'][doc][term]['tfidf']), a.tfidf['docs'][doc][term]['dc'], a.tfidf['docs'][doc][term]['ndc']])
            
    nps_writer = csv.writer(open(dbnpfn, 'wb'), delimiter=';')
    nps_writer.writerow(['Noun Phrase','Document ID','TC','TF','IDF','MAX TC in Doc','TFIDF','Total Docs','Docs with NP'])
    
    print "Writing to {}".format(dbnpfn)
    for term in a.tfidf['nps'] :
        term_string = term
        for doc in a.tfidf['nps'][term] :
            nps_writer.writerow([term_string.encode('UTF-8'),doc.encode('UTF-8'), a.tfidf['nps'][term][doc]['tc'], locale.str(a.tfidf['nps'][term][doc]['tf']), locale.str(a.tfidf['nps'][term][doc]['idf']), a.tfidf['nps'][term][doc]['max'], locale.str(a.tfidf['nps'][term][doc]['tfidf']), a.tfidf['nps'][term][doc]['dc'], a.tfidf['nps'][term][doc]['ndc']])
    print "Done"
    
def write_parse_log(parse_log,outprefix):
    plfn = "{}_parse_log.csv".format(outprefix)
    parse_log_writer = csv.writer(open(plfn,'wb'), delimiter=';')
    parse_log_writer.writerow(['Docuent ID','Parsed Text'])
    
    print "Writing to {}".format(plfn)
    for doc in parse_log :
        for tree in parse_log[doc] :
            ttext = tree.pprint()
            parse_log_writer.writerow([doc.encode('UTF-8'),ttext.encode('UTF-8')])
    
    print "Done"
    
def write_concepts_to_rdf(outprefix):
    cfn = "{}_concepts.ttl".format(outprefix)
    cl = ConceptLinker()
    print "Writing to {}".format(cfn)
    cl.serialize(destination=cfn)
    print "Done"    
    
    
def process(picklefile):
    annotator = Annotator()
    
    training_set = pickle.load(open(picklefile,'r'))
    
    definitions = {}
    indexed_definitions = {}
    for (id,t) in training_set :
        try :
            definitions = annotator.annotate(id, t)
        
            indexed_definitions[id] = {}
            indexed_definitions[id]['text'] = t
            indexed_definitions[id]['definitions'] = definitions
        except KeyboardInterrupt:
            print "Annotation aborted on {0}".format(id)
            break
         

    
    
    annotator.scoreConcepts()
    return definitions, annotator, indexed_definitions
        


if __name__ == '__main__' :
    parser = argparse.ArgumentParser(description='MetaLex Annotator v0.1a')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--full', action='store_true',help='Run on the complete set')
    group.add_argument('--train', action='store_true',help='Run only on the training set')
    group.add_argument('--test', action='store_true',help='Run only on the test set')
    group.add_argument('--file', help='Load a custom pickle file, containing a list of ID/Text tuples')
    
    args = parser.parse_args()

    if args.full :
        definitions, annotator, indexed_definitions = process('full_set.pickle')
        outprefix = "full"
    elif args.train :
        definitions, annotator, indexed_definitions = process('training_set.pickle')
        outprefix = "train"
    elif args.test :
        definitions, annotator, indexed_definitions = process('test_set.pickle')
        outprefix = "test"
    elif args.file :
        (a,b) = os.path.split(args.file)
        (outprefix,ext) = os.path.splitext(b)
        definitions, annotator, indexed_definitions = process(args.file)
    else :
        parser.print_help()
        
        quit()
        
    
    write_concept_scores(annotator,outprefix)
    
    write_definition_report(indexed_definitions, definitions,outprefix)
    
    write_parse_log(annotator.parse_log,outprefix)
    
#    write_concepts_to_rdf(outprefix)







