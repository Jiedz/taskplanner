import sys


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

from PyQt5.QtWidgets import QFileDialog, QApplication
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