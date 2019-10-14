from xrpApiWrapper import XRPAPI
import webbrowser
from datetime import datetime
from dateutil import tz


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
        self.account_info = self.api.get_account_info(self.activeAccount)
        self.transactions = self.api.get_account_transactions(self.activeAccount)

    def sendPayment(self, amount: float, destination_account: str, destination_tag: str) -> dict:
        api_key = self.config.data['accounts'][self.activeAccount]['apiKey']
        payment = self.api.submit_payment(source_address=self.activeAccount,
                                          destination_address=destination_account,
                                          source_tag='',
                                          destination_tag=destination_tag,
                                          amount=amount, api_key=api_key)
        result = {'status': 'ok'}
        if payment['status'] == 'error':
            result['status'] = 'error'
            result['message'] = self.api.get_error_message(payment)
        return result

    def getBalance(self):
        balance = float(self.account_info['account_data']['Balance'])
        return f'{balance / 1e6:.6f}'

    def getFormattedTransactions(self):
        data = []
        for tx in self.transactions['transactions']:
            if tx['outcome']['result'] == 'tesSUCCESS':
                amount = float(tx['outcome']['deliveredAmount']['value'])
                UTCtimeStamp = datetime.strptime(tx['outcome']['timestamp'],
                                                 '%Y-%m-%dT%H:%M:%S.000Z')
                UTCtimeStamp = UTCtimeStamp.replace(tzinfo=tz.tzutc())
                localTimeStamp = UTCtimeStamp.astimezone(tz.tzlocal())
                timeStampStr = localTimeStamp.strftime('%Y-%m-%d %H:%M:%S')
                if tx['specification']['source']['address'] == self.activeAccount:
                    icon = '\N{Wide-Headed Upwards Heavy Barb Arrow}'
                    address = tx['specification']['destination']['address']
                    amount = -amount
                else:
                    icon = '\N{Wide-Headed Downwards Heavy Barb Arrow}'
                    address = tx['specification']['source']['address']

                data.append(f'{icon} {amount: >+16.6f} XRP      {address}      {timeStampStr}')

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
