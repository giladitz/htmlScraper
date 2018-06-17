from html.parser import HTMLParser
import urllib.request as urllib2

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

    keysIteratorList = ['title',       # the title
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

    def handle_starttag(self, tag, attrs):
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
            

    def dictionaryAppendTo(self, data):
        if(data.startswith(' ')):
            key = self.dictionaryTraceLast(self.keysIterator)
            if(key != 'na'):
                # pass the found key to the add to last function to complete the cncatenating
                self.dictionaryAddToLast(key, data)
            return
        if(self.keysIterator < len(self.keysIteratorList)):
            if self.keysIteratorList[self.keysIterator] == 'add to last':
                # get the lst non 'add to last' key
                key = self.dictionaryTraceLast(self.keysIterator)
                if(key != 'na'):
                    # pass the found key to the add to last function to complete the cncatenating
                    self.dictionaryAddToLast(key, data)
            elif self.keysIteratorList[self.keysIterator] == 'ignore':
                pass
            else:
                self.jDictionary[self.keysIteratorList[self.keysIterator]].append(data)
    
        self.keysIterator += 1


    def dictionaryAddToLast(self, key, data):
        lastItemInGivenKey = len(self.jDictionary[key]) - 1
        if lastItemInGivenKey < 0:
            lastItemInGivenKey = 0
        self.jDictionary[key][lastItemInGivenKey] += ", " + data
    

    def dictionaryTraceLast(self, index):
        # going backwards from given index-1 to index 0
        for tracebackIndex in range(index-1,-1,-1):
            if(self.keysIteratorList[tracebackIndex] != 'add to last'):
                return self.keysIteratorList[tracebackIndex]
        
        return 'na'

    def dictionaryResetAppend(self):
        self.keysIterator = 0

    def dictionaryPrint(self):
        '''
        Create a way to print lengthwise each
        dictionary key:value
        '''
        buildLengthwiseLists = list()
        for k, v in self.jDictionary.items():
            pass



print("--------=================---------")
print("Html parser::")

parser = myHTMLParser()
page = urllib2.urlopen("https://www.seek.co.nz/Firmware-engineer-jobs?sortmode=ListedDate")
parser.feed(str(page.read()))

file = open("tags_and_data.txt", 'w')

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

