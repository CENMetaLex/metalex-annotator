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



tree = ElementTree()


# Vreemdelingenwet 2000
list = glob.glob('../../*_mls.xml')



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

