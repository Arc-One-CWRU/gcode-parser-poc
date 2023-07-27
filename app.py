
import signal
import sys

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QApplication, QPushButton
from PyQt6.QtGui import QVector3D
import pyqtgraph.opengl as gl
import numpy as np

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

        self.bed_x: float = gen.args.x_bed_size*self.units
        self.bed_y: float = gen.args.y_bed_size*self.units
        self.bed_z: float = gen.args.z_bed_size*self.units

        bed_vector: QVector3D = QVector3D(self.bed_x, self.bed_y, self.bed_z)

        grid = gl.GLGridItem(bed_vector)
        self.addItem(grid)
        grid.translate((bed_vector.x()/2), (bed_vector.y()/2), 0)

        self.addItem(gl.GLAxisItem(bed_vector))

    def create_vol(self, x: float, y: float, z: float,
                   x_corner: float, y_corner: float):

        vertexes = np.array([[0, 0, 0],
                             [x, 0, 0],
                             [0, y, 0],
                             [0, 0, z],
                             [x, y, 0],
                             [x, y, z],
                             [0, y, z],
                             [x, 0, z]])

        faces = np.array([[1, 0, 7], [1, 3, 7],
                            [1,2,4], [1,0,4],
                            [1,2,6], [1,3,6],
                            [0,4,5], [0,7,5],
                            [2,4,5], [2,6,5],
                            [3,6,5], [3,7,5]])
        self.addItem(gl.GLAxisItem(QtGui.QVector3D(x, y, z)))


if __name__ == '__main__':
    # Kills with Control + C
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication([])
    micer = Micer()
    micer.showMaximized()
    sys.exit(app.exec())
