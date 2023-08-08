import pyqtgraph.opengl as gl
from PyQt6.QtGui import QVector3D

from framework.ui.gcode_generator import GCODEGenerator


class MicerView(gl.GLViewWidget):

    def __init__(self, gen: GCODEGenerator):
        super(MicerView, self).__init__()

        self.gen = gen

        self.scale: float = 0.01

        bed_x: float = gen.args.x_bed_size
        bed_y: float = gen.args.y_bed_size
        bed_z: float = gen.args.z_bed_size

        bed_vector: QVector3D = QVector3D(bed_y, bed_x, bed_z)*self.scale
        print("bed vector: ", bed_vector)
        self.grid = gl.GLGridItem(bed_vector)
        self.grid.translate((bed_vector.x()/2), (bed_vector.y()/2), 0)
        self.addItem(self.grid)

        self.axis = gl.GLAxisItem(bed_vector)
        self.addItem(self.axis)

        self.box = gl.GLBoxItem(QVector3D(0, 0, 0), glOptions='opaque')
        self.addItem(self.box)

    # TODO currently grid and axis don't update when bed volume changes they should
    def update_bed(self):
        self.bed_x: float = self.gen.args.x_bed_size
        self.bed_y: float = self.gen.args.y_bed_size
        self.bed_z: float = self.gen.args.z_bed_size
        bed_vector: QVector3D = QVector3D(self.bed_x, self.bed_y, self.bed_z)*\
            self.scale

        # You MUST reset the grid transform or else the grid translation
        # will shoot it into outerspace. 
        self.grid.resetTransform()
        self.grid.setSize(size=bed_vector)
        # This is necessary for keeping the grid anchored to the axis origin
        self.grid.translate((bed_vector.x()/2), (bed_vector.y()/2), 0)
        self.axis.setSize(size=bed_vector)

        self.axis.update()
        self.grid.update()

    def reset_box(self):
        x_corner = y_corner = 0
        if self.gen.args.x_corner is not None:
            x_corner = self.gen.args.x_corner

        if self.gen.args.y_corner is not None:
            y_corner = self.gen.args.y_corner

        self.box.translate(-y_corner*self.scale,
                           -x_corner*self.scale, 0)
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

        self.box.setSize(y*self.scale, x*self.scale, z*self.scale)
        self.box.translate(y_corner*self.scale,
                           x_corner*self.scale, 0)
        self.box.update()
