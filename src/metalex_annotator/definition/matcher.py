# -*- coding: utf-8 -*-
'''
Created on 8 Jun 2011

@author: hoekstra
'''

import regex
from nltk.tree import Tree
from util import Util
from xml.sax.saxutils import escape


class DefinitionMatcher:
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        

    def getMultipartMatch(self, id, re_def_head, re_def_tail, re_def_last, num, stext, definitions):
        scope, mod = self.getHeadMatch(id, re_def_head, num, stext, definitions)
        
        if (scope and mod) :
            definitions, tail_match = self.getTailMatches(id, re_def_tail, re_def_last, num, scope, mod, stext, definitions)
            return definitions, tail_match
        else :
            return definitions, False

    def getTailMatches(self, id, re_def, re_def_last, num, scope, mod, stext, definitions):
        match = False
        for m in re_def.finditer(stext) :
            match = True
            term = regex.sub(r"/\w+","", m.group('term'))
            definition = regex.sub(r"/\w+","", m.group('def'))
            term, definition = self.selectTermAndDefinition(term, definition)
            print scope, term, mod, definition
            definitions.append((id, num, scope, term, mod, definition, stext))
        
        # If we found a match, there should be a 'last' element as well (if provided)
        if match and re_def_last != None:
            for m in re_def_last.finditer(stext) :
                term = regex.sub(r"/\w+","", m.group('term'))
                definition = regex.sub(r"/\w+","", m.group('def'))
                term, definition = self.selectTermAndDefinition(term, definition)
                print scope, term, mod, definition
                definitions.append((id, num, scope, term, mod, definition, stext))                
            
        return definitions, match

    def getHeadMatch(self, id, re_def, num, stext, definitions):
        m = re_def.search(stext)
        
        if m :
            if (m.group('scope') == None) :
                scope = 'none'
            else :
                scope = regex.sub(r"/\w+","", m.group('scope'))
            
            if (m.group('mod') == None) :
                mod = 'none'
            else :
                mod = regex.sub(r"/\w+","", m.group('mod'))
            return scope, mod
        
        return None, None 
    
    
    def getMultipartMatchTermHead(self, id, re_def_head, re_def_tail, num, stext, definitions):
        scope, mod, term = self.getTermHeadMatch(id, re_def_head, num, stext, definitions)
        
        if (scope and mod and term) :
            definitions, tail_match = self.getShortTailMatches(id, re_def_tail, num, scope, mod, term, stext, definitions)
            return definitions, tail_match
        else :
            return definitions, False

    def getShortTailMatches(self, id, re_def, num, scope, mod, term, stext, definitions):
        match = False
        for m in re_def.finditer(stext) :
            match = True
            definition = regex.sub(r"/\w+","", m.group('def'))
            print scope, term, mod, definition
            definitions.append((id, num, scope, term, mod, definition, stext))
            
        return definitions, match

    def getTermHeadMatch(self, id, re_def, num, stext, definitions):
        m = re_def.search(stext)
        
        if m :
            term = regex.sub(r"/\w+","", m.group('term'))
            if (m.group('scope') == None) :
                scope = 'none'
            else :
                scope = regex.sub(r"/\w+","", m.group('scope'))
            
            if (m.group('mod') == None) :
                mod = 'none'
            else :
                mod = regex.sub(r"/\w+","", m.group('mod'))
            return scope, mod, term
        
        return None, None, None    

    
    def getMatch(self, id, re_def, num, stext, definitions):
        m = re_def.search(stext)
        
        if m :
            term = regex.sub(r"/\w+","", m.group('term'))
            definition = regex.sub(r"/\w+","", m.group('def'))
            if (m.group('scope') == None) :
                scope = 'none'
            else :
                scope = regex.sub(r"/\w+","", m.group('scope'))
            
            if (m.group('mod') == None) :
                mod = 'none'
            else :
                mod = regex.sub(r"/\w+","", m.group('mod'))
                
            term, definition = self.selectTermAndDefinition(term, definition)
            
            definitions.append((id, num, scope, term, mod, definition, stext))
            return definitions, True
        
        return definitions, False
    
    def selectTermAndDefinition(self, term, definition):
        # Sometimes it's a bit unclear which is the term, and which the definition
        # Rule of thumb: the longer string is the definition
        
        #### CHANGED: Always return term and definition as originally recognised
        return term, definition
        
#        if len(term) > len(definition) :
#            return definition, term
#        else :
#            return term, definition
#        

#    re_def4a = regex.compile(r".*(wordt|worden)/\w+\s((die|deze)/\w+\s)?(voorts/\w+\s)?.*?(./Punc.*./Punc\s)?(?P<np>.*?)\s(voorts/\w+\s)?(aangewezen|aangemerkt|behandeld)/\w+\sals/\w+")
#    re_def4b = regex.compile(r".*(wordt|worden)/\w+\s(voorts/\w+\s)?.*?met/\w+\s(?P<np>.*?)\s(voorts/\w+\s)?gelijkgesteld/\w+")
#    re_def5 = regex.compile(r"tot/\w+\s(?P<np>.*?)\s(behoort|behoren)/\w+\s(?P<mod>(mede|niet|slechts))/\w+")
#    re_def6 = regex.compile(r"als/\w+\s(?P<np>.*?)\s(wordt|worden)/\w+\s(voorts/\w+\s)?(aangewezen|aangemerkt|behandeld)/\w+\s\:/\w+\s(\w+/Index\s)?.*")
#    re_def7 = regex.compile(r"(.*?/Num\s)?(?P<np>.*?)\somvat/\w+\s(mede/\w+\s)?")    

    
    

    
    ONDER = "(onder|tot)/\w+\s"
    KAN = "(kan|kunnen)/\w+\s"
    WORDT = "(?<!(dat/\w+\s))(wordt|worden)/\w+\s(?!\w+/V\s)"
    VERSTAAN = "(verstaan|begrepen|gerekend)/\w+\s"
    BEHOREN = "(behoort|behoren)/\w+\s"
    OMVAT = "omvat/\w+\s"
    
    MOD = "(?P<mod>(mede|niet|slechts|(in/\w+\salle/\w+\sopzichten/\w+\s))/\w+\s)"
    
    DIE = "((die|deze)/\w+\s)"
    VOORTS = "((voorts/\w+\s)|(voor/\w+\s.*?))"
    
    GELIJKGESTELD = "((gelijkgesteld/\w+\s)|(gelijk/\w+\sgesteld/\w+\s))"
    MET = "(?<!(en|of)/EnOf\s)met/\w+\s" 
    AANGEW = "((aangewezen|aangemerkt|behandeld|beschouwd)/\w+\s)"
    ALS = "(?<!(en|of)/EnOf\s)als/\w+\s(?!bedoeld)"
    INDIEN = "((als|indien|wanneer|behoudens|(in/\w+?\sgeval/\w+?\s))/\w+\s)"
    
    WET = "(wet|artikel|lid|bepalingen|bepaalde|hoofdstuk|afdeling|paragraaf|(algemene/\w+\swet/\w+\sbestuursrecht)|onderdeel)"
    
    NUM = "(.+?/Num\s)"
    PUNC = "(./Punc\s)"
    NOPUNC = "((?!./Punc)\s)"
    ENDPUNC = "\./Punc$"
    COLON = "(\:/Punc\s)"
    SEMICOLON = "(\;/Punc\s)"
    SCOLPUNC = "(\;|\.)/Punc"
    INDEX = "(.{1,4}?/Index\s)"
    NOINDEX = "(?!.{1,4}?/Index)"
    INUM = "(.{1,4}?/(Index|Num|Ref)\s)"
    
    SCOPE = "(voor/Prep\s(?!elke)(?P<scope>[^:;]*?{WET}/\w+(\s{INUM})?))".format(WET=WET,INUM=INUM)
    
    NOTERMSTART = "(?!({INUM}))(?!(en|of)/EnOf)(?!voor/Prep\s(de/\w+\s)?toepassing)(?!{INDIEN})(?!(mede|niet|slechts|(in/\w+\salle/\w+\sopzichten/\w+\s)))".format(INDIEN=INDIEN,MOD=MOD,INUM=INUM)
    
    # Definitions and terms may contain any character, but must start with a letter.
    DEF = "(?P<def>\w.*?)\s"
    TERM = "{NOTERMSTART}(?P<term>\w[^;:]*?)\s".format(NOTERMSTART=NOTERMSTART)

    
    # Onder [term] kan voor de toepassing van deze wet worden verstaan [def].

    d1 = r"^{INUM}?{ONDER}{TERM}{PUNC}?{KAN}?{SCOPE}?{WORDT}{PUNC}?{MOD}?{VERSTAAN}{DEF}{ENDPUNC}".format(INUM=INUM,ONDER=ONDER,TERM=TERM,PUNC=PUNC,KAN=KAN,WORDT=WORDT,SCOPE=SCOPE,MOD=MOD,VERSTAAN=VERSTAAN,DEF=DEF,ENDPUNC=ENDPUNC)

    # Onder [term] wordt voor de toepassing van deze wet begrepen [def].
    # Tot [term] wordt gerekend [def]   
    d1a = r"^{INUM}?{ONDER}{TERM}{PUNC}?{WORDT}{PUNC}?{SCOPE}?{MOD}?{VERSTAAN}{DEF}{ENDPUNC}".format(INUM=INUM,ONDER=ONDER,TERM=TERM,PUNC=PUNC,WORDT=WORDT,SCOPE=SCOPE,MOD=MOD,VERSTAAN=VERSTAAN,DEF=DEF,ENDPUNC=ENDPUNC)

    
    # [scope] wordt mede verstaan onder [term]: [def].
    # [scope] wordt begrepen onder [term]: [def].
    d2 = r"{SCOPE}?{WORDT}{MOD}?{VERSTAAN}{ONDER}{TERM}{COLON}{NOINDEX}{DEF}{ENDPUNC}".format(SCOPE=SCOPE,WORDT=WORDT,MOD=MOD,VERSTAAN=VERSTAAN,ONDER=ONDER,TERM=TERM,COLON=COLON,DEF=DEF,ENDPUNC=ENDPUNC,NOINDEX=NOINDEX)
    
    # [scope] wordt onder [term] mede verstaan [def]
    d3 = r"{SCOPE}?{WORDT}{ONDER}{TERM}{MOD}?{VERSTAAN}{PUNC}{DEF}{ENDPUNC}".format(SCOPE=SCOPE,WORDT=WORDT,MOD=MOD,VERSTAAN=VERSTAAN,ONDER=ONDER,TERM=TERM,COLON=COLON,DEF=DEF,PUNC=PUNC,ENDPUNC=ENDPUNC)
    
    # [term] wordt [scope] voorts aangewezen als [def]
    d4 = r"^{INUM}?{TERM}{PUNC}?{WORDT}{DIE}?({PUNC}.*{PUNC})?{SCOPE}?{VOORTS}?{MOD}?{AANGEW}{ALS}{DEF}{ENDPUNC}".format(INUM=INUM,DEF=DEF,WORDT=WORDT,DIE=DIE,PUNC=PUNC,SCOPE=SCOPE,VOORTS=VOORTS,MOD=MOD,AANGEW=AANGEW,ALS=ALS,TERM=TERM,ENDPUNC=ENDPUNC)

    # [term] wordt [scope] voorts gelijkgesteld met [def]
    d4a = r"^{INUM}?{TERM}{PUNC}?{WORDT}{DIE}?({PUNC}.*{PUNC})?{SCOPE}?{VOORTS}?{MOD}?{GELIJKGESTELD}{MET}{DEF}{ENDPUNC}".format(INUM=INUM,DEF=DEF,WORDT=WORDT,DIE=DIE,PUNC=PUNC,SCOPE=SCOPE,VOORTS=VOORTS,MOD=MOD,GELIJKGESTELD=GELIJKGESTELD,MET=MET,TERM=TERM,ENDPUNC=ENDPUNC)

    
    # [scope] worden die, mits blabla, [term] voorts aangewezen als [def]
    d5 = r"{SCOPE}({PUNC}.*)?{WORDT}{DIE}?{VOORTS}?.*?({PUNC}.*{PUNC})?{TERM}{VOORTS}?{MOD}?{AANGEW}{ALS}{DEF}{ENDPUNC}".format(SCOPE=SCOPE,PUNC=PUNC,WORDT=WORDT,DIE=DIE,VOORTS=VOORTS,DEF=DEF,MOD=MOD,AANGEW=AANGEW,ALS=ALS,TERM=TERM,ENDPUNC=ENDPUNC)
    
    # [scope] worden die, mits blabla, [term] voorts gelijkgesteld met [def]
    d5a = r"{SCOPE}({PUNC}.*)?{WORDT}{DIE}?{VOORTS}?.*?({PUNC}.*{PUNC})?{TERM}{VOORTS}?{MOD}?{GELIJKGESTELD}{MET}{DEF}{ENDPUNC}".format(SCOPE=SCOPE,PUNC=PUNC,WORDT=WORDT,DIE=DIE,VOORTS=VOORTS,DEF=DEF,MOD=MOD,GELIJKGESTELD=GELIJKGESTELD,MET=MET,TERM=TERM,ENDPUNC=ENDPUNC)
    
    # [scope] worden die, mits blabla, [term] voorts aangewezen als [def]
    d5b = r"{SCOPE}({PUNC}.*)?{WORDT}{DIE}?{VOORTS}?.*?({PUNC}.*{PUNC})?{TERM}{VOORTS}?{MOD}?{AANGEW}{ALS}{DEF}{ENDPUNC}".format(SCOPE=SCOPE,PUNC=PUNC,WORDT=WORDT,DIE=DIE,VOORTS=VOORTS,DEF=DEF,MOD=MOD,AANGEW=AANGEW,ALS=ALS,TERM=TERM,ENDPUNC=ENDPUNC)
    
    # [scope] worden die, mits blabla, [term] voorts gelijkgesteld met [def]
    d5c = r"{SCOPE}({PUNC}.*)?{WORDT}{DIE}?{VOORTS}?.*?({PUNC}.*{PUNC})?{TERM}{VOORTS}?{MOD}?{GELIJKGESTELD}{MET}{DEF}{ENDPUNC}".format(SCOPE=SCOPE,PUNC=PUNC,WORDT=WORDT,DIE=DIE,VOORTS=VOORTS,DEF=DEF,MOD=MOD,GELIJKGESTELD=GELIJKGESTELD,MET=MET,TERM=TERM,ENDPUNC=ENDPUNC)

    
    # In geval van schenking wordt [scope] [term] voorts als [def] aangemerkt
    d6 = r"{INDIEN}.*{WORDT}{PUNC}?{SCOPE}?{PUNC}?{TERM}{VOORTS}?{MOD}?{ALS}{DEF}{AANGEW}{ENDPUNC}".format(INDIEN=INDIEN,WORDT=WORDT,SCOPE=SCOPE,PUNC=PUNC,DEF=DEF,VOORTS=VOORTS,MOD=MOD,ALS=ALS,TERM=TERM,AANGEW=AANGEW,ENDPUNC=ENDPUNC)
    
    # In geval van schenking wordt [scope] [term] voorts met [def] gelijkgesteld
    d6a = r"{INDIEN}.*{WORDT}{PUNC}?{SCOPE}?{PUNC}?{TERM}{VOORTS}?{MOD}?{MET}{DEF}{GELIJKGESTELD}{ENDPUNC}".format(INDIEN=INDIEN,WORDT=WORDT,SCOPE=SCOPE,PUNC=PUNC,DEF=DEF,VOORTS=VOORTS,MOD=MOD,MET=MET,TERM=TERM,GELIJKGESTELD=GELIJKGESTELD,ENDPUNC=ENDPUNC)
    
    # wordt [scope] [term] voorts als [def] aangemerkt in geval van X
    d6b = r"{WORDT}{PUNC}?{SCOPE}?{PUNC}?{TERM}{VOORTS}?{MOD}?{ALS}{DEF}{AANGEW}{PUNC}?{INDIEN}?".format(INDIEN=INDIEN,WORDT=WORDT,SCOPE=SCOPE,PUNC=PUNC,DEF=DEF,VOORTS=VOORTS,MOD=MOD,ALS=ALS,TERM=TERM,AANGEW=AANGEW,ENDPUNC=ENDPUNC)
    
    # wordt [scope] [term] voorts met [def] gelijkgesteld in geval van schenking
    d6c = r"{WORDT}{PUNC}?{SCOPE}?{PUNC}?{TERM}{VOORTS}?{MOD}?{MET}{DEF}{GELIJKGESTELD}{PUNC}?{INDIEN}?".format(INDIEN=INDIEN,WORDT=WORDT,SCOPE=SCOPE,PUNC=PUNC,DEF=DEF,VOORTS=VOORTS,MOD=MOD,MET=MET,TERM=TERM,GELIJKGESTELD=GELIJKGESTELD,ENDPUNC=ENDPUNC)

    # [term] wordt [scope] voorts als [def] aangemerkt in geval van schenking 
    d6d = r"{INUM}?{TERM}{PUNC}?{WORDT}{PUNC}?{SCOPE}?{PUNC}?{VOORTS}?{MOD}?{ALS}{DEF}{AANGEW}{PUNC}?{INDIEN}?".format(INDIEN=INDIEN,WORDT=WORDT,SCOPE=SCOPE,PUNC=PUNC,DEF=DEF,VOORTS=VOORTS,MOD=MOD,ALS=ALS,TERM=TERM,AANGEW=AANGEW,ENDPUNC=ENDPUNC,INUM=INUM)
    
    # [term] wordt [scope] voorts met [def] gelijkgesteld in geval van schenking
    d6e = r"{INUM}?{TERM}{PUNC}?{WORDT}{PUNC}?{SCOPE}?{PUNC}?{VOORTS}?{MOD}?{MET}{DEF}{GELIJKGESTELD}{PUNC}?{INDIEN}?".format(INDIEN=INDIEN,WORDT=WORDT,SCOPE=SCOPE,PUNC=PUNC,DEF=DEF,VOORTS=VOORTS,MOD=MOD,MET=MET,TERM=TERM,GELIJKGESTELD=GELIJKGESTELD,ENDPUNC=ENDPUNC,INUM=INUM)

#    d6e = r"{TERM}.*{WORDT}.*{MET}.*{DEF}.*{GELIJKGESTELD}.*".format(INDIEN=INDIEN,WORDT=WORDT,SCOPE=SCOPE,PUNC=PUNC,DEF=DEF,VOORTS=VOORTS,MOD=MOD,MET=MET,TERM=TERM,GELIJKGESTELD=GELIJKGESTELD,ENDPUNC=ENDPUNC,INUM=INUM)


    
    # [scope] wordt voorts ALS [term] aangewezen [def]
    # Might conflict with d8
    d7a = r"{SCOPE}?({PUNC}.*)?{WORDT}{VOORTS}?{MOD}?{ALS}{TERM}{VOORTS}?{AANGEW}{NOPUNC}{DEF}{ENDPUNC}".format(SCOPE=SCOPE,PUNC=PUNC,WORDT=WORDT,VOORTS=VOORTS,MOD=MOD,ALS=ALS,TERM=TERM,AANGEW=AANGEW,NOPUNC=NOPUNC,DEF=DEF,ENDPUNC=ENDPUNC)
    # ... wordt [scope] voorts ALS [term] aangewezen [def]
    # Might conflict with d8
    d7b = r"{WORDT}{SCOPE}?({PUNC}.*)?{VOORTS}?{MOD}?{ALS}{TERM}{VOORTS}?{AANGEW}{NOPUNC}{DEF}{ENDPUNC}".format(SCOPE=SCOPE,PUNC=PUNC,WORDT=WORDT,VOORTS=VOORTS,MOD=MOD,ALS=ALS,TERM=TERM,AANGEW=AANGEW,NOPUNC=NOPUNC,DEF=DEF,ENDPUNC=ENDPUNC)
    
    # [scope] wordt voorts met [term] gelijkgesteld [def]
    # Might conflict with d8
    d7c = r"{SCOPE}?({PUNC}.*)?{WORDT}{VOORTS}?{MOD}?{MET}{TERM}{VOORTS}?{GELIJKGESTELD}{NOPUNC}{DEF}{ENDPUNC}".format(SCOPE=SCOPE,PUNC=PUNC,WORDT=WORDT,VOORTS=VOORTS,MOD=MOD,MET=MET,TERM=TERM,GELIJKGESTELD=GELIJKGESTELD,NOPUNC=NOPUNC,DEF=DEF,ENDPUNC=ENDPUNC)
    # ... wordt [scope] voorts met [term] gelijkgesteld [def]
    # Might conflict with d8
    d7d = r"{WORDT}{SCOPE}?({PUNC}.*)?{VOORTS}?{MOD}?{MET}{TERM}{VOORTS}?{GELIJKGESTELD}{NOPUNC}{DEF}{ENDPUNC}".format(SCOPE=SCOPE,PUNC=PUNC,WORDT=WORDT,VOORTS=VOORTS,MOD=MOD,MET=MET,TERM=TERM,GELIJKGESTELD=GELIJKGESTELD,NOPUNC=NOPUNC,DEF=DEF,ENDPUNC=ENDPUNC)
   


    
    # ... wordt voorts als [term] aangemerkt: a. [def]; b. [def]
    d8_term_head = r"{SCOPE}?({PUNC}.*)?{WORDT}{VOORTS}?{MOD}?{ALS}{TERM}{VOORTS}?{AANGEW}{PUNC}".format(SCOPE=SCOPE,PUNC=PUNC,WORDT=WORDT,VOORTS=VOORTS,MOD=MOD,ALS=ALS,TERM=TERM,AANGEW=AANGEW)
    d8_short_tail = r"{INDEX}{DEF}{SCOLPUNC}".format(INDEX=INDEX,DEF=DEF,SCOLPUNC=SCOLPUNC)

    # ... wordt voorts als [term] aangemerkt: a. [def]; b. [def]
    d8a_term_head = r"{SCOPE}?({PUNC}.*)?{WORDT}{VOORTS}?{MOD}?{MET}{TERM}{VOORTS}?{GELIJKGESTELD}{PUNC}".format(SCOPE=SCOPE,PUNC=PUNC,WORDT=WORDT,VOORTS=VOORTS,MOD=MOD,MET=MET,TERM=TERM,GELIJKGESTELD=GELIJKGESTELD)
    d8a_short_tail = r"{INDEX}{DEF}{SCOLPUNC}".format(INDEX=INDEX,DEF=DEF,SCOLPUNC=SCOLPUNC)


  
    # [scope] wordt mede verstaan onder: a. ditjes: ditjes die dingen doen; b. datjes: datjes die geen dingen doen
    d10_head = r"{SCOPE}?{WORDT}{MOD}?{VERSTAAN}{ONDER}{COLON}{INDEX}".format(SCOPE=SCOPE,WORDT=WORDT,MOD=MOD,VERSTAAN=VERSTAAN,ONDER=ONDER,COLON=COLON,INDEX=INDEX)
    d10_tail = r"{INDEX}{TERM}{COLON}{DEF}{SEMICOLON}(?={INDEX})".format(INDEX=INDEX,TERM=TERM,COLON=COLON,DEF=DEF,SEMICOLON=SEMICOLON)
    d10_last = r".*{INDEX}{TERM}{COLON}{DEF}{ENDPUNC}".format(INDEX=INDEX,TERM=TERM,COLON=COLON,DEF=DEF,ENDPUNC=ENDPUNC)

    d10_tail_multipart = r"{INDEX}{TERM}{COLON}{INUM}{DEF}{SCOLPUNC}".format(INDEX=INDEX,TERM=TERM,COLON=COLON,INUM=INUM,DEF=DEF,SCOLPUNC=SCOLPUNC)
  
    
    # [scope] wordt aangewezen: [term] als [def]
    d9_head = r"{SCOPE}?{WORDT}{MOD}?{AANGEW}{PUNC}".format(SCOPE=SCOPE,WORDT=WORDT,MOD=MOD,AANGEW=AANGEW,PUNC=PUNC)
    d9_tail = r"{INDEX}{DEF}{ALS}{TERM}{SCOLPUNC}".format(INDEX=INDEX,DEF=DEF,ALS=ALS,TERM=TERM,SCOLPUNC=SCOLPUNC)

    # [scope] wordt gelijkgesteld: [term] met [def]
    d9a_head = r"{SCOPE}?{WORDT}{MOD}?{GELIJKGESTELD}{PUNC}".format(SCOPE=SCOPE,WORDT=WORDT,MOD=MOD,GELIJKGESTELD=GELIJKGESTELD,PUNC=PUNC)
    d9a_tail = r"{INDEX}{DEF}{MET}{TERM}{SCOLPUNC}".format(INDEX=INDEX,DEF=DEF,MET=MET,TERM=TERM,SCOLPUNC=SCOLPUNC)

    
    # [scope] wordt mede verstaan onder: a. ditjes ditjes die dingen doen; b. datjes datjes die geen dingen doen
    d11_head = r"{SCOPE}?{WORDT}{MOD}?{VERSTAAN}{ONDER}{COLON}{INDEX}".format(SCOPE=SCOPE,WORDT=WORDT,MOD=MOD,VERSTAAN=VERSTAAN,ONDER=ONDER,COLON=COLON,INDEX=INDEX)
    d11_tail = r"{INDEX}{TERM}{DEF}{SCOLPUNC}".format(INDEX=INDEX,TERM=TERM,DEF=DEF,SCOLPUNC=SCOLPUNC)
    
    # [scope] wordt mede verstaan onder: ditjes: ditjes die dingen doen; datjes: datjes die geen dingen doen
    d12_head = r"{SCOPE}?{WORDT}{MOD}?{VERSTAAN}{ONDER}{COLON}{NOINDEX}".format(SCOPE=SCOPE,WORDT=WORDT,MOD=MOD,VERSTAAN=VERSTAAN,ONDER=ONDER,COLON=COLON,NOINDEX=NOINDEX)
    d12_tail = r"{TERM}{PUNC}{DEF}{SCOLPUNC}".format(TERM=TERM,PUNC=PUNC,DEF=DEF,SCOLPUNC=SCOLPUNC)
    d12_tail_multipart = r"{TERM}{PUNC}{INUM}{DEF}{SCOLPUNC}".format(TERM=TERM,PUNC=PUNC,INUM=INUM,DEF=DEF,SCOLPUNC=SCOLPUNC)
    
    
    d13 = r"^{INUM}?{ONDER}{TERM}{BEHOREN}{SCOPE}?{MOD}?{DEF}".format(ONDER=ONDER,TERM=TERM,BEHOREN=BEHOREN,SCOPE=SCOPE,MOD=MOD,DEF=DEF,INUM=INUM)
    
    # Als [term] wordt voorts mede aangewezen: a. visjes; b. kastanjes.
    d14_term_head = r"{ALS}{TERM}{WORDT}{SCOPE}?{VOORTS}?{MOD}?{AANGEW}{COLON}{INDEX}".format(ALS=ALS,TERM=TERM,WORDT=WORDT,SCOPE=SCOPE,VOORTS=VOORTS,MOD=MOD,AANGEW=AANGEW,COLON=COLON,INDEX=INDEX)
    d14_short_tail = r"{INDEX}{DEF}{SCOLPUNC}".format(INDEX=INDEX,DEF=DEF,SCOLPUNC=SCOLPUNC)

    # Met [term] wordt voorts mede gelijkgesteld: a. visjes; b. kastanjes.
    d14a_term_head = r"{MET}{TERM}{WORDT}{SCOPE}?{VOORTS}?{MOD}?{GELIJKGESTELD}{COLON}{INDEX}".format(MET=MET,TERM=TERM,WORDT=WORDT,SCOPE=SCOPE,VOORTS=VOORTS,MOD=MOD,GELIJKGESTELD=GELIJKGESTELD,COLON=COLON,INDEX=INDEX)
    d14a_short_tail = r"{INDEX}{DEF}{SCOLPUNC}".format(INDEX=INDEX,DEF=DEF,SCOLPUNC=SCOLPUNC)

    
    # 1. [term] omvat voor de toepassing van deze wet mede kastanjebomen.
    d15 = r"^{INUM}{TERM}{OMVAT}{SCOPE}?{VOORTS}?{MOD}?{DEF}{ENDPUNC}".format(NUM=NUM,TERM=TERM,OMVAT=OMVAT,SCOPE=SCOPE,VOORTS=VOORTS,MOD=MOD,DEF=DEF,ENDPUNC=ENDPUNC,INUM=INUM)
      
    re_def1 = regex.compile(d1)
    re_def1a = regex.compile(d1a)
    re_def2 = regex.compile(d2)
    re_def3 = regex.compile(d3)
    re_def4 = regex.compile(d4)
    re_def4a = regex.compile(d4a)    
    re_def5 = regex.compile(d5)
    re_def5a = regex.compile(d5a)
    re_def6 = regex.compile(d6)
    re_def6a = regex.compile(d6a)
    re_def6b = regex.compile(d6b)
    re_def6c = regex.compile(d6c)
    re_def6d = regex.compile(d6d)
    re_def6e = regex.compile(d6e)
    re_def7a = regex.compile(d7a)
    re_def7b = regex.compile(d7b)
    re_def7c = regex.compile(d7c)
    re_def7d = regex.compile(d7d)
    re_def8_term_head = regex.compile(d8_term_head)
    re_def8_short_tail = regex.compile(d8_short_tail)
    re_def8a_term_head = regex.compile(d8a_term_head)
    re_def8a_short_tail = regex.compile(d8a_short_tail)
    re_def9_head = regex.compile(d9_head)
    re_def9_tail = regex.compile(d9_tail)
    re_def9a_head = regex.compile(d9a_head)
    re_def9a_tail = regex.compile(d9a_tail)
    re_def10_head = regex.compile(d10_head)
    re_def10_tail = regex.compile(d10_tail)
    re_def10_last = regex.compile(d10_last)
    re_def11_head = regex.compile(d11_head)
    re_def11_tail = regex.compile(d11_tail)
    re_def12_head = regex.compile(d12_head)
    re_def12_tail = regex.compile(d12_tail)
    re_def12_tail_multipart = regex.compile(d12_tail_multipart)
    re_def13 = regex.compile(d13)
    re_def14_term_head = regex.compile(d14_term_head)
    re_def14_short_tail = regex.compile(d14_short_tail)
    re_def14a_term_head = regex.compile(d14a_term_head)
    re_def14a_short_tail = regex.compile(d14a_short_tail)
    re_def15 = regex.compile(d15)
    
    def_expressions = {'1' : escape(d1),
                       '1a': escape(d1a),
                       '2' : escape(d2),
                       '3' : escape(d3),
                       '4' : escape(d4),
                       '5' : escape(d5),
                       '6' : escape(d6),
                       '7a': escape(d7a),
                       '7b': escape(d7b),
                       '4a' : escape(d4a),
                       '5a' : escape(d5a),
                       '6a' : escape(d6a),
                       '6b' : escape(d6b),
                       '6c' : escape(d6c),
                       '6d' : escape(d6d),
                       '6e' : escape(d6e),
                       '7c': escape(d7c),
                       '7d': escape(d7d),
                       '8' : "term head: {}<br/>short tail: {}".format(escape(d8_term_head), escape(d8_short_tail)),
                       '9' : "head: {}<br/>tail: {}".format(escape(d9_head), escape(d9_tail)),
                       '8a' : "term head: {}<br/>short tail: {}".format(escape(d8a_term_head), escape(d8a_short_tail)),
                       '9a' : "head: {}<br/>tail: {}".format(escape(d9a_head), escape(d9a_tail)),
                       '10': "head: {}<br/>tail: {}<br/>last: {}".format(escape(d10_head), escape(d10_tail), escape(d10_last)),
                       '11': "head: {}<br/>tail: {}".format(escape(d11_head), escape(d11_tail)),
                       '12': "head: {}<br/>tail: {}".format(escape(d12_head), escape(d12_tail)),
                       '13': escape(d13),
                       '14': "term head: {}<br/>short tail: {}".format(escape(d14_term_head), escape(d14_short_tail)),
                       '14a': "term head: {}<br/>short tail: {}".format(escape(d14a_term_head), escape(d14a_short_tail)),
                       '15': escape(d15),
    }
    
    def match(self, id, tagged_text):
        definitions = []
        
        for t in tagged_text:
            stext = ""
            for node in t :
                if isinstance(node, Tree) :
                    stext += " "+ Util.flattenNP(node, strip = False) 
                else :
                    stext += Util.flattenLeaf(node, strip = False)
            
            if id == 'http://doc.metalex.eu/id/BWBR0002226/hoofdstuk/I/artikel/4/nl/2011-01-01':
                print '---\ndef6e test:\n{}\n{}\n---'.format(stext,self.d6d)
            
            stext = stext.lstrip().rstrip()
            
            definitions, changed = self.getMatch(id, self.re_def1, '1', stext, definitions)
            if not changed :
                definitions, changed = self.getMatch(id, self.re_def1a, '1a', stext, definitions)
            definitions, changed = self.getMatch(id, self.re_def2, '2', stext, definitions)
            definitions, changed = self.getMatch(id, self.re_def3, '3', stext, definitions)
            definitions, changed = self.getMatch(id, self.re_def4, '4', stext, definitions)
            definitions, changed = self.getMatch(id, self.re_def4a, '4a', stext, definitions)
            # Only try to match d5 if d4 did not match
            if not changed:
                definitions, changed = self.getMatch(id, self.re_def5, '5', stext, definitions)
                definitions, changed = self.getMatch(id, self.re_def5a, '5a', stext, definitions)
            definitions, changed = self.getMatch(id, self.re_def6, '6', stext, definitions)
            definitions, changed = self.getMatch(id, self.re_def6a, '6a', stext, definitions)
            definitions, changed = self.getMatch(id, self.re_def6b, '6b', stext, definitions)
            definitions, changed = self.getMatch(id, self.re_def6c, '6c', stext, definitions)
            definitions, changed = self.getMatch(id, self.re_def6d, '6d', stext, definitions)
            definitions, changed = self.getMatch(id, self.re_def6e, '6e', stext, definitions)
            definitions, changed = self.getMatch(id, self.re_def7a, '7a', stext, definitions)
            definitions, changed = self.getMatch(id, self.re_def7c, '7c', stext, definitions)
            # Only try to match 7b if 7a did not match
            if not changed: 
                definitions, changed = self.getMatch(id, self.re_def7b, '7b', stext, definitions)
                definitions, changed = self.getMatch(id, self.re_def7d, '7d', stext, definitions)

            definitions, changed = self.getMultipartMatchTermHead(id, self.re_def8_term_head, self.re_def8_short_tail, '8', stext, definitions)
            definitions, changed = self.getMultipartMatchTermHead(id, self.re_def8a_term_head, self.re_def8a_short_tail, '8a', stext, definitions)
            
            definitions, changed = self.getMultipartMatch(id, self.re_def10_head, self.re_def10_tail, self.re_def10_last, '10', stext, definitions)
            if not changed:
                # Avoid matches with e.g. 'Ambtenaren belast met de grensbewaking'
                definitions, changed = self.getMultipartMatch(id, self.re_def9_head, self.re_def9_tail, None, '9', stext, definitions)
                definitions, changed = self.getMultipartMatch(id, self.re_def9a_head, self.re_def9a_tail, None, '9a', stext, definitions)


            if not changed :
                definitions, changed = self.getMultipartMatch(id, self.re_def11_head, self.re_def11_tail, None, '11', stext, definitions)
            definitions, changed = self.getMultipartMatch(id, self.re_def12_head, self.re_def12_tail, None, '12', stext, definitions)
            definitions, changed = self.getMatch(id, self.re_def13, '13', stext, definitions)
            definitions, changed = self.getMultipartMatchTermHead(id, self.re_def14_term_head, self.re_def14_short_tail, '14', stext, definitions)
            definitions, changed = self.getMultipartMatchTermHead(id, self.re_def14a_term_head, self.re_def14a_short_tail, '14a', stext, definitions)
            definitions, changed = self.getMatch(id, self.re_def15, '15', stext, definitions)

        

        for (id, num, scope, term, mod, definition, stext) in definitions :
            print "---\nID:    {}\nType:  {}\nScope: {}\nTerm:  {}\nMod:   {}\nDef:   {}\nText:  {}".format(id.encode('UTF-8'), num.encode('UTF-8'), scope.encode('UTF-8'), term.encode('UTF-8'), mod.encode('UTF-8'), definition.encode('UTF-8'), stext.encode('UTF-8'))
        
                   
        return definitions
    