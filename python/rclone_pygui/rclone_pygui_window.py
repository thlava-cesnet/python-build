#
# Copyright (C) 2025 CESNET
#
# rclone_pygui is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

""" S3 rclone pygui window """

import sys, os, platform
from PySide6.QtWidgets import QMainWindow, QMessageBox
from PySide6.QtGui import QAction, QIcon, QShortcut, QKeySequence
from types import SimpleNamespace as nspace
import boto3

from .utils import WarningQD
from .version import __version__
from .rclone_control import Rclone_control
from .boto_widget import BotoWidget
from .rclone_pygui_lib import MainWidget

class MainWindow(QMainWindow):
    def __init__(self, qapp, args, variant="rclone_pygui"):
        super().__init__()
        self.qapp = qapp
        self.variant = variant
        self.args = args
        self.debug = args.debug
        self.min_pw_length = 3
        self.bdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.create_menu()
        self.create_stausbar()
        self.rclone_control = Rclone_control(args.debug, args.rclone_command)
        self.set_MainWidget()
        #self.create_context_menu()
        self.setWindowIcon(QIcon(os.path.join(self.bdir,'images/favicon.png')))
        self.resize(640, 100)

    def s3_client(self, access_key_id, secret_access_key, endpoint, region_name='ceph'):
        return boto3.client(service_name="s3", aws_access_key_id = access_key_id, aws_secret_access_key = secret_access_key, endpoint_url = 'https://'+endpoint, region_name=region_name)

    def create_menu(self):
        self.menu_bar = self.menuBar()
        self.menu = nspace(file=nspace(actions=nspace()), view=nspace(actions=nspace()))
        # file menu:
        file_menu = self.menu.file.obj = self.menu_bar.addMenu('&File')
        file_menu.setMinimumWidth(200)
        file_menu.addAction((open_action := QAction("&Open config", self)))
        open_action.setShortcut(QKeySequence.Open)
        self.menu.file.actions.open = open_action
        open_action.triggered.connect(lambda : self.centralWidget()._open_config_dialog())
        file_menu.addAction((exit_action := QAction("E&xit", self)))
        #exit_action.setShortcut(QKeySequence("Alt+x"))
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(lambda : self.centralWidget().quit())
        # view menu:
        view_menu = self.menu_bar.addMenu('&ViewMode')
        view_menu.setMinimumWidth(200)
        view_menu.addAction((config_action := QAction("Rclone config", self, disabled=True)))
        config_action.setShortcut(QKeySequence("Ctrl+r"))
        view_menu.addAction((s3_action := QAction("S&3 bucket manager", self, disabled=True)))
        s3_action.setShortcut(QKeySequence("Ctrl+3"))
        #s3_action.setStatusTip("S3 bucket manager")
        s3_action.setToolTip("S3 bucket manager")
        config_action.triggered.connect(lambda : self.centralWidget()._switch_widgets(self.set_MainWidget) )
        s3_action.triggered.connect(lambda : self.centralWidget()._switch_widgets(self.set_BotoWidget) )
        self.menu.view.actions.config = config_action
        self.menu.view.actions.s3 = s3_action
        # help menu:
        help_menu = self.menu_bar.addMenu('&Help')
        help_menu.addAction((about_action := QAction("&About", self)))
        about_text = f"""
        S3 {self.variant} (rclone pygui) v{__version__}
        (c) 2025 CESNET
        {platform.system()}; {platform.machine()}
        """
        about_action.triggered.connect(lambda : WarningQD(text=about_text).exec())

    def create_stausbar(self):
        self.statusbar = self.statusBar()
        #self.statusbar.addPermanentWidget(QLabel(f"abcd"))
        self.statusbar.showMessage("Ready", 2000)

    def _set_win_title(self, tit=None, state=""):
        if not tit: tit = f"{self.variant} [v{__version__}{f'; state:{state}' if self.debug else ''}]"
        self.setWindowTitle(tit)

    def set_MainWidget(self, data=None):
        self.setCentralWidget(MainWidget(self, self.args, data))
        self.centralWidget().show()

    def set_BotoWidget(self, data=None):
        try:
            s3 = self.s3_client(data.access_key_id, data.secret_access_key, data.endpoint)
            self.setCentralWidget(BotoWidget(self, self.args, s3, data))
            self.centralWidget().show()
        except Exception as e:
            WarningQD(title="Warning", text=f"{e}", icon=QMessageBox.Warning).exec()

    def _install_shortcuts(self, widget):
        QShortcut(QKeySequence("Alt+x"), widget, lambda : self.centralWidget().quit())

    def run(self):
        self.show()
        st = self.qapp.exec()
        sys.exit(st)

    def quit(self):
        self.qapp.quit()

