
import signal
import sys
import yaml
import logging
import pyqtgraph.opengl as gl
from PyQt6.QtGui import QDoubleValidator, QVector3D
from PyQt6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QLayout,
                             QLineEdit, QMessageBox, QPushButton, QVBoxLayout,
                             QWidget, QComboBox)


from typing import Callable
from gcode_generator import GCODEGenerator, InfillType


class Micer(QWidget):
    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)

        gen = GCODEGenerator()

        self.setWindowTitle('Micer')

        layout = QHBoxLayout()

        m_view = MicerView(gen)

        layout.addWidget(m_view)
        layout.addWidget(ButtonsWidget(gen, m_view))
        self.setLayout(layout)

def read_settings_from_yaml() -> dict:
    """Reads the settings the yaml config at app.yaml.
    """
    # Read YAML to initialize settings
    with open("app.yaml", "r", encoding="utf-8") as stream:
        try:
            settings = yaml.safe_load(stream)
            logging.info("loaded settings: %s", settings)
            return settings
        except yaml.YAMLError as exc:
            logging.error(exc)


def write_settings_to_yaml(key: str, value):
    """Write the settings to the yaml config at app.yaml
    """
    # Doing this through a single pass with "r+" permission does not work...
    # It'll end up appending the updated contents to the yaml instead of
    # overwriting.
    settings = read_settings_from_yaml()
    settings[key] = value
    with open("app.yaml", "w", encoding="utf-8") as stream:
        try:
            logging.info("wrote settings: %s", settings)
            yaml.safe_dump(settings, stream, sort_keys=False)
        except yaml.YAMLError as exc:
            logging.error(exc)

def label_to_yaml_property(name: str) -> str:
    return "_".join(name.lower().split(" "))

class ButtonsWidget(QWidget):
    class QLineEditNum(QLineEdit):
        def __init__(self, name: str, func: Callable[[float], None], m_view: 'MicerView'):
            super(QWidget, self).__init__()
            self.func = func
            self.m_view = m_view
            self.name = name

        def update_value(self):
            if self.text() == '':
                self.func(0)
            elif self.text() == '-':
                self.func(0)
            else:
                self.m_view.reset_box()
                print(self.name, self.text())
                self.func(float(self.text()))
                write_settings_to_yaml(key=label_to_yaml_property(self.name), value=float(self.text()))
                self.m_view.update_vol()

    def __init__(self, gen: GCODEGenerator, m_view: 'MicerView'):
        super(QWidget, self).__init__()

        logging.getLogger().setLevel(level=logging.INFO)

        self.gen = gen
        button_layout = QVBoxLayout()
        button_layout.setSizeConstraint(QLayout.SizeConstraint.SetMaximumSize)
        BUTTON_SIZE = 150

        names = ["X Volume", "Y Volume", "Z Volume", "X Corner", "Y Corner"]
        funcs: list[Callable[[float], None]] = [gen.set_x,
                                                gen.set_y,
                                                gen.set_z,
                                                gen.set_x_corner,
                                                gen.set_y_corner]
        settings = read_settings_from_yaml()
        if settings is None:
            raise ValueError("Settings should not be None")
        
        for i in range(len(names)):
            label = QLabel(names[i])
            label.setMaximumWidth(BUTTON_SIZE)
            button_layout.addWidget(label)

            line_edit = self.QLineEditNum(names[i], funcs[i], m_view)
            line_edit.setMaximumWidth(BUTTON_SIZE)
            line_edit.setValidator(QDoubleValidator())
            line_edit.textChanged.connect(line_edit.update_value)
            button_layout.addWidget(line_edit)
            
            # Load settings from yaml settings
            converted_yaml_property = label_to_yaml_property(names[i])
            settings_val = settings[converted_yaml_property]
            logging.info("name: %s, yaml property: %s, value: %f", names[i], converted_yaml_property, settings_val)
            line_edit.setText(str(settings_val))

        self.infill_list = QComboBox()
        for infill in InfillType:
            self.infill_list.addItem(infill.name)
        self.infill_list.currentIndexChanged.connect(self.update_infill_type)
        button_layout.addWidget(self.infill_list)

        button = QPushButton()
        button.setText("Create and Upload to Duet")
        button.clicked.connect(self.create_and_upload)
        button_layout.addWidget(button)

        self.setLayout(button_layout)

    def update_infill_type(self):
        self.gen.set_infill_type(InfillType(self.infill_list.currentIndex()))

    def create_and_upload(self):
        try:
            self.gen.run()
            # TODO add some feedback about it working
            self.gen.upload()
        except ValueError as e:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Unset Values")
            msg.setText(e.__str__())
            msg.layout().setColumnMinimumWidth(1, 50)
            msg.exec()


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
        grid.translate((bed_vector.x()/2), (bed_vector.y()/2), 0)

        self.addItem(grid)
        axis = gl.GLAxisItem(bed_vector)
        self.addItem(axis)
        self.box = gl.GLBoxItem(QVector3D(0, 0, 0), glOptions='opaque')
        self.addItem(self.box)

    def reset_box(self):
        x_corner = y_corner = 0
        if self.gen.args.x_corner is not None:
            x_corner = self.gen.args.x_corner

        if self.gen.args.y_corner is not None:
            y_corner = self.gen.args.y_corner

        self.box.translate(-x_corner*self.scale,
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
        self.box.translate(x_corner*self.scale,
                           y_corner*self.scale, 0)
        self.box.update()


if __name__ == '__main__':
    # Kills with Control + C
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication([])
    micer = Micer()
    micer.showMaximized()
    sys.exit(app.exec())
