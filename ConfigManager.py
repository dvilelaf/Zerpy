import json
import os
import re
import sys
try:
    from MessageBox import showMessageBox
    MessageBoxPresent = True
except ImportError:
    MessageBoxPresent = False


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
            message = f'Configuration file "{fileName}" is not a file.'
            if MessageBoxPresent:
                showMessageBox('Error', message, 'critical')
            sys.exit('Error: ' + message)

        with open(fileName, 'r') as infile:
            data = infile.read() \
                         .replace('\n', '')

            if re.match(re.compile("^module.exports = {.*}$"), data) is None:
                message = 'Configuration file must have the format: module.exports = {...}.'
                if MessageBoxPresent:
                    showMessageBox('Error', message, 'critical')
                sys.exit('Error: ' + message)

            data = data.replace('module.exports = ', '')
            data = re.sub(r',(\s*)}', r'\1}', data)  # Remove unnecesary commas that invalidate json files
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                message = f'Configuration file "{fileName}" is not a valid json file.'
                if MessageBoxPresent:
                    showMessageBox('Error', message, 'critical')
                sys.exit('Error: ' + message)
            if 'server' not in data or 'accounts' not in data:
                message = f'Configuration file "{fileName}" must contain "server" and "accounts" entries.'
                if MessageBoxPresent:
                    showMessageBox('Error', message, 'critical')
                sys.exit('Error: ' + message)
            for i in data['accounts']:
                if 'apiKey' not in data['accounts'][i] or \
                'secret' not in data['accounts'][i]:
                    message = f'All accounts in configuration file "{fileName}" must contain "apiKey" and "secret" entries'
                    if MessageBoxPresent:
                        showMessageBox('Error', message, 'critical')
                    sys.exit('Error: ' + message)
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
