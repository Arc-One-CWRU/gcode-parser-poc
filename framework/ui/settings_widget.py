from typing import Callable
import logging

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtWidgets import (QLabel, QLayout,
                             QLineEdit, QMessageBox, QPushButton, QVBoxLayout,
                             QWidget, QComboBox, QTabWidget)
from framework.ui.gcode_generator import GCODEGenerator, InfillType
from framework.ui.yaml import (read_settings_from_yaml, label_to_yaml_property,
                               write_settings_to_yaml)
from framework.ui.micer_view import MicerView


class QLineEditNum(QLineEdit):
    def __init__(self, name: str, func: Callable[[float], None],
                 m_view: 'MicerView'):
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
            self.func(float(self.text()))
            write_settings_to_yaml(key=label_to_yaml_property(self.name),
                                   value=float(self.text()))
            self.m_view.update_bed()
            self.m_view.update_vol()


class ButtonsWidget(QWidget):

    def __init__(self, gen: GCODEGenerator, m_view: 'MicerView'):
        super(QWidget, self).__init__()

        logging.getLogger().setLevel(level=logging.INFO)

        self.gen: GCODEGenerator = gen
        button_layout = QVBoxLayout()
        button_layout.setSizeConstraint(QLayout.SizeConstraint.SetMaximumSize)
        button_layout.setContentsMargins(15, 0, 0, 30)
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

            line_edit = QLineEditNum(names[i], funcs[i], m_view)
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

        upload_button = QPushButton()
        upload_button.setText("Create and Upload to Duet")
        upload_button.clicked.connect(self.create_and_upload)
        button_layout.addWidget(upload_button)

        play_button = QPushButton()
        play_button.setText("Run Last Created Print")
        play_button.clicked.connect(self.gen.start_last_print)
        button_layout.addWidget(play_button)

        pause_button = QPushButton()
        pause_button.setText("Pause Current Print")
        pause_button.clicked.connect(self.gen.pause_print)
        button_layout.addWidget(pause_button)

        resume_button = QPushButton()
        resume_button.setText("Resume Current Print")
        resume_button.clicked.connect(self.gen.resume_print)
        button_layout.addWidget(resume_button)

        estop_button = QPushButton()
        estop_button.setText("ESTOP!!!")
        estop_button.clicked.connect(self.gen.e_stop)
        button_layout.addWidget(estop_button)

        self.setLayout(button_layout)

    def update_infill_type(self):
        self.gen.set_infill_type(InfillType(self.infill_list.currentIndex()))

    def create_and_upload(self):
        try:
            self.gen.run()
            self.gen.upload()

            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("Uploaded")
            msg.setText("")

            timer = QTimer()
            timer.setInterval(5000)
            timer.timeout.connect(msg.close)
            timer.start()

            msg.exec()
        except ValueError as e:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Unset Values")
            msg.setText(e.__str__())
            msg.layout().setColumnMinimumWidth(1, 50)
            msg.exec()


class AdditionalSettingsWidget(QWidget):

    def __init__(self, gen: GCODEGenerator, m_view: 'MicerView'):
        super(QWidget, self).__init__()

        logging.getLogger().setLevel(level=logging.INFO)

        self.gen: GCODEGenerator = gen
        button_layout = QVBoxLayout()
        button_layout.setSizeConstraint(QLayout.SizeConstraint.SetMaximumSize)
        button_layout.setContentsMargins(15, 0, 0, 30)
        BUTTON_SIZE = 150

        fn_mappings = {
            "Weld Gap": gen.set_weld_gap,
            "Weld Layer Height": gen.set_weld_layer_height,
            "Weld Layer Width": gen.set_weld_layer_width,
            "Weld Layer Overlap": gen.set_weld_layer_overlap,
            "Travel Speed": gen.set_travel_speed,
            "Print Speed": gen.set_print_speed,
            "X Bed Size": gen.set_x_bed_size,
            "Y Bed Size": gen.set_y_bed_size,
            "Z Bed Size": gen.set_z_bed_size,
            "Z Clearance": gen.set_z_clearance
        }

        settings = read_settings_from_yaml()
        if settings is None:
            raise ValueError("Settings should not be None")

        for name, fn in fn_mappings.items():
            label = QLabel(name)
            label.setMaximumWidth(BUTTON_SIZE)
            button_layout.addWidget(label)

            line_edit = QLineEditNum(name, fn, m_view)
            line_edit.setMaximumWidth(BUTTON_SIZE)
            line_edit.setValidator(QDoubleValidator())
            line_edit.textChanged.connect(line_edit.update_value)
            button_layout.addWidget(line_edit)

            # Load settings from yaml settings
            converted_yaml_property = label_to_yaml_property(name)
            settings_val = settings[converted_yaml_property]
            logging.info(f"name: {name}, yaml property: {converted_yaml_property}, value: {settings_val}")
            line_edit.setText(str(settings_val))
        self.setLayout(button_layout)


class SettingsWidget(QWidget):
    """Encapsulates the core settings and additional settings widgets.

    Core Settings:
    - X Volume
    - Y Volume
    - Z Volume
    - X Corner
    - Y Corner
    - Infill Type

    Additional Settings
    - Weld Gap
    - Weld Layer Height
    - Weld Layer Width
    - Weld Layer Overlap
    - Travel Speed
    - Print Speed
    - X, Y, Z Bed Size
    - Z Clearance
    """
    def __init__(self, gen: GCODEGenerator, m_view: 'MicerView', parent=None):
        super(SettingsWidget, self).__init__(parent)
        settings_layout = QVBoxLayout()
        settings_tabs = QTabWidget()
        core_settings = ButtonsWidget(gen=gen, m_view=m_view)
        additional_settings = AdditionalSettingsWidget(gen=gen, m_view=m_view)

        settings_tabs.addTab(core_settings, "Core Settings")
        settings_tabs.addTab(additional_settings, "Additional Settings")
        settings_tabs.setMinimumWidth(400)
        settings_layout.addWidget(settings_tabs, 1, alignment=Qt.AlignmentFlag.AlignRight)
        self.setLayout(settings_layout)
