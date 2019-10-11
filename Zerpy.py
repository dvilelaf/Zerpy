from Controller import Controller
from ConfigManager import ConfigManager
import sys
import argparse
from PyQt5.QtCore import Qt, QSize, QRegExp
from PyQt5.QtGui import QPalette, QColor, QFont, QIcon, \
                        QValidator, QDoubleValidator, QRegExpValidator
from PyQt5.QtWidgets import QLabel, QMessageBox, QLineEdit, QWidget, \
                            QPushButton, QVBoxLayout, QHBoxLayout, QComboBox, \
                            QTableWidget, QHeaderView, QTableWidgetItem, QMenu, QApplication


class MainWindow(QWidget):
    ''' Main UI Window
    '''
    def __init__(self, config):
        super().__init__()
        self.controller = Controller(config)
        self.initUI()

    def initUI(self):
        # Window size and title
        self.setWindowTitle('Zerpy')
        self.resize(700, 700)
        self.setMinimumWidth(700)

        # Address label
        addressLabel = QLabel('Address')
        addressLabel.setAlignment(Qt.AlignCenter)

        # Address dropdown
        self.addressDropdown = QComboBox(self)
        for address in self.controller.config.data['accounts']:
            self.addressDropdown.addItem(address)
        self.addressDropdown.setCurrentText(self.controller.activeAccount)
        self.addressDropdown.activated.connect(self.on_dropdown_change)
        self.addressDropdown.setContextMenuPolicy(Qt.CustomContextMenu)
        self.addressDropdown.customContextMenuRequested.connect(self.on_dropdown_context_menu)

        # Refresh button
        refreshButton = QPushButton()
        refreshButton.setMaximumSize(40, 40)
        refreshIcon = QIcon.fromTheme("view-refresh")
        refreshButton.setIcon(refreshIcon)
        refreshButton.setIconSize(QSize(24,24))
        refreshButton.clicked.connect(self.refreshUI)
        refreshButton.setToolTip('Refresh balance and transactions')

        # Address layout
        addressayout = QHBoxLayout()
        addressayout.addWidget(addressLabel, 1)
        addressayout.addWidget(self.addressDropdown, 7)
        addressayout.addWidget(refreshButton)

        # Balance label
        balaceLabel = QLabel()
        balaceLabel.setText('Balance')
        balaceLabel.setAlignment(Qt.AlignCenter)

        # Balance amount label
        self.balaceAmountLabel = QLabel()
        self.balaceAmountLabel.setText(f'{self.controller.getBalance()} XRP')
        self.balaceAmountLabel.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(20)
        self.balaceAmountLabel.setFont(font)

        # Balance layout
        balanceLayout = QVBoxLayout()
        balanceLayout.addWidget(balaceLabel)
        balanceLayout.addWidget(self.balaceAmountLabel)
        balanceLayout.setContentsMargins(0, 10, 0, 10)

        # Transactions label
        transactionsLabel = QLabel('Transactions')
        transactionsLabel.setAlignment(Qt.AlignCenter)

        # Transactions table
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(1)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.horizontalHeader().setVisible(False)
        self.tableWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.populateTable()
        monofont = QFont()
        monofont.setFamily("Courier New");
        monofont.setPointSize(10)
        self.tableWidget.setFont(monofont)

        # Transactions layout
        transactionsLayout = QVBoxLayout()
        transactionsLayout.addWidget(transactionsLabel)
        transactionsLayout.addWidget(self.tableWidget)

        # Send label A
        sendLabelA = QLabel('Send')
        sendLabelA.setAlignment(Qt.AlignCenter)

        # Send amount
        self.sendAmount = QLineEdit()
        self.sendAmount.setAlignment(Qt.AlignCenter)
        self.sendAmount.setFont(monofont)
        validator = QRegExpValidator(QRegExp('^[0-9]+\.?[0-9]{0,6}$'))
        self.sendAmount.setValidator(validator)
        self.sendAmount.textChanged.connect(self.check_state)
        self.sendAmount.textChanged.emit(self.sendAmount.text())

        # Send label B
        sendLabelB = QLabel('XRP to')
        sendLabelB.setAlignment(Qt.AlignCenter)

        # Send address
        self.sendAddress = QLineEdit()
        self.sendAddress.setAlignment(Qt.AlignCenter)
        self.sendAddress.setFont(monofont)
        validator = QRegExpValidator(QRegExp('^r[A-HJ-NP-Za-km-z1-9]{24,34}$'))
        self.sendAddress.setValidator(validator)
        self.sendAddress.textChanged.connect(self.check_state)
        self.sendAddress.textChanged.emit(self.sendAmount.text())

        # Send button
        sendButton = QPushButton()
        sendButton.setMaximumSize(40, 40)
        sendIcon = QIcon.fromTheme("mail-send")
        sendButton.setIcon(sendIcon)
        sendButton.setIconSize(QSize(24,24))
        sendButton.clicked.connect(self.on_send_clicked)

        # Send layout
        sendLayout = QHBoxLayout()
        sendLayout.addWidget(sendLabelA)
        sendLayout.addWidget(self.sendAmount, 2)
        sendLayout.addWidget(sendLabelB)
        sendLayout.addWidget(self.sendAddress, 4)
        sendLayout.addWidget(sendButton)

        # Window layout
        layout = QVBoxLayout()
        layout.addLayout(addressayout)
        layout.addLayout(balanceLayout)
        layout.addLayout(transactionsLayout)
        layout.addLayout(sendLayout)
        self.setLayout(layout)

    def refreshUI(self):
        result = self.controller.update()
        if result['status'] == 'ok':
            self.balaceAmountLabel.setText(f'{self.controller.getBalance()} XRP')
            self.populateTable()
        else:
            confirmAlert = QMessageBox()
            confirmAlert.setWindowTitle('Something went wrong')
            confirmAlert.setText(result['message'])
            confirmAlert.setIcon(QMessageBox.Critical)
            confirmAlert.setStandardButtons(QMessageBox.Ok)
            confirmAlert.exec_()
            
    def on_dropdown_change(self):
        address = str(self.addressDropdown.currentText())
        self.controller.setActiveAccount(address)
        self.refreshUI()

    def on_send_clicked(self):
        confirmAlert = QMessageBox()
        confirmAlert.setWindowTitle('Send payment')
        confirmAlert.setText(f'You are about to send {self.sendAmount.text()} XRP to\n{self.sendAddress.text()}\nContinue?')
        confirmAlert.setIcon(QMessageBox.Warning)
        confirmAlert.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
        result = confirmAlert.exec_()

        if result == QMessageBox.Ok:
            payment = self.controller.sendPayment(self.sendAmount.text(), self.sendAddress.text())
            alert = QMessageBox()
            alert.setWindowTitle('Send payment')
            if payment['status'] == 'ok':
                alert.setText('Payment sent!')
                alert.setIcon(QMessageBox.Information)
            else:
                alert.setWindowTitle('Something went wrong')
                alert.setText(payment['message'])
                alert.setIcon(QMessageBox.Critical)
            alert.exec_()
            self.refreshUI()

    def populateTable(self):
        txs = self.controller.getFormattedTransactions()
        self.tableWidget.setRowCount(len(txs))

        for i in range(len(txs)):
            item = QTableWidgetItem(txs[i])
            item.setTextAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
            self.tableWidget.setItem(i, 0, item)

    def on_dropdown_context_menu(self, event):
        menu = QMenu(self)
        copyAddressAction = menu.addAction('Copy address')
        action = menu.exec_(self.mapToGlobal(event))

        if action == copyAddressAction:
            address = self.controller.activeAccount
            QApplication.clipboard().setText(address)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        openAction = menu.addAction('Open in browser')
        copyAddressAction = menu.addAction('Copy address')
        copyIDAction = menu.addAction('Copy transaction ID')
        gp = event.globalPos()
        action = menu.exec_(gp)
        vp_pos = self.tableWidget.viewport().mapFromGlobal(gp)
        row = self.tableWidget.rowAt(vp_pos.y())

        if action == openAction:
            self.controller.openTransactionInBrowser(row)
        elif action == copyAddressAction:
            txAddress = self.controller.getTxAddressByIndex(row)
            QApplication.clipboard().setText(txAddress)
        elif action == copyIDAction:
            txID = self.controller.getTxIDByIndex(row)
            QApplication.clipboard().setText(txID)

    def check_state(self, *args, **kwargs):
        sender = self.sender()
        validator = sender.validator()
        state = validator.validate(sender.text(), 0)[0]
        if state == QValidator.Acceptable:
            color = '#c4df9b' # green
        else:
            color = '#f6989d' # red
        sender.setStyleSheet('QLineEdit { color: %s }' % color)


def getPalette():
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, QColor(25, 25, 25))
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    return palette


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('configFileName', default='.secret_config.js', nargs='?',
                        help='Configuration file')
    args = parser.parse_args()
    cfg = ConfigManager.fromFile(args.configFileName)
    app = QApplication(sys.argv)
    app.setPalette(getPalette())
    window = MainWindow(cfg)
    window.show()
    app.exec_()
