
import signal
import sys

import pyqtgraph.opengl as gl
# from PyQt6.QtCore import QPoint
from PyQt6.QtGui import QDoubleValidator, QVector3D
from PyQt6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QLayout,
                             QLineEdit, QMessageBox, QPushButton, QVBoxLayout,
                             QWidget, QSpacerItem)


from gcode_generator import GCODEGenerator


class Micer(QWidget):
    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)

        gen = GCODEGenerator()

        self.setWindowTitle('Micer')

        layout = QHBoxLayout()

        layout.addWidget(MicerView(gen))
        layout.addWidget(ButtonsWidget(gen, self))
        self.setLayout(layout)


class ButtonsWidget(QWidget):
    def __init__(self, gen: GCODEGenerator, parent: Micer):
        super(QWidget, self).__init__(parent)

        self.gen = gen

        button_layout = QVBoxLayout()
        button_layout.setSizeConstraint(QLayout.SizeConstraint.SetMaximumSize)
        BUTTON_SIZE = 150

        names = ["X Volume", "Y Volume", "Z Volume", "X Corner", "Y Corner"]

        for name in names:
            label = QLabel(name)
            label.setMaximumWidth(BUTTON_SIZE)
            button_layout.addWidget(label)

            line_edit = QLineEdit()
            line_edit.setMaximumWidth(BUTTON_SIZE)
            line_edit.setValidator(QDoubleValidator())
            button_layout.addWidget(line_edit)

        button = QPushButton()
        button.setText("Create and Upload to Duet")
        button.clicked.connect(self.create_and_upload)
        button_layout.addWidget(button)

        self.setLayout(button_layout)

    def create_and_upload(self):
        try:
            self.gen.run()
            self.gen.upload()
        except ValueError as e:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Error Unset Parameters")
            msg.setText(e.__str__())
            # msg.
            msg.exec()


class MicerView(gl.GLViewWidget):
    def __init__(self, gen: GCODEGenerator):
        super(MicerView, self).__init__()

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
