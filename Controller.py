from xrp_api import XRPAPI
import webbrowser

class Controller:
    ''' Controller contains all functions that retrieve info from the XRPL,
    configuration info and keeps track of the active account in the UI
    '''
    def __init__(self, config: dict):
        self.config = config
        self.activeAccount = list(self.config.data['accounts'].keys())[0]
        self.api = XRPAPI()
        self.update()

    def setActiveAccount(self, account: str):
        self.activeAccount = account

    def update(self):
        self.transactions = self.api.get_account_transactions(self.activeAccount)
        self.account_info = self.api.get_account_info(self.activeAccount)

    def sendPayment(self, amount: float, destination_account: str) -> dict:
        api_key = self.config.data['accounts'][self.activeAccount]['apiKey']
        return self.api.submit_payment(self.activeAccount, destination_account, amount, api_key)

    def getBalance(self):
        balance = float(self.account_info['account_data']['Balance'])
        return f'{balance / 1e6:.2f}'

    def getFormattedTransactions(self):
        data = []
        for tx in self.transactions['transactions']:
            if tx['outcome']['result'] == 'tesSUCCESS':
                amount = float(tx['outcome']['deliveredAmount']['value'])
                timeStamp = tx['outcome']['timestamp'].replace('.000Z', '').replace('T', ' ')

                if tx['specification']['source']['address'] == self.activeAccount:
                    icon = '\N{upwards black arrow}'
                    address = tx['specification']['destination']['address']
                    amount = -amount
                else:
                    icon = '\N{downwards black arrow}'
                    address = tx['specification']['source']['address']

                data.append(f'{icon} {amount: >+12.2f} XRP      {address}      {timeStamp}')

        return data

    def openTransactionInBrowser(self, i: int):
        id = self.transactions['transactions'][i]['id']
        url = f'https://test.bithomp.com/explorer/{id}'
        webbrowser.open(url)

    def getTxAddressByIndex(self, i: int):
        tx = self.transactions['transactions'][i]
        if tx['specification']['source']['address'] == self.activeAccount:
            return tx['specification']['destination']['address']
        else:
            return tx['specification']['source']['address']

    def getTxIDByIndex(self, i: int):
        return self.transactions['transactions'][i]['id']
