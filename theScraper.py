from html.parser import HTMLParser
import urllib.request as urllib2
import yamlCollector as yamlColl
import re

class myHTMLParser(HTMLParser):
    jDictionary = {'title':[],
                    'listed time':[],
                    'company':[],
                    'type':[],
                    'location':[],
                    'area':[],
                    'classification':[],
                    'subClassification':[],
                    'information':[]
                    }

    keysIteratorList = ['title[stop at:Listed,at]',       # the title with stop mark, this will not ends in one line of with indentation
                        'listed time', # words and numbers Ex: 'Listed ten days ago, 10d ago'
                        'add to last', # the numbers of 'listed time', '10d ago' from previous line
                        'ignore',      # ignore 'at' as a general rule
                        'company',     # take the company\associate name
                        'type',        # divided between 2 lines, Ex: 'This is a \n Full Time \n job'
                        'add to last', # the last one is with indentation, meaning it is connected to the last one                    
                        'ignore',      # ignore 'location:' - the next data is a clean location text
                        'location',
                        'ignore',      # ignore 'area:' - the next data is a clean area text
                        'area',
                        'ignore',      # ignore 'classification:' - the next data is a clean classification text
                        'classification',
                        'ignore',      # ignore 'subClassification:' - the next data is a clean subClassification text
                        'subClassification',
                        'information', # more high level description - comes in 4 lines, hence:
                        'add to last',
                        'add to last',
                        'add to last',
                        ]
    keysIterator = 0

    startTags = list()
    dataList = list()
    parseThisTagPlease = False
    firstInARow = True

    def handle_starttag(self, tag, attrs):
        # in the original page 'article' tag is where we would like
        #  to look for the data - so mark the start and end of it for 
        #  the data consume methods
        if(tag == 'article'):
            self.parseThisTagPlease = True
        
        #if(self.parseThisTagPlease):
            #self.startTags.append(attrs)

    def handle_data(self, data):
        if(self.parseThisTagPlease):
            # dataList for url parsing to file (the firstt manually stage)
            self.dataList.append(data)
            self.dictionaryAppendTo(data)
    
    def handle_endtag(self, endTag):
        if(endTag == 'article'):
            self.parseThisTagPlease = False
            self.dictionaryResetAppend()
            
    
    @staticmethod
    def checkIfInstructionsInKeyString(string):
        '''
        Just check if this Key has '[...]' inside
        '''
        if '[' in string:
            if ']' in string:
                return True

    @staticmethod
    def checkForTheInstructionInKeyString(string):
        res = re.search('\[.*(:)(.*)\]', string)
        # take group 2 as the results, create a list out of it:
        #  split by ',' to a list
        splitList = res.group(2).split(",")
        # return the word that we are looking for in the instruction
        return splitList

    @staticmethod
    def getStrippedKey(keyString):
        res = re.search('(\w+)\[', keyString)
        # return the first word\s before the [...] brackets
        return res.group(1)        

    def dictionaryAppendTo(self, data):
        # option (1)
        # ' ' space at the begining means we need to concatenate it to the last string
        if(data.startswith(' ')):
            key = self.dictionaryTraceLast(self.keysIterator)
            if(key != 'na'):
                # pass the found key to the add to last function to complete the cncatenating
                self.dictionaryAddToLast(key, data, " - ")
            return
        
        # option (2)        
        # run on this data only if it is marked under the list 'keysIteratorList', or
        #  in other words, its index is smaller than the list len
        if(self.keysIterator < len(self.keysIteratorList)):
            # option (2.0)        
            # if we have instruction in this KEY
            if myHTMLParser.checkIfInstructionsInKeyString(self.keysIteratorList[self.keysIterator]):
                instructionInKey = myHTMLParser.checkForTheInstructionInKeyString(self.keysIteratorList[self.keysIterator])
                # check that any item in the key instruction is not in the current data
                # NOT WORKING!!! the 'not if' is not finding any 'Listed' for example!
                if any(itm not in data for itm in instructionInKey):
                    key = myHTMLParser.getStrippedKey(self.keysIteratorList[self.keysIterator])
                    if(self.firstInARow):
                        self.jDictionary[key].append(data)
                        self.firstInARow = False
                    else:
                        self.dictionaryAddToLast(key, data, " ")
                    return
                else:
                    self.firstInARow = True
                    self.keysIterator += 1

            # option (2.1)        
            # 'add to last' is a special item that tells us to add this data to the last
            #  data in the jDictionary - append it with the last one, so need to trace back 
            #  to find the last "real", non 'add to last' data marker
            if self.keysIteratorList[self.keysIterator] == 'add to last':
                # get the last non 'add to last' key
                key = self.dictionaryTraceLast(self.keysIterator)
                if(key != 'na'):
                    # pass the found key to the add to last function to complete the cncatenating
                    self.dictionaryAddToLast(key, data, " - ")
            # option (2.2)        
            elif self.keysIteratorList[self.keysIterator] == 'ignore':
                pass
            # option (2.3)        
            else:
                self.jDictionary[self.keysIteratorList[self.keysIterator]].append(data)
    
            self.keysIterator += 1

    
    def dictionaryAddToLast(self, key, data, separator):
        try:
            lastItemInGivenKey = len(self.jDictionary[key]) - 1
            if lastItemInGivenKey < 0:
                lastItemInGivenKey = 0
            self.jDictionary[key][lastItemInGivenKey] += separator + data
        except:
            print('ssss')
    

    def dictionaryTraceLast(self, index):
        # going backwards from given index-1 to index 0
        try:
            #print(index)
            for tracebackIndex in range(index-1,-1,-1):
                if(self.keysIteratorList[tracebackIndex] != 'add to last'):
                    return self.keysIteratorList[tracebackIndex]
        except:
            print('noooooo')
        
        return 'na'

    def dictionaryResetAppend(self):
        self.keysIterator = 0

    def dictionaryPrint(self):
        '''
        Create a way to print lengthwise each
        dictionary key:value
        '''
        csvStyleItemsList = list()
        oneLine = ''

        # go through the keys
        for k,v in self.jDictionary.items():
            oneLine += k + ", "
        
        # add their line to the head of the list
        csvStyleItemsList.append(oneLine[:-2])
        oneLine = ''

        # go through the entire dictionary: deep style
        #  and add each column to the list (as a row)
        try:
            for items in range(len(self.jDictionary['title'])):
                for k,v in self.jDictionary.items():
                    #print(v[items] + ", ")
                    oneLine += v[items] + ", "
                
                csvStyleItemsList.append(oneLine[:-2])
                oneLine = ''
                #print('-----------\n\n')
        except:
            print("out out out...")
        finally:
            csvStyleItemsList.append(oneLine[:-2])
            
        
        return csvStyleItemsList
            



print("--------=================---------")
print("Html parser::")

# collect YAML URLs
yamlObj = yamlColl.YamlCollector()
yamlObj.importConfigFile()
urlList = yamlObj.getTypeList(yamlColl.YamlCollector.TYPE_URL)

# init parser
parser = myHTMLParser()

for url in urlList:
    page = urllib2.urlopen(url)
    parser.feed(str(page.read()))
    res = re.search('\w/([a-zA-Z0-9_-]+)?', url)

    file = open(res.group(1) + ".txt", 'w')

    startTags_len = len(parser.startTags)
    dataList_len = len(parser.dataList)
    i = 0
    j = 0

    #while(i < startTags_len) & (j < dataList_len):
    while (j < dataList_len):
        #file.write(f'{parser.startTags[i]} : {parser.dataList[j]}\n')
        file.write(f'{parser.dataList[j]}\n')
        i += 1
        j += 1

file.close()

listToSavePrintOrElse = parser.dictionaryPrint()
csvFile = open("results.csv", 'w')

for item in listToSavePrintOrElse:
    csvFile.write(item + '\n')

csvFile.close()


