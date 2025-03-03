
import os.path
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtGui import QMovie
from PySide6.QtCore import QByteArray, QThread, Signal
from .utils import resource_path

class AnimePlayer(QWidget):
    def __init__(self, filename, title, parent=None):
        QWidget.__init__(self, parent)
        filepath = resource_path(filename)
        if parent.debug and not os.path.isfile(filepath): print(f"File not found: \"{filepath}\"")
        # Load the file into a QMovie
        self.movie = QMovie(filepath, QByteArray(), self)
        size = self.movie.scaledSize()
#        self.setGeometry(20, 20, size.width(), size.height())
        self.setWindowTitle(title)
        self.movie_screen = QLabel()
        # Make label fit the gif
 #       self.movie_screen.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
 #       self.movie_screen.setAlignment(Qt.AlignCenter)
        # Create the layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.movie_screen)
        self.setLayout(main_layout)
        # Add the QMovie object to the label
        self.movie.setCacheMode(QMovie.CacheAll)
        self.movie.setSpeed(100)
        self.movie_screen.setMovie(self.movie)
        self.movie.start()
    def stop(self):
        self.movie.stop()

class Threaded():
    class WorkerThread(QThread):
        ready, error = Signal(bool), Signal(bool)
        def run(self):
            #print("Thread started ...")
            try:
                self.th.th_run()
                self.ready.emit(True)
            except Exception as e:
                self.errmsg = f"{e}"
                self.error.emit(False)
        def process_ready(self, st):
            #print(f"Thread ready st={st}")
            self.th.th_ready()
        def process_error(self, st):
            #print(f"Thread error st={st}")
            self.th.th_error(self.errmsg)
    def __init__(self, widget):
        self.widget = widget
        if False == self.th_init(): return
        wt = Threaded.WorkerThread(widget)
        wt.th = self
        wt.ready.connect(wt.process_ready)
        wt.error.connect(wt.process_error)
        wt.finished.connect(wt.deleteLater)
        wt.start()
    def th_init(self):
        pass
    def th_run(self):
        pass
    def th_ready(self):
        pass
    def th_error(self, errmsg):
        raise Exception(errmsg)
