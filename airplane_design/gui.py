"""

@author: Jasper Day
"""

# gui code allows you to select parameters and then updates some plots

from PySide6 import QtCore, QtWidgets, QtGui
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure
import structures
import sys
import pprint

# drop-down menu for materials
# input box for spar outer diameter
# input box for spar inner diameter
# input box for wing span

class StructuresGraph(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(StructuresGraph, self).__init__(parent)
        self.resize(800, 600)
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        # add 2x2 grid of subplots
        self.axs = self.figure.subplots(2,2)
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.canvas)
    
    def update(self, system):
        # plot outputs
        for axs_row in self.axs:
            for ax in axs_row:
                ax.clear()
        structures.make_all_charts(self.axs, system)
        self.figure.tight_layout()
        self.canvas.draw()

class StruTextOutput(QtWidgets.QTextEdit):
    def __init__(self, parent=None):
        super(StruTextOutput, self).__init__(parent)
        self.setReadOnly(True)
    def update(self, system):
        sysinfo = structures.get_system_info(system)
        string = f"""Maximum moment: {sysinfo['max_moment']:0.2f} N.m
Maximum displacement: {sysinfo['max_displacement'] * 1e3:0.2f} mm
Maximum stress: {sysinfo['max_stress'] / 1e6:0.2f} MPa
Mass: {system['beam'].mass * 1e3:0.2f} g"""
        self.setText(string)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Airplane Design")
        self.centralWidget = QtWidgets.QWidget()
        self.setCentralWidget(self.centralWidget)
        self.layout = QtWidgets.QGridLayout(self.centralWidget)
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.update()
        self.update_plot()

    def create_widgets(self):
        self.materials_label = QtWidgets.QLabel("Materials")
        self.materials_dropdown = QtWidgets.QComboBox()
        self.materials_dropdown.addItems(structures.mat_dict.keys())
        self.beam_label = QtWidgets.QLabel("Beam Type")
        self.beam_dropdown = QtWidgets.QComboBox()
        self.beam_dropdown.addItems(structures.beam_dict.keys())
        self.spar_outer_label = QtWidgets.QLabel("Spar Outer Size (mm)")
        self.spar_outer_input = QtWidgets.QLineEdit('25')
        self.spar_inner_label = QtWidgets.QLabel("Spar Inner Size (mm)")
        self.spar_inner_input = QtWidgets.QLineEdit('20')
        self.wing_span_label = QtWidgets.QLabel("Wing Span (m)")
        self.wing_span_input = QtWidgets.QLineEdit('2.4')
        self.update_button = QtWidgets.QPushButton("Update")
        self.weight_label = QtWidgets.QLabel("Weight (kg)")
        self.weight_input = QtWidgets.QLineEdit('3')
        self.gforce_label = QtWidgets.QLabel("G Force")
        self.gforce_input = QtWidgets.QLineEdit('6')
        self.plot = StructuresGraph()
        self.text_output = StruTextOutput()

    def create_layout(self):
        self.layout.addWidget(self.materials_label, 0, 0)
        self.layout.addWidget(self.materials_dropdown, 0, 1,1,3)
        self.layout.addWidget(self.beam_label, 1, 0)
        self.layout.addWidget(self.beam_dropdown, 1, 1,1,3)
        self.layout.addWidget(self.spar_outer_label, 2, 0)
        self.layout.addWidget(self.spar_outer_input, 2, 1)
        self.layout.addWidget(self.spar_inner_label, 2, 2)
        self.layout.addWidget(self.spar_inner_input, 2, 3)
        self.layout.addWidget(self.wing_span_label, 3, 0)
        self.layout.addWidget(self.wing_span_input, 3, 1, 1, 3)
        self.layout.addWidget(self.weight_label, 4, 0)
        self.layout.addWidget(self.weight_input, 4, 1,1,3)
        self.layout.addWidget(self.gforce_label, 5, 0)
        self.layout.addWidget(self.gforce_input, 5,1,1,3)
        self.layout.addWidget(self.plot, 7, 0, 1, 4)
        self.layout.addWidget(self.update_button, 6, 1, 1, 2)
        self.layout.addWidget(self.text_output, 8, 0, 3, 4)

    def create_connections(self):
        # self.materials_dropdown.currentIndexChanged.connect(self.update_plot)   
        # self.beam_dropdown.currentIndexChanged.connect(self.update_plot)
        # self.spar_outer_input.textChanged.connect(self.update_plot)
        # self.spar_inner_input.textChanged.connect(self.update_plot)
        # self.wing_span_input.textChanged.connect(self.update_plot)
        self.update_button.clicked.connect(self.update_plot)
        
    def update_plot(self):
        # get inputs
        material_name = structures.mat_dict[self.materials_dropdown.currentText()]
        spar_outer = float(self.spar_outer_input.text())*1e-3
        spar_inner = float(self.spar_inner_input.text())*1e-3
        wing_span = float(self.wing_span_input.text())
        weight = float(self.weight_input.text())
        gforce = float(self.gforce_input.text())
        beamtype = structures.beam_dict[self.beam_dropdown.currentText()]
        dimensions = {"outer": spar_outer, "inner": spar_inner, "length": wing_span}
        # calculate outputs
        system = structures.get_system(material_name, dimensions, weight, gforce, beamtype)
        self.plot.update(system)
        self.text_output.update(system)

if __name__=="__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())