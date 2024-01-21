import sys

import numpy
from matplotlib import pyplot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar


def set_style(widget, stylesheets):
    """
    Recursively set style sheets to a widget and all its sub-widgets.
    :param widget: :py:class:'QWidget'
        The widget to which the style is set.
    :param stylesheets: dict or str
        A single style sheet or a dictionary of them. Each key can either contain a single style sheet or another dictionary
        of style sheets. Each key must be equal to the attribute name of a sub-widget, internal to 'widget'.
    :return:
    """
    if type(stylesheets) is str: # widget is an 'elementary' QWidget
        widget.setStyleSheet(stylesheets)
    else: # widget is a custom QWidget
        for widget_name in tuple(stylesheets):
            try:
                if widget_name == 'main':
                    widget.setStyleSheet(stylesheets['main'])
                else:
                    set_style(widget=getattr(widget, widget_name),
                              stylesheets=stylesheets[widget_name])
            except Exception as e:
                print(e)

from screeninfo import get_monitors

def get_primary_screen():
    monitors = get_monitors()
    return [m for m in monitors if m.is_primary][0]


from PyQt5.Qt import QCursor, QApplication

def get_pixel_ratio():
    # Source: https://stackoverflow.com/a/40053864/3388962
    pos = QCursor.pos()
    for screen in QApplication().screens():
        rect = screen.geometry()
        if rect.contains(pos):
            return screen.devicePixelRatio()

from PyQt5.QtWidgets import QFileDialog, QApplication, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt
import os
def select_file(start_directory=None, title="Select file"):
    """
    INPUTS
    -----------
    start_directory : str
        the absolute path of the starting directory.
    """
    if start_directory is None:
        start_directory = os.getcwd()
    #Let the user choose a different data path, if needed.
    #--------------------------------
    #app = QApplication(sys.argv)
    file_dialog = QFileDialog()
    file_path = file_dialog.getOpenFileName(caption=title, directory=start_directory)[0]
    if file_path == '':
        return
    else:
        return file_path

def select_directory(start_directory=None, title="Select Directory"):
    """
    INPUTS
    -----------
    start_directory : str
        the absolute path of the starting directory.
    """
    if start_directory is None:
        start_directory = os.getcwd()
    #Let the user choose a different data path, if needed.
    #--------------------------------
    #app = QApplication(sys.argv)
    file_dialog = QFileDialog()
    file_dialog.rejected.connect(lambda: None)
    directory_path = file_dialog.getExistingDirectory(caption=title, directory=start_directory)
    if directory_path == '':
            return
    else:
        return directory_path


class PyplotWidget(QWidget):
    '''
    This class defines a plot widget based on :py:class:`matplotlib.pyplot`.
    A widget of this kind contains:
        - A :py:class:`matplotlib.pyplot.Figure`
        - A navigation toolbar
        - A figure canvas
    '''

    def __init__(self,
                 name: str = "Pyplot Widget",
                 figure=None,
                 grid: bool = True,
                 parent: QWidget = None):
        '''
        Parameters
        ----------
        name : str, optional
            Name of the widget. The default is "Pyplot Widget".
        figure : TYPE, optional
            The pyplot figure that the widget should contain. The default is None.
        grid: bool, optionak
            If 'True', the grid is shown on all axes at the widget's creation
        parent: py:class:`QWidget`, optional
            The parent of this widget.
        Returns
        -------
        None.

        '''
        super().__init__()
        self.name = name
        if figure is not None:
            self.figure = figure
        else:
            self.figure = pyplot.figure(figsize=(9, 8))
            self.figure.add_subplot(111)
        if grid:
            for axis in self.figure.axes:
                axis.grid(True)
        # Make the Fiber Interactive
        pyplot.ion()
        # Close the Figure before Inserting it into the Widget
        pyplot.close(pyplot.gcf())
        self.canvas = FigureCanvas(self.figure)
        #self.toolbar = NavigationToolbar(self.canvas, self)
        # Set Main Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.setSpacing(0)
        # Add Widgets to Layout
        self.title_label = QLabel()
        self.title_label.setContentsMargins(0, 0, 0, 0)
        self.title_label.setAlignment(Qt.AlignCenter)
        #self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.canvas)
        # self.background = self.canvas.copy_from_bbox(self.figure.bbox)

    def draw(self):
        '''
        Repaints the figure canvas with current data.

        Returns
        -------
        None.

        '''
        self.canvas.draw()
        self.canvas.flush_events()

    def set_title(self, title: str):
        self.title_label.setText(title)
