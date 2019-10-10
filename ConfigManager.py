import json
import os
import re
import sys


class ConfigManager:
    ''' This class handles the loading and saving of the configuration file
    '''
    def __init__(self, accounts: dict={},
                 server: str='wss://s.altnet.rippletest.net:51233',
                 fileName: str='.secret_config.js'):
        self.accounts = accounts
        self.server = server
        self.fileName = fileName

    @classmethod
    def fromFile(cls, fileName: str='.secret_config.js') -> 'ConfigManager':
        if os.path.isfile(fileName):
            with open(fileName, 'r') as infile:
                data = infile.read() \
                             .replace('\n', '') \
                             .replace(' ', '') \
                             .replace('module.exports=', '')
                data = re.sub(r',}', r'}', data)  # Remove unnecesary commas
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    sys.exit(f'Error: {fileName} is not a valid config file')
                if not data['accounts']:
                    raise ValueError
                return cls(data['accounts'], data['server'], fileName)
        else:
            raise FileNotFoundError

    def get_data(self):
        return {'server': self.server,
                'accounts': self.accounts,
                'fileName': self.fileName}

    data = property(get_data)

    def save(self, fileName: str=''):
        fileName = fileName if fileName else self.fileName
        with open(fileName, 'w') as outfile:
            outfile.write('module.exports = ' + json.dumps(self.data, indent=4))

    def __str__(self):
        data = {'server': self.server, 'accounts': self.accounts}
        return f'<{self.fileName}>\nmodule.exports = ' + json.dumps(data, indent=4)

    def __repr__(self):
        return 'ConfigHandler()'
