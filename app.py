
import signal
import sys
from PyQt6.QtWidgets import (QApplication, QHBoxLayout, QWidget)
from framework.ui.gcode_generator import GCODEGenerator
from framework.ui import MicerView, SettingsWidget


class Micer(QWidget):
    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)

        gen = GCODEGenerator()

        self.setWindowTitle('Micer')

        layout = QHBoxLayout()
        m_view = MicerView(gen)

        layout.addWidget(m_view, 5)
        layout.addWidget(SettingsWidget(gen, m_view), 1)
        self.setLayout(layout)


if __name__ == '__main__':
    # Kills with Control + C
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication([])
    micer = Micer()
    micer.showMaximized()
    sys.exit(app.exec())
