from typing import Callable
import logging

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtWidgets import (QLabel, QLayout,
                             QLineEdit, QMessageBox, QPushButton, QVBoxLayout,
                             QWidget, QComboBox, QTabWidget)
from framework.ui.gcode_generator import GCODEGenerator, InfillType
from framework.ui.yaml import (read_settings_from_yaml, label_to_yaml_property,
                   write_settings_to_yaml)
from framework.ui.micer_view import MicerView

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

class SettingsWidget(QWidget):
    def __init__(self, gen: GCODEGenerator, m_view: 'MicerView', parent = None):
        super(SettingsWidget, self).__init__(parent)
        settings_layout = QVBoxLayout()
        settings_tabs = QTabWidget()
        core_settings = ButtonsWidget(gen=gen, m_view=m_view)
        additional_settings = QLabel("Widget in Additional Settings.")

        settings_tabs.addTab(core_settings, "Core Settings")
        settings_tabs.addTab(additional_settings, "Additional Settings")
        settings_tabs.setMinimumWidth(400)
        settings_layout.addWidget(settings_tabs, 1, alignment=Qt.AlignmentFlag.AlignRight)
        self.setLayout(settings_layout)
