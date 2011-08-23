# -*- coding: utf-8 -*-
'''
Created on 27 Apr 2011

@author: hoekstra
'''

from annotate import Annotator
from xml.etree.ElementTree import ElementTree
import csv
from cornetto.linker import ConceptLinker
from definition.matcher import DefinitionMatcher
from string import Template
import regex
import pickle



def prettify_id(id):
    docid = regex.sub(r'/id/','/doc/',regex.sub('$','/data.xml',id))
    
    bwb = regex.search('BWB(?P<bwb>\w+?)/',id).group('bwb')
    docstring = 'BWB{} : '.format(bwb)
    for m in regex.finditer(r'/(?P<part>(hoofdstuk|artikel|paragraaf|sectie|lid|onderdeel|afdeling)?)/(?P<index>([ivclmxIVCLMX0-9\:\.\-\s]+([a-z]+)?))',id) :
        docstring = docstring + "{} {}, ".format(m.group('part').capitalize(),m.group('index')) 
    
    docstring = docstring.rstrip(', ')
    return docid, docstring


tree = ElementTree()
a = Annotator()

training_set = pickle.load(open('training_set.pickle','r'))

count = 0
pos = 2
indexed_definitions = {}
for (id,t) in training_set :
    count = count + 1
    if count > pos : 
        break
    print id
    nps, tokenized, tagged, parsed, definitions = a.process(id, t)

    indexed_definitions[id] = {}
    indexed_definitions[id]['text'] = t
    indexed_definitions[id]['definitions'] = definitions
     
    if len(nps) < 1 :
        print "Could not find NP in:\n{0}\n{1}\n{2}".format(t.encode('UTF-8'), tokenized, tagged)


a.scoreConcepts()
        

nps_writer = csv.writer(open('nps_by_doc.csv', 'wb'), delimiter=';')
nps_writer.writerow(['ID','NP','TF','TFIDF'])

print "Writing to nps_by_doc.csv"
for doc in a.tfidf['docs'] :
    doc_string = doc
    for term in a.tfidf['docs'][doc] :
        nps_writer.writerow([doc_string,term.encode('UTF-8'), a.tfidf['docs'][doc][term]['tf'], a.tfidf['docs'][doc][term]['tfidf']])
        doc_string = ''
        
nps_writer = csv.writer(open('docs_by_np.csv', 'wb'), delimiter=';')
nps_writer.writerow(['NP','ID','TF','TFIDF'])

print "Writing to docs_by_np.csv"
for term in a.tfidf['nps'] :
    term_string = term
    for doc in a.tfidf['nps'][term] :
        nps_writer.writerow([term_string.encode('UTF-8'),doc.encode('UTF-8'), a.tfidf['nps'][term][doc]['tf'], a.tfidf['nps'][term][doc]['tfidf']])
        term_string = ''
print "Done"

def_writer = csv.writer(open('definitions.csv', 'wb'), delimiter=';')
def_writer.writerow(['ID','Type','Scope','Concept','Modifier', 'Def','Context'])

print "Writing to definitions.csv"
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

print "Writing to definitions.html"
f = open("definitions.html","w")
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

print indexed_definitions

for id, deftextdict in indexed_definitions.items():
    
    docid, docstring = prettify_id(id)
    f.write("<h1>{}</h1>".format(docstring))
    f.write("<p>{}</p>".format(deftextdict['text']))
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


print "Writing to concepts.rdf"
ConceptLinker.serialize(destination='concepts.rdf')
print "Done"    







