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




if __name__ == '__main__' :
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else :
        print """MetaLex Annotator v0.1a 
Copyright (c) 2011, Rinke Hoekstra, Universiteit van Amsterdam
Licensed under the AGPL v3 (see http://www.gnu.org/licenses/agpl-3.0.txt)
        
    Script for generating a full set of articles, as well as a training and test set (1:4)

        Usage:
        python generate_evaluation_set.py [path-to-metalex-files]
        
    Make sure to run 'generate_evaluation_sets.py' first!"""
    
        exit()
    
    tree = ElementTree()

    list = glob.glob(path+"/*.xml")
    
    
    articles = []
    
    for f in list :
        print f
        try :
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
        except Exception as e:
            print "Some error: {}".format(e)
            
            
    setsize = len(articles)
    train_setsize = setsize/5
    random.seed()
    
    randomized_set = random.sample(articles, setsize)
    
    
    training_set = randomized_set[:train_setsize]
    test_set = randomized_set[train_setsize:]
    
    print "Training set size: {}\nTest set size: {}".format(train_setsize,len(test_set))
    
    print "Dumping sets to file..."
    print "Writing to full_set.pickle"
    pickle.dump(articles, open('full_set.pickle','w'))
    full_writer = csv.writer(open('full_set.csv', 'wb'), delimiter=';')
    full_writer.writerow(['ID','Text'])
    print "Writing to full_set.csv"
    for (id,t) in articles :
        full_writer.writerow([id.encode('UTF-8'),t.encode('UTF-8')])
    print "Done"
    
    print "Writing to training_set.pickle"
    pickle.dump(training_set, open('training_set.pickle','w'))
    train_writer = csv.writer(open('training_set.csv', 'wb'), delimiter=';')
    train_writer.writerow(['ID','Text'])
    print "Writing to training_set.csv"
    for (id,t) in training_set :
        train_writer.writerow([id.encode('UTF-8'),t.encode('UTF-8')])
    print "Done"
    
    print "Writing to test_set.pickle"
    pickle.dump(test_set,open('test_set.pickle','w'))
    test_writer = csv.writer(open('test_set.csv', 'wb'), delimiter=';')
    test_writer.writerow(['ID','Text'])
    print "Writing to test_set.csv"
    for (id,t) in test_set :
        test_writer.writerow([id.encode('UTF-8'),t.encode('UTF-8')])
    print "Done"

