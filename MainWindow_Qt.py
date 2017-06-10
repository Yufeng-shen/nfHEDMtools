# coding: utf-8
import pickle
import h5py
import numpy as np
import sys, os
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from GrainMatch_Qt import WorkingWindow

class AppForm(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle('Grain Matching')

        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()

    def load_default(self):
        self.a0 = h5py.File('/home/fyshen13/Downloads/AngFiles_Anneal0_Output/Segment_15_2deg_27.dream3d')
        self.ID0=self.a0['DataContainers']['ImageDataContainer']['CellData']['FeatureIds']
        self.IPF0=self.a0['DataContainers']['ImageDataContainer']['CellData']['IPFColor']
        self.Mask0=self.a0['DataContainers']['ImageDataContainer']['CellData']['Mask']
        self.ce0=self.a0['DataContainers']['ImageDataContainer']['CellData']['EulerAngles']
        self.ci0=self.a0['DataContainers']['ImageDataContainer']['CellData']['Confidence Index']

        self.a1 = h5py.File('/home/fyshen13/Downloads/AngFiles_Anneal1_Output/Segment_match_2deg_27.dream3d')
        self.ID1=self.a1['DataContainers']['ImageDataContainer']['CellData']['FeatureIds']
        self.IPF1=self.a1['DataContainers']['ImageDataContainer']['CellData']['IPFColor']
        self.Mask1=self.a1['DataContainers']['ImageDataContainer']['CellData']['Mask']
        self.ce1=self.a1['DataContainers']['ImageDataContainer']['CellData']['EulerAngles']
        self.ci1=self.a1['DataContainers']['ImageDataContainer']['CellData']['Confidence Index']

        self.s0=np.loadtxt('/home/fyshen13/Downloads/AngFiles_Anneal0_Output/centroids._2deg_27.txt')[1:]
        self.s1=np.loadtxt('/home/fyshen13/Downloads/AngFiles_Anneal1_Output/centroids._2deg_27.txt')[1:]

        self.e0=np.loadtxt('/home/fyshen13/Downloads/AngFiles_Anneal0_Output/AvgEulerAngles._2deg_27.txt')[1:]
        self.e1=np.loadtxt('/home/fyshen13/Downloads/AngFiles_Anneal1_Output/AvgEulerAngles._2deg_27.txt')[1:]

        self.backnomatched=pickle.load(open('/home/fyshen13/Fe/matchID/2deg27/nomatchgrain_backward.pickle','r'))
        self.v1=np.loadtxt('/home/fyshen13/Downloads/AngFiles_Anneal1_Output/Volumes._2deg_27.txt')[1:]
        idx1=np.argsort(self.v1)
        idx1=np.flipud(idx1)
        self.backnomatched=idx1[self.backnomatched]
        self.backcorID=np.loadtxt('/home/fyshen13/Fe/matchID/2deg27/corFeatureIDs_backward.txt').astype(int)

        self.workingwindow=WorkingWindow(_mainwindow=self)
        self.workingwindow.show()
    def load_plot(self):
        file_choices = "DREAM3D (*.dream3d)"
        filename0 = unicode(QFileDialog.getOpenFileName(self,
                'Load state 0 file','',file_choices))
        self.a0 = h5py.File(filename0)
        self.ID0=self.a0['DataContainers']['ImageDataContainer']['CellData']['FeatureIds']
        self.IPF0=self.a0['DataContainers']['ImageDataContainer']['CellData']['IPFColor']
        filename1 = unicode(QFileDialog.getOpenFileName(self,
                'Load state 1 file','',file_choices))
        self.a1 = h5py.File(filename1)
        self.ID1=self.a1['DataContainers']['ImageDataContainer']['CellData']['FeatureIds']
        self.IPF1=self.a1['DataContainers']['ImageDataContainer']['CellData']['IPFColor']
        
        self.workingwindow=WorkingWindow(_mainwindow=self)
        self.workingwindow.show()

    def save_plot(self):
        file_choices = "PNG (*.png)|*.png"
        
        path = unicode(QFileDialog.getSaveFileName(self, 
                        'Save file', '', 
                        file_choices))
        if path:
            self.canvas.print_figure(path, dpi=self.dpi)
            self.statusBar().showMessage('Saved to %s' % path, 2000)
    
    def on_about(self):
        msg = """ A demo of using PyQt with matplotlib:
        
         * Use the matplotlib navigation bar
         * Add values to the text box and press Enter (or click "Draw")
         * Show or hide the grid
         * Drag the slider to modify the width of the bars
         * Save the plot to a file using the File menu
         * Click on a bar to receive an informative message
        """
        QMessageBox.about(self, "About the demo", msg.strip())
    

    def create_main_frame(self):
        self.main_frame=QWidget()
        slider_label = QLabel('alpha (%):')
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(50)
        self.slider.setTracking(True)
        self.slider.setTickPosition(QSlider.TicksBothSides)

#        self.centroid0=QLineEdit()
#        self.centroid1=QLineEdit()
        
        self.setCentralWidget(self.slider)
        return

    def create_status_bar(self):
        self.status_text = QLabel("This is a demo")
        self.statusBar().addWidget(self.status_text, 1)
        
    def create_menu(self):        
        self.file_menu = self.menuBar().addMenu("&File")
        
        load_default_action = self.create_action("&Load default dream3d",
            shortcut="Ctrl+D", slot=self.load_default, 
            tip="Load the dream3d file")
        load_file_action = self.create_action("&Load dream3d",
            shortcut="Ctrl+L", slot=self.load_plot, 
            tip="Load the dream3d file")
        save_file_action = self.create_action("&Save plot",
            shortcut="Ctrl+S", slot=self.save_plot, 
            tip="Save the plot")
        quit_action = self.create_action("&Quit", slot=self.close, 
            shortcut="Ctrl+Q", tip="Close the application")
        
        self.add_actions(self.file_menu, 
            (save_file_action,None, load_file_action,None, load_default_action, None, quit_action))
        
        self.help_menu = self.menuBar().addMenu("&Help")
        about_action = self.create_action("&About", 
            shortcut='F1', slot=self.on_about, 
            tip='About the demo')
        
        self.add_actions(self.help_menu, (about_action,))

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def create_action(  self, text, slot=None, shortcut=None, 
                        icon=None, tip=None, checkable=False, 
                        signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action


def main():
    app = QApplication(sys.argv)
    form = AppForm()
    form.show()
    app.exec_()


if __name__ == "__main__":
    main()
