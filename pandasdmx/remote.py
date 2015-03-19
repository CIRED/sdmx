# encoding: utf-8

from IPython.config.configurable import LoggingConfigurable
from IPython.utils.traitlets import Int 
import requests
from tempfile import SpooledTemporaryFile as STF
from contextlib import closing

    

class REST(LoggingConfigurable):
    """
    Query resources via REST
    """

    max_size = Int(2**24, config=True, 
                   help='max size of in-memory file before spooling to disk')
            
    def __init__(self):
        super(REST, self).__init__()
        self.name = 'pandasdmx.client.REST'
        
        
                             
    def get(self, url, fromfile = None, params = {}):
        '''
        Read file from URL or local file.
        
        Return file-like for parsing
        Raise error if file could not be obtained.
 '''
        if fromfile:
            # Load data from local file 
            source = open(fromfile, 'rb')
            final_url = status_code = None    
        else:
            self.log.debug('Requesting %s', url)
            source, final_url, status_code = self.request(url, params = params) 
        return source, final_url, status_code
         
    
    def request(self, url, params = {}):
        """
        Retrieve SDMX messages.
        If needed, override in subclasses to support other data providers.

        :param url: The URL of the message.
        :type url: str
        :return: the xml data as file-like object 
        """
        
        with closing(requests.get(url, params = params, 
                                  stream = True, timeout= 30.1)) as response:
            if response.status_code == requests.codes.OK:
                source = STF(max_size = self.max_size)
                for c in response.iter_content(chunk_size = 1000000):
                    source.write(c)
                source.seek(0)
            else:
                source = None
            return source, response.url, int(response.status_code)
