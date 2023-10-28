'''
This module defines a task widget.
'''

#%% Imports
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QIcon
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
    QTextEdit,
    QDesktopWidget,
    QComboBox
    )
from taskplanner.tasks import Task
from taskplanner.gui.stylesheets.tasks import TaskWidgetStyle
from taskplanner.gui.utilities import set_style, get_screen_size

import os

import inspect
class TaskWidget(QWidget):

    """
    This class defines a task widget.
    """

    def __init__(self,
                 task:Task,
                 main_color:str=None,
                 parent:QWidget=None):
        """
        :param task: :py:class:'taskplanner.tasks.Task'
            The task associated to this widget
        :param main_color: str, optional
            The main color of this task and all sub-tasks
        """
        self.task, self.main_color = task, main_color
        super().__init__(parent=parent)
        # Layout
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)
        # Geometry
        # Get screen size
        screen_size = get_screen_size()
        width, height = int(screen_size.width*0.4), int(screen_size.height*0.6)
        self.setGeometry(int(screen_size.width/2)-int(width/2),
                         int(screen_size.height/2)-int(height/2),
                         width, # width
                         height) # height
        # Define style
        self._style = TaskWidgetStyle(font='light',
                                      color_palette='deep purple')
        # Toolbar
        self.make_toolbar()
        # Task Name
        self.make_name_linedit()
        # Task Description
        self.make_description_textedit()
        # Set style
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
                super().__init__(parent=parent)
                self.task_widget = parent
                self.layout = QHBoxLayout()
                self.setLayout(self.layout)
                self.layout.setAlignment(Qt.AlignLeft)
                # Geometry
                x, y, w, h = [getattr(self.parent().geometry(), x)() for x in ['x',
                                                                               'y',
                                                                               'width',
                                                                               'height']]
                self.setFixedSize(int(w*0.9), int(h * 0.1))
                # Path Label
                self.make_path_label()
                # Category widget
                self.make_category_widget()
                # Completed button
                self.make_completed_pushbutton()
                # Style
                self.setAttribute(Qt.WA_StyledBackground, True)



            def make_completed_pushbutton(self):
                # Pushbutton to mark the task as completed
                self.completed_pushbutton = QPushButton()
                self.layout.addWidget(self.completed_pushbutton)
                # Geometry
                x, y, w, h = [getattr(self.geometry(), u)() for u in ['x', 'y', 'width', 'height']]
                width, height = int(self.height() * 0.5), int(self.height() * 0.5)
                self.completed_pushbutton.setFixedSize(width, height)
                # Icon
                icon_path = self.parent()._style.icon_path
                icon_filename = os.path.join(icon_path, 'ok.png')
                self.completed_pushbutton.setIcon(QIcon(icon_filename))

                def callback():
                    if not self.task_widget.task.completed:
                        self.task_widget.task.completed = True
                        # Change background color
                        stylesheet = self.parent()._style.stylesheets['standard view']['toolbar']['completed_pushbutton']
                        stylesheet = stylesheet.replace('/* background-color */', 'background-color:%s;/* main */\n'%(self.parent()._style.color_palette["completed"]))
                        self.completed_pushbutton.setStyleSheet(stylesheet)
                    else:
                        self.task_widget.task.completed = False
                        # Change background color
                        stylesheet = self.parent()._style.stylesheets['standard view']['toolbar'][
                            'completed_pushbutton']
                        stylesheet = stylesheet.replace('background-color:%s;/* main */\n'%(self.parent()._style.color_palette["completed"]),
                                                        '/* background-color */')
                        self.completed_pushbutton.setStyleSheet(stylesheet)

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

            def make_category_widget(self):
                class CategoryWidget(QWidget):
                    """
                    This widget contains:

                        - A combobox of category names
                        - A "+" button to add a new category
                        - A dialog to add a new category, that pops up when the "+" button is clicked
                    """
                    def __init__(self, parent:QWidget):
                        super().__init__(parent=parent)
                        # Layout
                        self.layout = QHBoxLayout()
                        self.setLayout(self.layout)
                        self.layout.setAlignment(Qt.AlignCenter)
                        # Geometry
                        width, height = int(parent.width() * 0.4), int(parent.height() * 0.5)
                        self.setFixedSize(width, height)
                        # Categories combobox
                        self.make_categories_combobox()
                        # Add category pushbutton
                        self.make_add_pushbutton()
                        # Add category dialog
                        #self.make_add_dialog()

                    def make_categories_combobox(self):
                        self.categories_combobox = QComboBox(parent=self)
                        # Layout
                        self.layout.addWidget(self.categories_combobox)
                        # Geometry
                        width, height = int(self.width() * 0.7), int(self.height()*0.7)
                        self.categories_combobox.setFixedSize(width, height)
                        # Add items to list
                        self.categories_combobox.addItems(['Category 1', 'Category 2'])
                        # Callback
                        def item_changed():
                            self.parent().parent().task.category = self.categories_combobox.currentText()

                        self.categories_combobox.currentIndexChanged.connect(lambda : item_changed())

                    def make_add_pushbutton(self):
                        # Pushbutton to mark the task as add
                        self.add_pushbutton = QPushButton()
                        self.layout.addWidget(self.add_pushbutton)
                        # Geometry
                        width, height = int(self.height() * 0.7), int(self.height() * 0.7)
                        self.add_pushbutton.setFixedSize(width, height)
                        # Icon
                        icon_path = self.parent().parent()._style.icon_path
                        icon_filename = os.path.join(icon_path, 'plus.png')
                        self.add_pushbutton.setIcon(QIcon(icon_filename))

                        def callback():
                            raise NotImplementedError

                        self.add_pushbutton.clicked.connect(lambda: callback())

                    def make_add_dialog(self):
                        raise NotImplementedError

                self.category_widget = CategoryWidget(parent=self)
                self.layout.addWidget(self.category_widget)




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


