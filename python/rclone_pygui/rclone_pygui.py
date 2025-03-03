#!/usr/bin/env python

import sys, os, json, shutil
# aux
import time
from PySide6.QtWidgets import QWidget, QApplication, QGroupBox, QLabel, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QFormLayout, QStyle, QMainWindow, QFileDialog, QMessageBox
from PySide6.QtGui import QAction, QRegularExpressionValidator, QMovie
from PySide6.QtCore import QTimer, QByteArray, Qt, QThread, Signal
from subprocess import PIPE, TimeoutExpired, Popen
from argparse import ArgumentParser
from types import SimpleNamespace
from enum import Enum

from .boto_widget import BotoWidget
from .anime_player import AnimePlayer, Threaded
from .utils import *

class MainWindow(QMainWindow):
    def __init__(self, app, args):
        super(MainWindow, self).__init__()
        self.app = app
        self.args = args
        self.create_menu()
        self.set_MainWidget()
        self._set_win_title(None, self.centralWidget().state)
        #self.setWindowIcon(QIcon('logo.png'))
        self.resize(640, 100)

    def create_menu(self):
        self.menu_bar = self.menuBar()
        # file menu:
        file_menu = self.menu_bar.addMenu('&File')
        file_menu.setMinimumWidth(200)
        file_menu.addAction((open_action := QAction("&Open config", self)))
        self.open_action = open_action
        open_action.triggered.connect(lambda : self.centralWidget()._open_dialog())
        file_menu.addAction((exit_action := QAction("E&xit", self)))
        exit_action.triggered.connect(self.quit)
        # view menu:
        view_menu = self.menu_bar.addMenu('&ViewMode')
        view_menu.setMinimumWidth(200)
        view_menu.addAction((config_action := QAction("Rclone config", self, disabled=True)))
        view_menu.addAction((s3_action := QAction("S&3 buckets", self, disabled=True)))
        config_action.triggered.connect(lambda : self.centralWidget()._switch_widgets() )
        s3_action.triggered.connect(lambda : self.centralWidget()._switch_widgets() )
        self.config_action = config_action
        self.s3_action = s3_action
        # help menu:
        help_menu = self.menu_bar.addMenu('&Help')
        help_menu.addAction((about_action := QAction("&About", self)))
        about_action.triggered.connect(lambda : Warning().exec())

    def _set_win_title(self, tit=None, state=""):
        if not tit: tit = f"rclone_config_pygui [{state}]"
        self.setWindowTitle(tit)

    def set_MainWidget(self):
        self.setCentralWidget(MainWidget(self, self.args))
        self.centralWidget().show()

    def set_BotoWidget(self, profile=None):
        self.setCentralWidget(BotoWidget(self, self.args, profile))
        self.centralWidget().show()

    def run(self):
        self.show()
        st = self.app.exec()
        sys.exit(st)

    def quit(self):
        self.app.quit()

class States(Enum):
    INIT, PWOK, BOTO, FIN = range(1,5)
    def __str__(self): return f"{self.name}"
    def debug(self): return f"{self.name}[{self.value}]"
    @classmethod
    def start_state(cls): return cls.INIT
    @classmethod
    def finish_state(cls): return cls.FIN

class MainWidget(QWidget):
    def __init__(self, window, args):
        super(MainWidget, self).__init__()
        self.debug = args.debug
        self.config_file = args.rclone_config
        self.rclone_command = args.rclone_command
        self.rclone_pygui_command = sys.argv[0]
        #
        self.remote_name = "not selected"
        self.endpoint = ""
        self.access_key_id = ""
        self.secret_access_key = ""
        self.window = window
        self.state = States.INIT
        self.profile = None
        self.prepareGUI()

    def prepareGUI(self):
        #
        self.gbox_old_pw = self._create_old_password_box()
        gbox_remote_config = self._create_remote_config_box()
        gbox_new_pw = self._create_new_password_box()
        #
        win_layout = QVBoxLayout()
        for gbox in (self.gbox_old_pw, gbox_remote_config, gbox_new_pw):
            win_layout.addWidget(gbox)
        self.setLayout(win_layout)
        self.transition_to_state_INIT()

    def _open_dialog(self):
        selected_config,_ = QFileDialog.getOpenFileName(self, 'Select rclone config ...', '.', "configs (*.conf)")
        if not selected_config: return
        if self.debug: print(f"Selected config file: {selected_config}")
        self.config_file = os.path.relpath(selected_config)
        self.gbox_old_pw.setTitle(f"Config File: {self.config_file}")
        self.transition_to_state_INIT()

    def _switch_widgets(self):
        if self.debug: print("MainWidget._switch_widgets")
        self.window.set_BotoWidget(self.profile)

    def _create_old_password_box(self):
        gbox = QGroupBox(f"Config File: {self.config_file}", parent=self)
        #
        label = QLabel("Password:")
        self.input_old_pw = QLineEdit("", parent=gbox)
        self.input_old_pw.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_old_pw.setMinimumWidth(240)
        self.input_old_pw.returnPressed.connect(self.process_button_old_pw)
        #
        self.button_old_pw = QPushButton("Enter", parent=gbox)
        self.button_old_pw.setToolTip("Check password and read config")
        self.button_old_pw.clicked.connect(self.process_button_old_pw)
        #
        self.spinner_old_pw = AnimePlayer('./images/spinner.gif',"Tit",parent=self)
        self.spinner_old_pw.hide()
#        self._set_button_icon(self.button_old_pw, 'SP_DialogOpenButton')
        # icon names and usage:
        # https://www.pythonguis.com/faq/built-in-qicons-pyqt/
        # print( sorted([attr for attr in dir(QStyle.StandardPixmap) if attr.startswith("SP_")]) )
        # SP_DialogOpenButton SP_DialogApplyButton SP_DialogCloseButton
        #
        layout = QHBoxLayout()
        for widget in (label, self.input_old_pw, self.button_old_pw, self.spinner_old_pw):
            layout.addWidget(widget)
        gbox.setLayout(layout)
        return gbox

    def _create_remote_config_box(self):
        gbox = QGroupBox(f"Remote: {self.remote_name}", parent=self)
        #
        self.input_endpoint = QLineEdit(self.endpoint)
        self.input_access_key_id = QLineEdit(self.access_key_id)
        v1 = QRegularExpressionValidator(r"[a-zA-Z0-9]+", self)
        self.input_access_key_id.setValidator(v1)
        self.input_secret_access_key = QLineEdit(self.secret_access_key)
        self.input_secret_access_key.setEchoMode(QLineEdit.EchoMode.PasswordEchoOnEdit)
        #
        layout = QFormLayout()
        for label_text, input_widget in (
            ("Endpoint:", self.input_endpoint),
            ("Access Key Id:", self.input_access_key_id),
            ("Secret Access Key:", self.input_secret_access_key),
        ):
            layout.addRow(QLabel(label_text), input_widget)
        gbox.setLayout(layout)
        self.gbox_remote_config = gbox
        return gbox

    def _create_new_password_box(self):
        gbox = QGroupBox(f"Config encryption", parent=self)
        #
        label = QLabel("Password:")
        self.input_new_pw = QLineEdit("", parent=gbox)
        self.input_new_pw.setEchoMode(QLineEdit.EchoMode.PasswordEchoOnEdit)
        self.input_new_pw.setMinimumWidth(240)
        self.input_new_pw.returnPressed.connect(self.process_button_new_pw)
        #
        self.button_new_pw = QPushButton("Enter", parent=gbox, disabled=True)
        self.button_new_pw.setToolTip("Save keys and set new password")
        self.button_new_pw.clicked.connect(self.process_button_new_pw)
        #
        self.spinner_new_pw = AnimePlayer('./images/spinner.gif',"Tit",parent=self)
        self.spinner_new_pw.hide()
        #
        layout = QHBoxLayout()
        for widget in (label, self.input_new_pw, self.button_new_pw, self.spinner_new_pw):
            layout.addWidget(widget)
        gbox.setLayout(layout)
        return gbox

    def _set_button_icon(self, button, icon_name):
        button.setIcon(self.style().standardIcon(getattr(QStyle, icon_name)))

    def process_button_old_pw(self):
        class XThreaded(Threaded):
            def th_init(self):
                self.widget.spinner_old_pw.show()
                self.widget.button_old_pw.setEnabled(False)
                self.widget._set_button_icon(self.widget.button_old_pw, 'SP_DialogCloseButton')
            def th_run(self):
                self.widget.check = self.widget.rclone_config_check(self.widget.input_old_pw.text())
            def th_ready(self):
                if self.widget.debug: print("check_result:", self.widget.check)
                if self.widget.check: self.widget.transition_to_state_PWOK(self.widget.profile)
                else:
                    Warning(title="Warning", text="Password check failed", icon=QMessageBox.Warning).exec()
                    self.widget.transition_to_state_INIT()
            def th_error(self, errmsg):
                self.widget.spinner_old_pw.hide()
                Warning(title="Warning", text=errmsg, icon=QMessageBox.Warning).exec()
        r = XThreaded(self)

    def process_button_new_pw(self):
        class XThreaded(Threaded):
            def th_init(self):
                self.widget.spinner_new_pw.show()
                self.widget.button_new_pw.setEnabled(False)
                #self.widget._set_button_icon(self.widget.button_new_pw, 'SP_DialogCloseButton')
            def th_run(self):
                data = {
                    'pw_old': self.widget.input_old_pw.text(),
                    'pw_new': self.widget.input_new_pw.text(),
                    'access_key_id': self.widget.input_access_key_id.text(),
                    'secret_access_key': self.widget.input_secret_access_key.text(),
                    'endpoint': self.widget.input_endpoint.text(),
                }
                n = SimpleNamespace(**data)
                # run rclone to change config pw:
                if n.pw_new != n.pw_old:  self.widget.rclone_change_config_pw(n.pw_old, n.pw_new)
                # run rclone to save S3 keys:
                self.widget.status = self.widget.rclone_change_keys(n.pw_new, n.endpoint, n.access_key_id, n.secret_access_key)
            def th_ready(self):
                if self.widget.debug: print("new_pw_wt_result:", self.widget.status)
                self.widget.spinner_new_pw.hide()
                self.widget.button_new_pw.setEnabled(True)
                if self.widget.status:
                    if Confirm(self.widget, f"Finished, saved - continue to bucket operations?").exec():
                        self.widget.transition_to_state_BOTO()
                    else:
                        self.widget.transition_to_state_FIN()
            def th_error(self, errmsg):
                self.widget.spinner_new_pw.hide()
                Warning(title="Warning", text=errmsg, icon=QMessageBox.Warning).exec()
        r = XThreaded(self)

    def transition_to_state_INIT(self):
        self.remote_name = "not selected"
        if self.debug: print(f"transition to state INIT")
        self.gbox_remote_config.setTitle(f"Remote {self.remote_name}")
        self.spinner_old_pw.hide()
        self.input_old_pw.setText("")
        self.input_old_pw.setEnabled(True)
        self.input_old_pw.setFocus()
        self._set_button_icon(self.button_old_pw, 'SP_DialogOpenButton')
        #  SP_DialogOpenButton SP_DialogApplyButton SP_DialogCloseButton
        self.button_old_pw.setEnabled(True)
        self.window.open_action.setEnabled(True)
        self.window.config_action.setEnabled(False)
        self.window.s3_action.setEnabled(False)
        for key in ('endpoint', 'access_key_id', 'secret_access_key'):
            setattr(self, f"{key}", "")
            getattr(self, f"input_{key}").setText(getattr(self, f"{key}"))
            getattr(self, f"input_{key}").setEnabled(False)
        self.input_new_pw.setEnabled(False)
        self._set_button_icon(self.button_new_pw, 'SP_DialogCloseButton')
        self.button_new_pw.setEnabled(False)
        self.state = States.INIT
        self.window._set_win_title(None, self.state)

    def transition_to_state_PWOK(self, profile):
        self.remote_name = profile['remote_name']
        if self.debug: print(f"transition to state PWOK {profile['remote_name']=}")
        self.gbox_remote_config.setTitle(f"Remote {self.remote_name}")
        self.input_old_pw.setEnabled(False)
        self.spinner_old_pw.hide()
        self.button_old_pw.setEnabled(False)
        for key in ('endpoint', 'access_key_id', 'secret_access_key'):
            setattr(self, f"{key}", profile[key])
            getattr(self, f"input_{key}").setText(getattr(self, f"{key}"))
            getattr(self, f"input_{key}").setEnabled(True)
        self.window.open_action.setEnabled(True)
        self.window.config_action.setEnabled(False)
        self.window.s3_action.setEnabled(True)
        self.input_new_pw.setEnabled(True)
        self._set_button_icon(self.button_new_pw, 'SP_DialogApplyButton')
        self.button_new_pw.setEnabled(True)
        self.state = States.PWOK
        self.window._set_win_title(None, self.state)

    def transition_to_state_BOTO(self):
        if self.debug: print(f"transition to state BOTO")
        self.state = States.BOTO
        self.window._set_win_title(None, self.state)
        self.window.set_BotoWidget(self.profile)

    def transition_to_state_FIN(self):
        print("Done.")
        self.quit()

    def rclone_config_check(self, config_pw):
        if self.debug: print(f"call rclone config dump")
        (st, err, out) = subprocess_call(
            self.rclone_command, ['--config', self.config_file, '--ask-password=false', 'config', 'dump'],
            self.debug,
            { 'RCLONE_CONFIG_PASS': config_pw }
        )
        if st==0:
            lines = json.loads(out)
            if self.debug: print(json.dumps(lines, indent=2))
            for remote_name, profile in lines.items():
                if profile['type'] == "s3":
                    profile['remote_name'] = remote_name
                    self.profile = profile
                    return True
        return False

    def rclone_change_config_pw(self, pw_old, pw_new):
        if self.debug: print(f"call rclone config encryption set")
        (st, err, out) = subprocess_call(
            self.rclone_command, [
                '--config', self.config_file, 'config', 'encryption', 'set', '--ask-password=false',
                '--password-command', f"{self.rclone_pygui_command} --password_command"
            ],
            self.debug,
            { 'PYGUI_RCLONE_OLDPW': pw_old, 'PYGUI_RCLONE_NEWPW': pw_new }
        )

    def rclone_change_keys(self, config_pw, endpoint, access_key_id, secret_access_key):
        if self.debug: print(f"rclone_change_keys:")
        options = {
            "endpoint": { "confval":endpoint, 'updated':False },
            "access_key_id": { "confval":access_key_id, 'updated':False },
            "secret_access_key": { "confval":secret_access_key, 'updated':False },
        }
        nextarg, rcstate, rcresult, rcconfname  = "--all", None, "", ""
        while True:
            all_options_updated = False
            for opt in [k for k in options.keys() if not options[k]['updated']]:
                if rcconfname == opt:
                    rcresult = options[opt]['confval']
                    options[opt]['updated'] = True
            if self.debug: print(f"call rclone w.nextarg: {nextarg}")
            (st, err, out) = subprocess_call(
                self.rclone_command, ['--config', self.config_file, 'config', 'update', '--non-interactive', self.remote_name, '--continue'] + [nextarg],
                self.debug,
                { 'RCLONE_CONFIG_PASS': config_pw, 'RCLONE_RESULT': rcresult }
            )
            if st != 0: raise Exception(f"Wrong status ({st}) from subprocess ({err=}).")
            jout = json.loads(out)
            if self.debug: print(json.dumps(jout, indent=2))
            rcstate = jout['State']
            # exit from while:
            if rcstate == "": break
            if len([k for k in options.keys() if not options[k]['updated']])==0: break
            #
            nextarg = f"--state={rcstate}"
            rcresult = str(jout['Option']['Default'])
            rcconfname = jout['Option']['Name']
        if self.debug: print(f"rclone_change_keys done.")
        return True

    def quit(self):
        self.window.quit()

def subprocess_call(cmd, cmd_args, debug, env=None):
    wait_timeout_s = 6
    proc = None
    try:
        if debug: print(f"subprocess call: {cmd} {cmd_args=} {env=}")
        env_copy = os.environ.copy()
        if env != None: env_copy.update(env)
        proc = Popen([cmd] + cmd_args, stdin=PIPE, stdout=PIPE, stderr=PIPE, text=True, env=env_copy, start_new_session=True)
        proc.wait(timeout = wait_timeout_s)
        out = proc.stdout.read()
        err = proc.stderr.read()
        if debug: print(out, err)
        status = proc.returncode
        return (status, err, out)
    except TimeoutExpired as e:
        status, err = 255, 'timeout'
        return (status, err, '')
    finally:
        if proc:
            proc.stdin.close()
            proc.terminate()
            if debug: print(f"-->subprocess call finnished: {cmd} {cmd_args=}: {status=} {err=}")

def get_rclone_version(cmd, debug=False):
    if debug: print(f"call rclone version")
    (st, err, out) = subprocess_call(cmd, ["version"], debug)
    if st == 0: return out.split("\n")[0].replace('rclone ', '')
    else: raise Exception(f"Rclone not found ({err=})")

def fatal_err(msg, status=1):
    print(f"Fatal error: {msg}")
    sys.exit(status)

def parse_args(argv):
    p = ArgumentParser(description="CESNET S3 rclone pygui")
    p.add_argument("-d", "--debug", help="enable debug outputs (default %(default)s)", action="store_true")
    p.add_argument("-c", "--rclone_config", help="rclone config file (default: %(default)s)", default='./rclone.conf')
    p.add_argument("-r", "--rclone_command", help="rclone command, could be full path to command (default: %(default)s)", default='rclone')
    p.add_argument("-p", "--password_command", action="store_true", help="run as rclone password command, for internal use")
    return p.parse_args(argv)

def main(argv = None):
    args = parse_args(argv)
    if args.password_command:
        subproc_pw_old = os.environ.get('PYGUI_RCLONE_OLDPW', "")
        subproc_pw_new = os.environ.get('PYGUI_RCLONE_NEWPW', "")
        pwchng = os.environ.get('RCLONE_PASSWORD_CHANGE', "")
        if pwchng != "1":
            print(subproc_pw_old)
        else:
            print(subproc_pw_new)
    else:
        if not os.path.isfile(args.rclone_config): fatal_err(f"Rclone config \"{args.rclone_config}\" not found.")
        if not (rclone := shutil.which(args.rclone_command)): fatal_err(f"Rclone command \"{args.rclone_command}\" not found.")
        print(f"Using rclone command \"{rclone}\"")
# ***
#        rclone_version = get_rclone_version(rclone, args.debug)
#        print(f"rclone version: {rclone_version}")
        MainWindow(QApplication(), args).run()
#        MainWindow(QApplication(), args).show()
#        QtAsyncio.run()

if __name__ == '__main__':
    sys.exit(main())
