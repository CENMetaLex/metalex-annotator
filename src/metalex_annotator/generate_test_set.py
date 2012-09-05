# -*- coding: utf-8 -*-
'''
Created on 27 Apr 2011

@author: hoekstra
'''

from xml.etree.ElementTree import ElementTree
import glob
import pickle
import random
import csv
import sys
import re



if __name__ == '__main__' :
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else :
        print """MetaLex Annotator v0.1a 
Copyright (c) 2011, Rinke Hoekstra, Universiteit van Amsterdam
Licensed under the AGPL v3 (see http://www.gnu.org/licenses/agpl-3.0.txt)
        
    Script for generating a full set of articles, as well as a training and test set (1:4)

        Usage:
        python generate_test_set.py [path-to-metalex-files]
        
    """
    
        exit()
    
    tree = ElementTree()

    list = glob.glob(path+"/*.xml")
    
    
    
    
    articles = []
    
    for f in list :
        print f
        try :
            bwbid = re.search("(.*)\..*",f).group(1)
            outfile = "{}.pickle".format(bwbid)
            csvoutfile = "{}.csv".format(bwbid)
            root = tree.parse(f)
            
            hcontainers = root.findall('.//{http://www.metalex.eu/metalex/1.0}hcontainer')
            
            for hc in hcontainers :
                if 'class' in hc.attrib.keys() :
                    about = hc.attrib['about']
                    if hc.attrib['class'] == 'artikel' :
                        containers = hc.findall('{http://www.metalex.eu/metalex/1.0}container')
                        for c in containers :
                            text = ''
                            for t in c.itertext() :
                                text += " " + t.strip()
                        
                        articles.append((about,text))
                        
            print "Dumping {} articles to file...".format(len(articles))
            print "Writing to {}".format(outfile)
            pickle.dump(articles, open(outfile,'w'))
            writer = csv.writer(open(csvoutfile,'w'), delimiter=';')
            writer.writerow(['ID','Text'])
            print "Writing to {}".format(csvoutfile)
            for (id,t) in articles :
                writer.writerow([id.encode('UTF-8'),t.encode('UTF-8')])
            print "Done"
            
        except Exception as e:
            print "Some error: {}".format(e)
            
    print "DONE!"

