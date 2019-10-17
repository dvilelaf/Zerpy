from Controller import Controller
from ConfigManager import ConfigManager
import sys
import threading
import re
import argparse
from TransactionsWidget import TransactionsWidget
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QPalette, QColor, QIcon
from PyQt5.QtWidgets import (QLabel, QMessageBox, QWidget, QPushButton, QVBoxLayout,
                             QHBoxLayout, QComboBox, QMenu, QApplication)


class MainWindow(QWidget):
    ''' Main UI Window
    '''
    newDataSignal = pyqtSignal()
    refreshSignal = pyqtSignal()

    def __init__(self, config):
        super().__init__()
        self.controller = Controller(config)
        self.initUI()

    def initUI(self):
        # Window size and title
        self.setWindowTitle('Zerpy')
        self.resize(750, 700)
        self.setMinimumWidth(700)
        self.setWindowIcon(QIcon('./images/zerpy.png'))

        # Address label
        addressLabel = QLabel('Address')
        addressLabel.setAlignment(Qt.AlignCenter)

        # Address dropdown
        self.addressDropdown = QComboBox(self)
        for address in self.controller.config.data['accounts']:
            item = address
            if 'alias' in self.controller.config.data['accounts'][address]:
                item += f"  ({self.controller.config.data['accounts'][address]['alias']})"
            self.addressDropdown.addItem(item)
        self.addressDropdown.setCurrentText(self.controller.activeAccount)
        self.addressDropdown.activated.connect(self.on_dropdown_change)
        self.addressDropdown.setContextMenuPolicy(Qt.CustomContextMenu)
        self.addressDropdown.customContextMenuRequested.connect(self.on_dropdown_context_menu)

        # Refresh button
        self.refreshButton = QPushButton()
        self.refreshButton.setMaximumSize(40, 40)
        refreshIcon = QIcon.fromTheme("view-refresh")
        self.refreshButton.setIcon(refreshIcon)
        self.refreshButton.setIconSize(QSize(24,24))
        self.refreshButton.clicked.connect(self.refresh_data)
        self.refreshButton.setToolTip('Refresh balance and transactions')

        # Address layout
        addressLayout = QHBoxLayout()
        addressLayout.addWidget(addressLabel, 1)
        addressLayout.addWidget(self.addressDropdown, 7)
        addressLayout.addWidget(self.refreshButton)

        # Transactions widget
        self.transactionsWidget = TransactionsWidget(self.controller, self.refreshSignal)

        # Window layout
        windowLayout = QVBoxLayout()
        windowLayout.addLayout(addressLayout)
        windowLayout.addWidget(self.transactionsWidget)
        self.setLayout(windowLayout)

        # New data signal
        self.newDataSignal.connect(self.transactionsWidget.on_new_data)
        self.newDataSignal.connect(self.transactionsWidget.switchWidget)
        self.newDataSignal.connect(lambda: self.refreshButton.setDisabled(False))
        self.newDataSignal.connect(lambda: self.addressDropdown.setDisabled(False))

        # Refresh signal
        self.refreshSignal.connect(self.refresh_data)

    def update(self):
        self.controller.update()
        self.newDataSignal.emit()

    def refresh_data(self):
        self.refreshButton.setDisabled(True)
        self.addressDropdown.setDisabled(True)
        self.transactionsWidget.switchWidget()
        threading.Thread(target=self.update, daemon=True).start()

    def on_dropdown_change(self):
        address = str(self.addressDropdown.currentText())
        address = re.sub(r'\s*\(.*\)', '', address)  # Remove alias
        self.controller.setActiveAccount(address)
        self.refresh_data()

    def on_dropdown_context_menu(self, event):
        menu = QMenu(self)
        copyAddressAction = menu.addAction('Copy account address')
        action = menu.exec_(self.mapToGlobal(event))

        if action == copyAddressAction:
            address = self.controller.activeAccount
            QApplication.clipboard().setText(address)


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
