from PyQt5.QtWidgets import QMessageBox, QApplication
import sys

icons = {'warning': QMessageBox.Warning,
         'critical': QMessageBox.Critical,
         'info': QMessageBox.Information}

def showMessageBox(title: str, text: str, kind: str='warning'):

    app = QApplication(sys.argv)
    messageBox = QMessageBox()
    messageBox.setWindowTitle(title)
    messageBox.setText(text)
    messageBox.setIcon(icons[kind])
    messageBox.setStandardButtons(QMessageBox.Ok)
    messageBox.exec_()
    messageBox.show()