'''
Created on 3 May 2011

@author: hoekstra
'''
import sys
import re
from annotate import Annotator
from xml.etree.ElementTree import ElementTree


if __name__ == '__main__' :
    if len(sys.argv) > 1:
        uri = sys.argv[1]
        print 'Lookup',uri
        
        regex = r'.*?(BWB\w\d+).*?(\d\d\d\d-\d\d-\d\d)'
        
        m = re.search(regex, uri)

        
        if m :
            bwbid = m.group(1)
            print bwbid
            version = m.group(2)
            print version
            
            f = '../../../metalex_converter/out/{0}_{1}_ml.xml'.format(bwbid,version)
            
            tree = ElementTree()
            root = tree.parse(f)
            
            element = root.find(".//*[@about='"+uri+"']")
            
            a = Annotator()
            
            
            text = ''
            for t in element.itertext() :
                text += " " + t.strip()
            
            print text
            
            nps, tokenized_raw, n_tagged_raw, parsed_raw = a.process(id, text)
            
            out = ''
            for s in tokenized_raw:
                for w in s :
                    out += w + ' '
                out += '\n\n'
            
            print out.rstrip()
            
            out = ''
            for s in n_tagged_raw:
                for (w,t) in s :
                    out += w + '/' + t + ' '
                out += '\n\n'
            
            print out.rstrip()
            
            
            
            
            
        