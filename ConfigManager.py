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
        if not os.path.isfile(fileName):
            sys.exit(f'Error: {fileName} is not a file')

        with open(fileName, 'r') as infile:
            data = infile.read() \
                         .replace('\n', '')

            if re.match(re.compile("^module.exports = {.*}$"), data) is None:
                sys.exit('Error: configuration file must have the format: module.exports = {...}')

            data = data.replace('module.exports = ', '')
            data = re.sub(r',(\s*)}', r'\1}', data)  # Remove unnecesary commas that invalidate json files
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                sys.exit(f'Error: {fileName} is not a valid json file')
            if 'server' not in data or 'accounts' not in data:
                sys.exit('Error: configuration file must contain "server" and "accounts" entries')
            for i in data['accounts']:
                if 'apiKey' not in data['accounts'][i] or \
                'secret' not in data['accounts'][i]:
                    sys.exit('Error: all accounts in configuration file must contain "apiKey" and "secret" entries')
            return cls(data['accounts'], data['server'], fileName)


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
