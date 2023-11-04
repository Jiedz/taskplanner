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
        self.make_name_widget()
        # Category
        self.make_category_widget()
        # Priority
        self.make_priority_widget()
        # Assignee
        self.make_assignee_widget()
        # Task Description
        self.make_description_textedit()
        # Sub-tasks
        self.make_subtask_list_widget()
        self.layout.addStretch()
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
                # Path Label
                self.make_path_label()
                self.layout.addStretch()
                # Completed button
                self.make_completed_pushbutton()
                # Style
                self.setAttribute(Qt.WA_StyledBackground, True)

            def make_path_label(self):
                self.path_label = QLabel()
                self.layout.addWidget(self.path_label)
                # Geometry
                text = ''
                for ancestor in self.task_widget.task.ancestors:
                    text += f'{ancestor.name}/'
                self.path_label.setText(text)

            def make_completed_pushbutton(self):
                # Pushbutton to mark the task as completed
                self.completed_pushbutton = QPushButton()
                self.layout.addWidget(self.completed_pushbutton)
                self.completed_pushbutton.setMinimumSize(int(0.05*self.parent().width()),
                                                         int(0.05*self.parent().width()))
                # Icon
                icon_path = self.parent()._style.icon_path
                icon_filename = os.path.join(icon_path,
                                             'ok.png')
                self.completed_pushbutton.setIcon(QIcon(icon_filename))

                def switch_background(completed:bool):
                    stylesheet = self.parent()._style.stylesheets['standard view']['toolbar'][
                        'completed_pushbutton']
                    if completed:
                        # Change background color
                        stylesheet = stylesheet.replace('/* background-color */', 'background-color:%s;/* main */\n' % (
                        self.parent()._style.color_palette["completed"]))
                    else:
                        stylesheet = stylesheet.replace(
                            'background-color:%s;/* main */\n' % (self.parent()._style.color_palette["completed"]),
                            '/* background-color */')
                    self.completed_pushbutton.setStyleSheet(stylesheet)

                def callback():
                    self.parent().task._completed = not self.parent().task.completed
                    switch_background(self.parent().task.completed)

                self.completed_pushbutton.clicked.connect(lambda: callback())
                self.parent().task.completed_changed.connect(lambda **kwargs: switch_background(self.parent().task.completed))


        self.toolbar = Toolbar(parent=self)
        self.layout.addWidget(self.toolbar)

    def make_category_widget(self):
        class CategoryWidget(QWidget):
            """
            This widget contains:

                - A combobox of category names
                - A "+" button to add a new category
                - A linedit that pops up when the "+" button is clicked
            """

            def __init__(self, parent: QWidget):
                super().__init__(parent=parent)
                # Layout
                self.layout = QHBoxLayout()
                self.setLayout(self.layout)
                self.layout.setAlignment(Qt.AlignLeft)
                # Icon
                self.make_icon_pushbutton()
                # Categories combobox
                self.make_categories_combobox()
                # Add category pushbutton
                self.make_add_pushbutton()
                # New Textedit
                self.make_new_textedit()
                self.layout.addStretch()

            def make_icon_pushbutton(self):
                self.icon_pushbutton = QPushButton()
                self.layout.addWidget(self.icon_pushbutton)
                # Icon
                icon_path = self.parent()._style.icon_path
                icon_filename = os.path.join(icon_path, 'categories.png')
                self.icon_pushbutton.setIcon(QIcon(icon_filename))


            def make_categories_combobox(self):
                self.categories_combobox = QComboBox(parent=self)
                # Layout
                self.layout.addWidget(self.categories_combobox)
                self.categories_combobox.setMinimumWidth(int(0.3*self.parent().width()))
                # Add items to list
                self.categories_combobox.addItems(['Category 1', 'Category 2'])

                # Callback
                def item_changed():
                    self.parent().task.category = self.categories_combobox.currentText()

                self.categories_combobox.currentIndexChanged.connect(lambda: item_changed())

            def make_add_pushbutton(self):
                # Pushbutton to mark the task as add
                self.add_pushbutton = QPushButton()
                self.layout.addWidget(self.add_pushbutton)
                # Icon
                icon_path = self.parent()._style.icon_path
                icon_filename = os.path.join(icon_path, 'plus.png')
                self.add_pushbutton.setIcon(QIcon(icon_filename))

                def callback():
                    # Show the new assignee linedit
                    self.new_textedit.setText('')
                    self.new_textedit.show()

                self.add_pushbutton.clicked.connect(lambda: callback())

            def make_new_textedit(self):
                # textedit to define a new assignee when the 'plus' button is clicked
                self.new_textedit = QTextEdit()
                # Layout
                self.layout.addWidget(self.new_textedit)
                self.new_textedit.setMaximumSize(int(0.6 * self.parent().width()),
                                                 int(0.07 * self.parent().height()))

                def callback():
                    if '\n' in self.new_textedit.toPlainText():
                        self.new_textedit.hide()
                    elif self.new_textedit.toPlainText().replace('\n', '') != '':
                        self.parent().task.category = self.new_textedit.toPlainText()

                self.new_textedit.textChanged.connect(lambda: callback())
                self.new_textedit.setPlaceholderText("New Category")
                self.new_textedit.hide()

        self.category_widget = CategoryWidget(parent=self)
        self.layout.addWidget(self.category_widget)

    def make_priority_widget(self):
        class PriorityWidget(QWidget):
            """
            This widget contains:

                - An icon symbolizing priority
                - A combobox containing priority levels
            """

            def __init__(self, parent: QWidget):
                super().__init__(parent=parent)
                # Layout
                self.layout = QHBoxLayout()
                self.setLayout(self.layout)
                # Icon push button
                self.make_icon_pushbutton()
                # Combobox
                self.make_combobox()
                self.layout.addStretch()

            def make_icon_pushbutton(self):
                self.icon_pushbutton = QPushButton()
                self.layout.addWidget(self.icon_pushbutton)
                # Icon
                icon_path = self.parent()._style.icon_path
                icon_filename = os.path.join(icon_path,
                                             'ring-bell.png')
                self.icon_pushbutton.setIcon(QIcon(icon_filename))

            def make_combobox(self):
                self.combobox = QComboBox()
                self.layout.addWidget(self.combobox)
                self.combobox.setMinimumWidth(int(0.15 * self.parent().width()))
                # Set priority levels
                self.combobox.addItems(['Low',
                                        'Medium',
                                        'High',
                                        'Urgent'])

                def callback():
                    self.parent().task._priority = self.combobox.currentText().lower()

                self.combobox.currentIndexChanged.connect(lambda: callback())
                self.parent().task.priority_changed.connect(lambda **kwargs:
                                                                     self.combobox.setCurrentText(
                                                                         self.parent().task.priority.title()
                                                                     ))

        self.priority_widget = PriorityWidget(parent=self)
        self.layout.addWidget(self.priority_widget)

    def make_assignee_widget(self):
        class AssigneeWidget(QWidget):
            """
            This widget contains:

                - An icon symbolizing assignee
                - A combobox containing assignee names
                - a '+' button to add an assignee
                - a linedit that pops up when the '+' button is clicked
            """
            def __init__(self,
                         parent:QWidget):
                super().__init__(parent=parent)
                # Layout
                self.layout = QHBoxLayout()
                self.layout.setAlignment(Qt.AlignLeft)
                self.setLayout(self.layout)
                # Geometry
                # Icon pushbutton
                self.make_icon_pushbutton()
                # Assignee combobox
                self.make_combobox()
                # Add pushbutton
                self.make_add_pushbutton()
                # New Textedit
                self.make_new_textedit()
                self.layout.addStretch()

            def make_icon_pushbutton(self):
                self.icon_pushbutton = QPushButton()
                self.layout.addWidget(self.icon_pushbutton)
                # Icon
                icon_path = self.parent()._style.icon_path
                icon_filename = os.path.join(icon_path, 'assignee.png')
                self.icon_pushbutton.setIcon(QIcon(icon_filename))

            def make_combobox(self):
                self.combobox = QComboBox()
                # Layout
                self.layout.addWidget(self.combobox)
                self.combobox.setMinimumWidth(int(0.2 * self.parent().width()))
                # Add items to list
                self.combobox.addItems(['Assignee 1', 'Assignee 2'])

                # Callback
                def item_changed():
                    self.parent().task.assignee = self.combobox.currentText()

                self.combobox.currentIndexChanged.connect(lambda: item_changed())

            def make_add_pushbutton(self):
                # Pushbutton to mark the task as add
                self.add_pushbutton = QPushButton()
                self.layout.addWidget(self.add_pushbutton)
                # Icon
                icon_path = self.parent()._style.icon_path
                icon_filename = os.path.join(icon_path, 'plus.png')
                self.add_pushbutton.setIcon(QIcon(icon_filename))

                def callback():
                    # Show the new assignee linedit
                    self.new_textedit.setText('')
                    self.new_textedit.show()

                self.add_pushbutton.clicked.connect(lambda: callback())

            def make_new_textedit(self):
                # textedit to define a new assignee when the 'plus' button is clicked
                self.new_textedit = QTextEdit()
                # Layout
                self.layout.addWidget(self.new_textedit)
                self.new_textedit.setMaximumSize(int(0.6 * self.parent().width()),
                                                  int(0.07 * self.parent().height()))
                def callback():
                    if '\n' in self.new_textedit.toPlainText():
                        self.new_textedit.hide()
                    elif self.new_textedit.toPlainText().replace('\n', '') != '':
                        self.parent().task.assignee = self.new_textedit.toPlainText()

                self.new_textedit.textChanged.connect(lambda: callback())
                self.new_textedit.setPlaceholderText("New Assignee")
                self.new_textedit.hide()


        self.assignee_widget = AssigneeWidget(parent=self)
        self.layout.addWidget(self.assignee_widget)

    def make_name_widget(self):
        class NameWidget(QWidget):
            """
            This widget contains:
                - An icon indicating a top-level task
                - A textedit containing the task's name
            """
            def __init__(self,
                         parent: QWidget):
                super().__init__(parent=parent)
                # Layout
                self.layout = QHBoxLayout()
                self.layout.setAlignment(Qt.AlignLeft)
                self.setLayout(self.layout)
                # Geometry
                self.setMaximumSize(int(0.8 * self.parent().width()),
                                    int(0.1 * self.parent().height()))
                # Icon
                self.make_icon_pushbutton()
                # Textedit
                self.make_textedit()
                self.layout.addStretch()

            def make_icon_pushbutton(self):
                self.icon_pushbutton = QPushButton()
                self.layout.addWidget(self.icon_pushbutton)
                # Icon
                icon_path = self.parent()._style.icon_path
                icon_filename = os.path.join(icon_path, 'task.png')
                self.icon_pushbutton.setIcon(QIcon(icon_filename))

            def make_textedit(self):
                self.textedit = QTextEdit()
                # Layout
                self.layout.addWidget(self.textedit)
                # Geometry
                self.textedit.setMinimumSize(int(self.width()*0.8),
                                             int(self.height()))
                def callback():
                    self.parent().task.name = self.textedit.toPlainText()

                self.textedit.textChanged.connect(lambda : callback())
                self.textedit.setText(self.parent().task.name)
                self.textedit.setPlaceholderText("Task Name")
        self.name_widget = NameWidget(parent=self)
        self.layout.addWidget(self.name_widget)

    def make_description_textedit(self):
        self.description_textedit = QTextEdit()
        # Layout
        self.layout.addWidget(self.description_textedit)
        #self.description_textedit.setAlignment(Qt.AlignLeft)
        def callback():
            self.task.description = self.description_textedit.toPlainText()

        self.description_textedit.textChanged.connect(lambda : callback())
        self.description_textedit.setText(self.task.description)
        self.description_textedit.setPlaceholderText("Task description")

    def make_subtask_list_widget(self):
        class SubtaskListWidget(QWidget):
            """
            This widget contains:
                - An icon symbolizing a subtask
                - A list of SubtaskWidget, each corresponding to a subtask
            """
            def __init__(self,
                         parent: QWidget):
                super().__init__(parent=parent)
                # Layout
                self.layout = QVBoxLayout()
                self.setLayout(self.layout)
                # Icon
                self.make_icon_pushbutton()

            def make_icon_pushbutton(self):
                self.icon_pushbutton = QPushButton()
                self.layout.addWidget(self.icon_pushbutton)
                # Geometry
                self.icon_pushbutton.setMaximumSize(int(self.parent().width()*0.03),
                                                    int(self.parent().width()*0.1))
                # Icon
                icon_path = self.parent()._style.icon_path
                icon_filename = os.path.join(icon_path, 'subtask.png')
                self.icon_pushbutton.setIcon(QIcon(icon_filename))

        self.subtask_list_widget = SubtaskListWidget(parent=self)
        self.layout.addWidget(self.subtask_list_widget)


