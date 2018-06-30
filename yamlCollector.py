import yaml

class YamlCollector:

    # types of keys to search\retrieve
    TYPE_INVALID = 'invalid'
    TYPE_URL = 'url to scrap'

    def importConfigFile(self):
        with open('config.yaml','r') as stream:
            self.configFile = yaml.load(stream)
    
    def getTypeList(self, type):
        '''
        type is pre-defined values of this class: TYPE_
        '''
        val = self.configFile[type]
        return val
        