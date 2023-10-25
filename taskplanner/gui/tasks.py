'''
This module defines a task widget.
'''

#%% Imports
from PyQt5.QtCore import Qt, QRect
from PyQt5.Qt import QFont
from PyQt5.QtWidgets import \
(
    QApplication,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDateTimeEdit,
    QDial,
    QDoubleSpinBox,
    QFontComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLCDNumber,
    QLineEdit,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSlider,
    QSpinBox,
    QTabWidget,
    QTimeEdit,
    QVBoxLayout,
    QBoxLayout,
    QGridLayout,
    QWidget,
    QScrollArea,
    QTextEdit
    )
from taskplanner.tasks import Task
from taskplanner.gui.stylesheets.tasks import TaskWidgetStyle
from taskplanner.gui.utilities import set_style
import os
class TaskWidget(QWidget):

    """
    This class defines a task widget.
    """

    def __init__(self,
                 task:Task,
                 main_color:str=None):
        """
        :param task: :py:class:'taskplanner.tasks.Task'
            The task associated to this widget
        :param main_color: str, optional
            The main color of this task and all sub-tasks
        """
        self.task, self.main_color = task, main_color
        super().__init__()
        # Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setAlignment(Qt.AlignTop)
        # Geometry
        self.setFixedHeight(900)
        self.setFixedWidth(850)
        # Toolbar
        self.make_toolbar()
        # Task Name
        self.make_name_linedit()
        # Task Description
        self.make_description_textedit()
        # Style
        self._style = TaskWidgetStyle(font='elegant light')
        set_style(widget=self,
                  stylesheets=self._style.stylesheets['standard view'])

    def make_toolbar(self):
        class Toolbar(QWidget):
            """
            The toolbar contains:

                - A pushbutton to mark the task as completed
                - A pushbutton to close the Task view

            :return:
            """
            def __init__(self, parent):
                super().__init__()
                self.task_widget = parent
                self.layout = QHBoxLayout()
                self.setLayout(self.layout)
                self.layout.setAlignment(Qt.AlignLeft)
                # Geometry
                x, y, w, h = [getattr(self.task_widget.geometry(), x)() for x in ['x',
                                                                                  'y',
                                                                                  'width',
                                                                                  'height']]
                self.setFixedSize(int(w*0.9), int(h * 0.1))
                # Path Label
                self.make_path_label()
                # Completed button
                self.make_completed_pushbutton()
                # Style
                self.setAttribute(Qt.WA_StyledBackground, True)



            def make_completed_pushbutton(self):
                # Pushbutton to mark the task as completed
                self.completed_pushbutton = QPushButton('Mark Completed')
                self.layout.addWidget(self.completed_pushbutton)
                # Geometry
                self.completed_pushbutton.setFixedSize(int(self.width() * 0.25),
                                                       int(self.height() * 0.5))

                def callback():
                    if self.completed_pushbutton.text() == 'Mark Completed':
                        self.completed_pushbutton.setText('Completed')
                        self.task_widget.task.completed = True
                    else:
                        self.completed_pushbutton.setText('Mark Completed')
                        self.task_widget.task.completed = False
                self.completed_pushbutton.clicked.connect(lambda : callback())

            def make_path_label(self):
                self.path_label = QLabel()
                self.layout.addWidget(self.path_label)
                # Geometry
                self.path_label.setFixedSize(int(self.width() * 0.5),
                                                       int(self.height() * 0.5))
                text = ''
                for ancestor in self.task_widget.task.ancestors:
                    text += f'{ancestor.name}/'
                self.path_label.setText(text)

        self.toolbar = Toolbar(parent=self)
        self.layout.addWidget(self.toolbar)

    def make_name_linedit(self):
        self.name_linedit = QLineEdit()
        # Layout
        self.layout.addWidget(self.name_linedit)
        self.name_linedit.setAlignment(Qt.AlignLeft)
        # Geometry
        self.name_linedit.setFixedSize(int(self.width()*0.6),
                                       int(self.height()*0.1))
        def callback():
            self.task.name = self.name_linedit.text()

        self.name_linedit.textEdited.connect(lambda : callback())
        self.name_linedit.setText(self.task.name)
        self.name_linedit.setPlaceholderText("Task Name")

    def make_description_textedit(self):
        self.description_textedit = QTextEdit()
        # Layout
        self.layout.addWidget(self.description_textedit)
        self.description_textedit.setAlignment(Qt.AlignLeft)
        # Geometry
        self.description_textedit.setFixedSize(int(self.width()*0.6),
                                       int(self.height()*0.2))
        def callback():
            self.task.description = self.description_textedit.toPlainText()

        self.description_textedit.textChanged.connect(lambda : callback())
        self.description_textedit.setText(self.task.description)
        self.description_textedit.setPlaceholderText("Task description")


