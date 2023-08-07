import pyqtgraph.opengl as gl
from PyQt6.QtGui import QVector3D

from framework.ui.gcode_generator import GCODEGenerator


class MicerView(gl.GLViewWidget):

    def __init__(self, gen: GCODEGenerator):
        super(MicerView, self).__init__()

        self.gen = gen

        self.scale: float = 0.01

        self.bed_x: float = gen.args.x_bed_size
        self.bed_y: float = gen.args.y_bed_size
        self.bed_z: float = gen.args.z_bed_size

        bed_vector: QVector3D = QVector3D(self.bed_x, self.bed_y, self.bed_z)*self.scale

        grid = gl.GLGridItem(bed_vector)
        grid.translate((-bed_vector.x()/2), (bed_vector.y()/2), 0)
        grid.scale(-1, 1, 1)
        self.addItem(grid)

        axis = gl.GLAxisItem(bed_vector)
        axis.scale(-1, 1, 1)
        self.addItem(axis)

        self.box = gl.GLBoxItem(QVector3D(0, 0, 0), glOptions='opaque')
        self.box.rotate(90, 0, 0, 1)
        self.addItem(self.box)

    def reset_box(self):
        x_corner = y_corner = 0
        if self.gen.args.x_corner is not None:
            x_corner = self.gen.args.x_corner

        if self.gen.args.y_corner is not None:
            y_corner = self.gen.args.y_corner

        self.box.translate(x_corner*self.scale,
                           -y_corner*self.scale, 0)
        self.box.update()

    def update_vol(self):
        x = y = z = x_corner = y_corner = 0

        if self.gen.args.x_size is not None:
            x = self.gen.args.x_size

        if self.gen.args.y_size is not None:
            y = self.gen.args.y_size

        if self.gen.args.z_size is not None:
            z = self.gen.args.z_size

        if self.gen.args.x_corner is not None:
            x_corner = self.gen.args.x_corner

        if self.gen.args.y_corner is not None:
            y_corner = self.gen.args.y_corner

        self.box.setSize(x*self.scale, y*self.scale, z*self.scale)
        self.box.translate(-x_corner*self.scale,
                           y_corner*self.scale, 0)
        self.box.update()
