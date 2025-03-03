
import json
from PySide6.QtWidgets import QWidget, QApplication, QGroupBox, QLabel, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QFormLayout, QStyle, QMainWindow, QFileDialog, QMessageBox, QComboBox, QListWidget, QListWidgetItem, QTableWidget, QDialogButtonBox
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import QThread, Signal

import boto3
from botocore.exceptions import ClientError

from .anime_player import AnimePlayer, Threaded
from .utils import *

class BotoWidget(QWidget):
    def __init__(self, window, args, profile=None):
        super(BotoWidget, self).__init__()
        self.debug = args.debug
        self.state = None
        self.window = window
        self.profile = profile
        self.s3 = self.s3_init()
        self.buckets = []
        self.bucket = None
        self.prepareGUI()
        if self.debug: print(f"BotoWidget: Profile: {profile}")
        self.get_buckets()

    def prepareGUI(self):
        gbox = QGroupBox(f"S3 remote profile \"{self.profile['remote_name']}\" on {self.profile['endpoint']}", parent=self)
        self.spinner_buckets = AnimePlayer('./images/spinner.gif',"Tit",parent=self)
        self.spinner_buckets.hide()
        self.bucket_label = QLabel(f"Selected bucket: {self.bucket}")
        self.buckets_label = QLabel("Available buckets:")
        self.buckets_combo = QListWidget()
        self.buckets_combo.addItems([])
        self.buckets_combo.currentItemChanged.connect(self.set_selected_bucket)

        self.new_bucket_edit = QLineEdit("")
        self.new_bucket_edit.setToolTip("New bucket name")
        self.new_bucket_edit.setPlaceholderText("New bucket name")
        v1 = QRegularExpressionValidator(r"^[-a-zA-Z0-9._]{1,63}$", self)
        self.new_bucket_edit.setValidator(v1)
        self.new_bucket_edit.returnPressed.connect(self.create_bucket)
        create_bucket_button = QPushButton("Create bucket")
        create_bucket_button.clicked.connect(self.create_bucket)
        delete_bucket_button = QPushButton("Delete bucket")
        delete_bucket_button.clicked.connect(self.delete_bucket)
        layout = QFormLayout()
        layout.addRow(self.new_bucket_edit, create_bucket_button)
        layout.addRow(self.bucket_label, delete_bucket_button)
        layout.addRow(self.buckets_label, self.spinner_buckets)
        layout.addRow(self.buckets_combo)
        gbox.setLayout(layout)
        win_layout = QVBoxLayout()
        for gbox in (gbox,):
            win_layout.addWidget(gbox)
        self.setLayout(win_layout)
        self.window.open_action.setEnabled(False)
        self.window.config_action.setEnabled(True)
        self.window.s3_action.setEnabled(False)

    def s3_init(self):
        s3 = boto3.client(service_name="s3",
            aws_access_key_id=self.profile['access_key_id'],
            aws_secret_access_key=self.profile['secret_access_key'],
            #+"X",
            endpoint_url='https://'+self.profile['endpoint'],
            region_name='ceph')
        return s3

    def set_selected_bucket(self, bucket=None):
        if isinstance(bucket, QListWidgetItem):
            self.bucket = self.buckets_combo.currentItem().text()
        else:
            self.bucket = bucket
        if self.debug: print(f"itemText: {self.bucket}")
        self.bucket_label.setText(f"Selected bucket: {self.bucket}")

    def get_buckets(self):
        class XThreaded(Threaded):
            def th_init(self):
                self.widget.spinner_buckets.show()
            def th_run(self):
                r =  self.widget.s3.list_buckets()
                self.widget.buckets = [b['Name'] for b in r['Buckets']]
                if self.widget.debug: print(json.dumps(r['Buckets'], indent=2, sort_keys=True, default=str))
            def th_ready(self):
                if self.widget.debug: print("get_buckets thread ready")
                self.widget.spinner_buckets.hide()
                self.widget.buckets_label.setText("Available buckets:")
                self.widget.buckets_combo.clear()
                self.widget.buckets_combo.addItems(self.widget.buckets)
            def th_error(self, errmsg):
                self.widget.spinner_buckets.hide()
                Warning(title="Warning", text=errmsg, icon=QMessageBox.Warning).exec()
        r = XThreaded(self)

    def create_bucket(self):
        class XThreaded(Threaded):
            def th_init(self):
                self.widget.new_bucket = self.widget.new_bucket_edit.text()
                if not isinstance(self.widget.new_bucket, str) or self.widget.new_bucket=="":
                    if self.widget.debug: print(self.widget.new_bucket, type(self.widget.new_bucket))
                    Warning(title="Warning", text=f"Wrong bucket name ({self.widget.new_bucket})", icon=QMessageBox.Warning).exec()
                    return False
                if self.widget.debug: print(f"create_bucket \"{self.widget.new_bucket}\"")
                self.widget.spinner_buckets.show()
                self.widget.buckets_label.setText("Creating new bucket ...")
            def th_run(self):
                r =  self.widget.s3.create_bucket(Bucket=self.widget.new_bucket)
                if self.widget.debug: print(r)
            def th_ready(self):
                self.widget.set_selected_bucket(self.widget.new_bucket)
                self.widget.new_bucket = None
                if self.widget.debug: print("create_bucket thread ready")
                self.widget.new_bucket_edit.setText("")
                self.widget.get_buckets()
                self.widget.set_selected_bucket(self.widget.bucket)
            def th_error(self, errmsg):
                self.widget.spinner_buckets.hide()
                Warning(title="Warning", text=errmsg, icon=QMessageBox.Warning).exec()
        r = XThreaded(self)

    def delete_bucket(self):
        class XThreaded(Threaded):
            def th_init(self):
                if not isinstance(self.widget.bucket, str):
                    Warning(title="Warning", text="Wrong bucket", icon=QMessageBox.Warning).exec()
                    return False
                if not Confirm(self.widget, f"Really delete bucket \"{self.widget.bucket}\"").exec():
                    if self.widget.debug: print("Cancelled...")
                    return False
                if self.widget.debug: print(f"delete_bucket \"{self.widget.bucket}\"")
                self.widget.spinner_buckets.show()
                self.widget.buckets_label.setText("Deleting bucket ...")
            def th_run(self):
                r =  self.widget.s3.delete_bucket(Bucket=self.widget.bucket)
                if self.widget.debug: print(r)
            def th_ready(self):
                self.widget.set_selected_bucket()
                if self.widget.debug: print(f"delete_bucket thread ready")
                self.widget.get_buckets()
                self.widget.set_selected_bucket()
            def th_error(self, errmsg):
                self.widget.spinner_buckets.hide()
                Warning(title="Warning", text=errmsg, icon=QMessageBox.Warning).exec()
        r = XThreaded(self)

    def _switch_widgets(self):
        if self.debug: print("BotoWidget._switch_widgets")
        self.window.set_MainWidget()

