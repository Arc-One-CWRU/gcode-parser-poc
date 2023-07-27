
import signal
import sys

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QApplication, QPushButton
from PyQt6.QtGui import QVector3D
import pyqtgraph.opengl as gl

from gcode_generator import GCODEGenerator


class Micer(QWidget):
    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)
        self.setWindowTitle('Micer')

        layout = QHBoxLayout()
        self.setLayout(layout)

        layout.addWidget(MicerView())
        layout.addWidget(QPushButton())


class MicerView(gl.GLViewWidget):
    def __init__(self):
        super(MicerView, self).__init__()

        gen = GCODEGenerator()

        self.units: float = 0.01

        self.bed_x: float = gen.args.x_bed_size
        self.bed_y: float = gen.args.y_bed_size
        self.bed_z: float = gen.args.z_bed_size

        bed_vector: QVector3D = QVector3D(self.bed_x, self.bed_y, self.bed_z)*self.units

        grid = gl.GLGridItem(bed_vector)
        grid.translate((bed_vector.x()/2), (bed_vector.y()/2), 0)

        self.addItem(grid)
        axis = gl.GLAxisItem(bed_vector)
        self.addItem(axis)
        self.addItem(self.create_vol(50, 30, 20, 25, 76))

    def create_vol(self, x: float, y: float, z: float,
                   x_corner: float, y_corner: float) -> gl.GLBoxItem:

        print = gl.GLBoxItem(QVector3D(x, y, z)*self.units, glOptions='opaque')
        print.translate(x_corner*self.units, y_corner*self.units, 0)
        return print


if __name__ == '__main__':
    # Kills with Control + C
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication([])
    micer = Micer()
    micer.showMaximized()
    sys.exit(app.exec())
