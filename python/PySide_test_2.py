#!/usr/bin/env python

import sys
#from PySide6 import QtGui,QtCore,QtQuick
from PySide6 import QtCore, QtGui
#from PySide6.QtWidgets import QApplication,QWidget,QLabel
from PySide6.QtWidgets import *

#QML_FILE = "01.qml"
#class MainWindow(QtQuick.QQuickView):
# 
#    def __init__(self, parent=None):
#        super(MainWindow, self).__init__(parent)
#        self.setTitle("QML Example @ PySide2")
##        self.setSource(QtCore.QUrl.fromLocalFile(QML_FILE))
#        self.setResizeMode(QtQuick.QQuickView.SizeRootObjectToView)

class MainWindow(QWidget):
    def __init__(self, app):
        super(MainWindow, self).__init__()
        self.app = app
        self.prepareGUI()
        
    def prepareGUI(self):
        self.setWindowTitle('Test1')
        self.resize(320,100)
#        label = QLabel("Enter password:", parent=self)
#        label.move(280,100)
        (button := QPushButton("Enter", parent=self)).setToolTip("Close app")
#        button.move(280,140)
        p1 = QLineEdit("", parent=self)
        self.p1 = p1
        p1.setEchoMode(QLineEdit.EchoMode.Password)
#        button.clicked.connect(QtCore.QCoreApplication.instance().quit)
#        button.clicked.connect(self.app.quit)
        button.clicked.connect(self.close)
        gb = QGroupBox("Enter password:", parent=self)
        l1 = QHBoxLayout()
        #l1.addWidget(label)
        l1.addWidget(p1)
        l1.addWidget(button)
        gb.setLayout(l1)
        
    def run(self):
        self.show()
        sys.exit(self.app.exec())

    def close(self):
        print(self.p1.text())
        self.app.quit()
    

def main():
    app = QApplication(sys.argv)
    MainWindow(app).run()
    

if __name__ == '__main__':
    main()
