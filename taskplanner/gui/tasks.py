"""
This module defines a task widget.
"""

import os
from datetime import date as dt

# %% Imports
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon, QTextCursor
from PyQt5.QtWidgets import \
    (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QTextEdit,
    QComboBox,
    QScrollArea,
    QMainWindow,
    QCalendarWidget,
)

from taskplanner.gui.stylesheets.tasks import TaskWidgetStyle
from taskplanner.gui.utilities import set_style, get_screen_size
from taskplanner.tasks import Task


class TaskWidget(QWidget):
    """
    This class defines a task widget.
    """

    def __init__(self,
                 task: Task,
                 main_color: str = None,
                 parent: QWidget = None):
        """
        :param task: :py:class:'taskplanner.tasks.Task'
            The task associated to this widget
        :param main_color: str, optional
            The main color of this task and all sub-tasks
        :param parent: :py:class:'QWidget', optional
            The parent widget
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
        width, height = int(screen_size.width * 0.3), int(screen_size.height * 0.6)
        self.setGeometry(int(screen_size.width / 2) - int(width / 2),
                         int(screen_size.height / 2) - int(height / 2),
                         width,  # width
                         height)  # height
        # Define style
        self._style = TaskWidgetStyle(font='light',
                                      color_palette='deep purple')
        # Scroll area
        self.scrollarea = QScrollArea()
        self.scrollarea.setWidgetResizable(True)
        self.scrollarea.setGeometry(self.geometry())
        self.scrollarea.setWidget(self)
        # Toolbar
        self.make_toolbar()
        self.toolbar.setMinimumHeight(int(self.height()*0.08))
        self.toolbar.completed_pushbutton.setFixedSize(int(self.toolbar.height()*0.7),
                                                         int(self.toolbar.height()*0.7))
        # Task Name
        self.make_name_widget()
        ## Textedit
        self.name_widget.textedit.setFixedHeight(int(self.height()*0.1))
        self.name_widget.textedit.setMinimumWidth(int(self.width()*0.6))
        # Horizontal layout that contains the (category, priority, assignee) layout and the (start date, end date) widgets
        self.middle_layout_horizontal = QHBoxLayout()
        self.layout.addLayout(self.middle_layout_horizontal)
        # Vertical layout for category, priority, assignee
        self.middle_layout_vertical = QVBoxLayout()
        self.middle_layout_horizontal.addLayout(self.middle_layout_vertical)
        # Category
        self.make_category_widget()
        ## Combobox
        self.category_widget.combobox.setMinimumWidth(int(self.width()*0.2))
        ## New textedit
        self.category_widget.new_textedit.setMaximumHeight(int(self.category_widget.combobox.height() * 2))
        # Priority
        self.make_priority_widget()
        ## Combobox
        self.priority_widget.combobox.setMinimumWidth(int(self.width() * 0.2))
        # Assignee
        self.make_assignee_widget()
        ## Combobox
        self.assignee_widget.combobox.setMinimumWidth(int(self.width() * 0.2))
        ## New textedit
        self.assignee_widget.new_textedit.setMaximumHeight(self.category_widget.new_textedit.height())
        # Start and end date widgets
        self.make_date_widgets()
        self.middle_layout_horizontal.addStretch()
        ## Start date
        # Task Description
        self.make_description_textedit()
        self.description_textedit.setMaximumWidth(int(self.width()*0.8))
        self.description_textedit.setMinimumHeight(int(self.height() * 0.15))
        # Sub-tasks
        self.make_subtask_list_widget()
        self.subtask_list_widget.setMaximumWidth(int(self.width()*2))
        ## Icon pushbutton
        self.subtask_list_widget.icon_pushbutton.setFixedSize(int(self.height()*0.05),
                                                              int(self.height()*0.05))
        ## New textedit
        self.subtask_list_widget.new_textedit.setFixedWidth(int(self.width()*0.5))
        self.subtask_list_widget.new_textedit.setFixedHeight(int(self.category_widget.new_textedit.height()))
        # Set style
        set_style(widget=self,
                  stylesheets=self._style.stylesheets['standard view'])

    def show(self):
        super().show()
        self.scrollarea.show()

    def make_toolbar(self):
        class Toolbar(QWidget):
            """
            The toolbar contains:

                - A pushbutton to mark the task as completed
                - A pushbutton to close the Task view

            :return:
            """

            def __init__(self,
                         task: Task,
                         parent: QWidget):
                """
                :param task: :py:class:'taskplanner.tasks.Task'
                    The task associated to this widget
                :param parent: :py:class:'QWidget', optional
                    The parent widget
                """
                super().__init__(parent=parent)
                self.task = task
                self.task_widget = parent
                self.layout = QHBoxLayout()
                self.setLayout(self.layout)
                self.layout.setAlignment(Qt.AlignLeft)
                # Path widget
                self.make_path_widget()
                self.layout.addStretch()
                # Completed button
                self.make_completed_pushbutton()
                # Style
                self.setAttribute(Qt.WA_StyledBackground, True)

            def make_path_widget(self):
                class PathWidget(QWidget):
                    """
                    This widget contains:
                        - A pushbutton for each super-task
                        - A "/" label between each pair of super-tasks, as a separator
                    """
                    def __init__(self,
                                 task: Task,
                                 parent: QWidget = None):
                        """
                        :param task: :py:class:'taskplanner.tasks.Task'
                            The task associated to this widget
                        :param parent: :py:class:'QWidget', optional
                            The parent widget
                        """
                        super().__init__(parent=parent)
                        self.task = task
                        # Layout
                        self.layout = QHBoxLayout()
                        self.setLayout(self.layout)
                        # Geometry
                        # Push buttons and Labels
                        self.separator_label = QLabel()
                        self.separator_label.setText('|')
                        self.supertask_pushbuttons = []
                        self.make_path()
                        self.layout.addStretch()
                        slots = [slot for slot in self.task.parent_changed._slots if
                                 'PathWidget.' in str(slot)]
                        for slot in slots:
                            self.task.parent_changed.disconnect(slot)
                        self.task.parent_changed.connect(lambda **kwargs: self.make_path())

                    def make_path(self):
                        for supertask in self.task.ancestors:
                            if supertask not in [widget.task for widget in self.supertask_pushbuttons]:
                                pushbutton = self.make_supertask_pushbutton(supertask=supertask)
                                self.layout.addWidget(pushbutton)
                                self.supertask_pushbuttons += [pushbutton]
                        for widget in self.supertask_pushbuttons:
                            if widget.task not in self.task.ancestors:
                                widget.hide()
                                self.supertask_pushbuttons.remove(widget)

                    def make_supertask_pushbutton(self,
                                                  supertask: Task):
                        pushbutton = QPushButton()
                        setattr(pushbutton, 'task', supertask)
                        # Geometry
                        # Callback
                        def callback():
                            task_widget = TaskWidget(task=supertask)
                            task_widget.show()

                        def update_widget():
                            n_max = min([len(supertask.name), 20])
                            text = supertask.name[:n_max]
                            if n_max == 20:
                                text += '...'
                            pushbutton.setText(text)

                        # Connect task and widget
                        pushbutton.clicked.connect(callback)
                        supertask.name_changed.connect(lambda **kwargs: update_widget())
                        # Set initial text
                        update_widget()
                        return pushbutton


                self.path_widget = PathWidget(task=self.task,
                                              parent=self)
                self.layout.addWidget(self.path_widget)

            def make_completed_pushbutton(self):
                # Pushbutton to mark the task as completed
                self.completed_pushbutton = QPushButton()
                self.layout.addWidget(self.completed_pushbutton)
                # Icon
                icon_path = self.parent()._style.icon_path
                icon_filename = os.path.join(icon_path,
                                             'ok.png')
                self.completed_pushbutton.setIcon(QIcon(icon_filename))

                def switch_background(completed: bool):
                    stylesheet = self.parent()._style.stylesheets['standard view']['toolbar'][
                        'completed_pushbutton']
                    if completed:
                        stylesheet = stylesheet.replace('/* background-color */', 'background-color:%s;/* main */' % (
                            self.parent()._style.color_palette["completed"]))
                    else:
                        stylesheet = stylesheet.replace(
                            'background-color:%s;/* main */' % (self.parent()._style.color_palette["completed"]),
                            '/* background-color */')
                    self.parent()._style.stylesheets['standard view']['toolbar'][
                        'completed_pushbutton'] = stylesheet
                    self.completed_pushbutton.setStyleSheet(stylesheet)

                def callback():
                    self.task.completed = not self.task.completed
                    switch_background(self.task.completed)

                # Set Current Value
                switch_background(self.task.completed)
                self.completed_pushbutton.clicked.connect(lambda: callback())
                self.task.completed_changed.connect(
                    lambda **kwargs: switch_background(self.task.completed))

        self.toolbar = Toolbar(task=self.task,
                               parent=self)
        self.layout.addWidget(self.toolbar)

    def make_category_widget(self):
        class CategoryWidget(QWidget):
            """
            This widget contains:

                - A combobox of category names
                - A "+" button to add a new category
                - A linedit that pops up when the "+" button is clicked
            """

            def __init__(self,
                         task: Task,
                         parent: QWidget = None):
                """
                :param task: :py:class:'taskplanner.tasks.Task'
                    The task associated to this widget
                :param parent: :py:class:'QWidget', optional
                    The parent widget
                """
                super().__init__(parent=parent)
                self.task = task
                # Layout
                self.layout = QHBoxLayout()
                self.setLayout(self.layout)
                self.layout.setAlignment(Qt.AlignLeft)
                # Icon
                self.make_icon_pushbutton()
                # Categories combobox
                self.make_combobox()
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

            def make_combobox(self):
                self.combobox = QComboBox(parent=self)
                # Layout
                self.layout.addWidget(self.combobox)
                # Add items to list
                self.combobox.addItems(['Category 1', 'Category 2'])

                # Callback
                def item_changed():
                    self.task.category = self.combobox.currentText()

                def change_item():
                    self.combobox.setCurrentText(self.task.category)

                self.task.category_changed.connect(lambda **kwargs: change_item())
                self.combobox.currentIndexChanged.connect(lambda: item_changed())
                # Set Initial Value
                change_item()

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

                def callback():
                    if '\n' in self.new_textedit.toPlainText():
                        self.new_textedit.hide()
                    elif self.new_textedit.toPlainText().replace('\n', '') != '':
                        self.task.category = self.new_textedit.toPlainText()

                self.new_textedit.textChanged.connect(lambda: callback())
                self.new_textedit.setPlaceholderText("New Category")
                self.new_textedit.hide()

        self.category_widget = CategoryWidget(task=self.task,
                                              parent=self)
        self.middle_layout_vertical.addWidget(self.category_widget)

    def make_priority_widget(self):
        class PriorityWidget(QWidget):
            """
            This widget contains:

                - An icon symbolizing priority
                - A combobox containing priority levels
            """

            def __init__(self,
                         task: Task,
                         parent: QWidget=None):
                """
                :param task: :py:class:'taskplanner.tasks.Task'
                    The task associated to this widget
                :param parent: :py:class:'QWidget', optional
                    The parent widget
                """
                super().__init__(parent=parent)
                self.task = task
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
                # Set priority levels
                self.combobox.addItems(['Low',
                                        'Medium',
                                        'High',
                                        'Urgent'])

                def callback():
                    # Update task
                    self.task.priority = self.combobox.currentText().lower()

                def inv_callback():
                    # Update widget
                    self.combobox.setCurrentText(self.task.priority.title())

                # Connect task and widget
                self.task.priority_changed.connect(lambda **kwargs: inv_callback())
                self.combobox.currentIndexChanged.connect(lambda: callback())
                # Set initial value
                inv_callback()

        self.priority_widget = PriorityWidget(task=self.task,
                                              parent=self)
        self.middle_layout_vertical.addWidget(self.priority_widget)

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
                         task: Task,
                         parent: QWidget = None):
                """
                :param task: :py:class:'taskplanner.tasks.Task'
                    The task associated to this widget
                :param parent: :py:class:'QWidget', optional
                    The parent widget
                """
                super().__init__(parent=parent)
                self.task = task
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
                # Add items to list
                self.combobox.addItems(['Assignee 1', 'Assignee 2'])

                # Callback
                def callback():
                    # Update task
                    self.task.assignee = self.combobox.currentText()

                def inv_callback():
                    if self.task.assignee is None:
                        callback()
                    # Update widget
                    self.combobox.setCurrentText(self.task.assignee)

                # Connect task and widget
                self.task.assignee_changed.connect(lambda **kwargs: inv_callback())
                self.combobox.currentIndexChanged.connect(lambda: callback())
                # Set initial value
                inv_callback()

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

                def callback():
                    if '\n' in self.new_textedit.toPlainText():
                        self.new_textedit.hide()
                    elif self.new_textedit.toPlainText().replace('\n', '') != '':
                        self.task.assignee = self.new_textedit.toPlainText()

                self.new_textedit.textChanged.connect(lambda: callback())
                self.new_textedit.setPlaceholderText("New Assignee")
                self.new_textedit.hide()

        self.assignee_widget = AssigneeWidget(task=self.task,
                                              parent=self)
        self.middle_layout_vertical.addWidget(self.assignee_widget)

    def make_date_widgets(self):
        class DateWidget(QWidget):
            """
            This widget contains:
                - An icon symbolizing the type of time mode (start, end, ...)
                - A label indicating the selected date
                - A calendar widget that allows the user to select a day
            """
            def __init__(self,
                         task: Task,
                         parent: QWidget = None,
                         time_mode: str = 'start'):
                """
                :param task: :py:class:'taskplanner.tasks.Task'
                    The task associated to this widget
                :param parent: :py:class:'QWidget', optional
                    The parent widget
                :param time_mode: str, optional
                    The time mode, e.g., 'start', 'end'.
                """
                TIME_MODES = ['start', 'end']
                if time_mode not in TIME_MODES:
                    raise ValueError(f'Unrecognized time more {time_mode}. Possible time modes are {tuple(TIME_MODES)}')
                self.task = task
                self.time_mode = time_mode
                super().__init__(parent=parent)
                # Layout
                self.layout = QHBoxLayout()
                self.setLayout(self.layout)
                # Icon pushbutton
                self.make_icon_pushbutton()
                # Label
                self.make_label()
                # Calendar widget
                self.make_calendar_widget()

            def make_icon_pushbutton(self):
                self.icon_pushbutton = QPushButton()
                # Layout
                self.layout.addWidget(self.icon_pushbutton)
                # Icon
                icon_path = self.parent()._style.icon_path
                name = 'start' if self.time_mode=='start' else 'stop'
                icon_filename = os.path.join(icon_path, f'{name}-time.png')
                self.icon_pushbutton.setIcon(QIcon(icon_filename))

                def callback():
                    self.calendar_widget.show()

                self.icon_pushbutton.clicked.connect(callback)

            def make_label(self):
                self.label = QLabel()
                # Layout
                self.layout.addWidget(self.label)
                # Geometry
                self.label.setMaximumHeight(int(self.height()))

                def update_label():
                    date = getattr(self.task, f'{self.time_mode}_date')
                    self.label.setText(f'{date.day}/{date.month}/{date.year}')

                getattr(self.task, f'{self.time_mode}_date_changed').connect(lambda **kwargs: update_label())
                update_label()



            def make_calendar_widget(self):
                self.calendar_widget = QCalendarWidget()
                self.calendar_widget.setGridVisible(True)
                # Geometry
                x, y, w, h = [getattr(self.parent().geometry(), f'{z}')() for z in ['x',
                                                                           'y',
                                                                           'width',
                                                                           'height']]
                self.calendar_widget.setWindowTitle(f'{self.time_mode.title()} Date')
                self.calendar_widget.setGeometry(int(x+1.5*w),
                                                 int(y+h/2),
                                                 self.calendar_widget.width(),
                                                 self.calendar_widget.height())

                def callback():
                    # Get date from calendar
                    date = self.calendar_widget.selectedDate()
                    # Set date to task
                    old_date = getattr(self.task, f'{self.time_mode}_date')
                    task_date = dt(date.year(),
                                   date.month(),
                                   date.day())
                    try:
                        setattr(self.task, f'{self.time_mode}_date', task_date)
                    except ValueError:
                        self.calendar_widget.setSelectedDate(QDate(old_date.year,
                                                                   old_date.month,
                                                                   old_date.day))
                        callback()
                    # Hide calendar
                    self.calendar_widget.hide()

                self.calendar_widget.clicked.connect(callback)

        self.start_date_widget = DateWidget(task=self.task,
                                            parent=self,
                                            time_mode='start')
        self.middle_layout_horizontal.addWidget(self.start_date_widget)
        self.end_date_widget = DateWidget(task=self.task,
                                          parent=self,
                                          time_mode='end')
        self.middle_layout_horizontal.addWidget(self.end_date_widget)


    def make_name_widget(self):
        class NameWidget(QWidget):
            """
            This widget contains:
                - An icon indicating a top-level task
                - A textedit containing the task's name
            """

            def __init__(self,
                         task: Task,
                         parent: QWidget = None):
                """
                :param task: :py:class:'taskplanner.tasks.Task'
                    The task associated to this widget
                :param parent: :py:class:'QWidget', optional
                    The parent widget
                """
                super().__init__(parent=parent)
                self.task = task
                # Layout
                self.layout = QHBoxLayout()
                self.layout.setAlignment(Qt.AlignLeft)
                self.setLayout(self.layout)
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

                def callback():
                    # Update task
                    self.task.name = self.textedit.toPlainText()

                def inv_callback():
                    # Update widget
                    """
                    This function is only called when the task's property is
                    changed outside this widget. If widget signals are not blocked
                    at the time of updating the widget, an infinite recursion is triggered
                    between task update and widget update.
                    """
                    self.textedit.blockSignals(True)
                    self.textedit.setText(self.task.name)
                    self.textedit.blockSignals(False)
                    """
                    For some reason, the cursor is normally reset to the start of the 
                    widget. One then needs to move the cursor to the end and then reset the cursor
                    """
                    # Move cursor to the end
                    cursor = self.textedit.textCursor()
                    cursor.movePosition(cursor.Right,
                                        cursor.MoveAnchor,
                                        len(self.task.name))
                    """
                    For some other reason, all text is also automatically selected, so one needs to
                    clear the selection.
                    """
                    cursor.clearSelection()
                    # Reset cursor
                    self.textedit.setTextCursor(cursor)

                # Connect task and widget
                self.textedit.textChanged.connect(lambda: callback())
                self.task.name_changed.connect(lambda **kwargs: inv_callback())
                # Set initial value
                inv_callback()
                self.textedit.setPlaceholderText("Task Name")

        self.name_widget = NameWidget(task=self.task,
                                      parent=self)
        self.layout.addWidget(self.name_widget)

    def make_description_textedit(self):
        self.description_textedit = QTextEdit()
        # Layout
        self.layout.addWidget(self.description_textedit)
        # Geometry

        def callback():
            # Update taks
            self.task.description = self.description_textedit.toPlainText()

        def inv_callback():
            # Update widget
            """
            This function is only called when the task's property is
            changed outside this widget. If widget signals are not blocked
            at the time of updating the widget, an infinite recursion is triggered
            between task update and widget update.
            """
            self.description_textedit.blockSignals(True)
            self.description_textedit.setText(self.task.description)
            self.description_textedit.blockSignals(False)
            """
            For some reason, the cursor is normally reset to the start of the 
            widget. One then needs to move the cursor to the end and then reset the cursor
            """
            # Move cursor to the end
            cursor = self.description_textedit.textCursor()
            cursor.movePosition(cursor.Right,
                                cursor.MoveAnchor,
                                len(self.task.description))
            """
            For some other reason, all text is also automatically selected, so one needs to
            clear the selection.
            """
            cursor.clearSelection()
            # Reset cursor
            self.description_textedit.setTextCursor(cursor)# Connect task and widget
        self.description_textedit.textChanged.connect(lambda: callback())
        self.task.description_changed.connect(lambda **kwargs: inv_callback())
        # Set initial value
        inv_callback()
        self.description_textedit.setPlaceholderText("Task description")

    def make_subtask_list_widget(self):
        class SubtaskListWidget(QWidget):
            """
            This widget contains:
                - An icon symbolizing a subtask
                - A list of SubtaskWidget, each corresponding to a subtask
                - A textedit, to add a new subtask with a given name
            """

            def __init__(self,
                         task: Task,
                         parent: QWidget = None):
                """
                :param task: :py:class:'taskplanner.tasks.Task'
                    The task associated to this widget
                :param parent: :py:class:'QWidget', optional
                    The parent widget
                """
                super().__init__(parent=parent)
                self.task = task
                # Layout
                self.layout = QVBoxLayout()
                self.setLayout(self.layout)
                # Icon
                self.make_icon_pushbutton()
                # New Textedit
                self.make_new_textedit()
                # Subtasks
                self.subtask_widgets = []
                self.make_subtask_widgets()

                slots = [slot for slot in self.task.children_changed._slots if 'SubtaskListWidget.' in str(slot)]
                for slot in slots:
                    self.task.children_changed.disconnect(slot)
                self.task.children_changed.connect(lambda **kwargs: self.update_subtasks())

            def make_icon_pushbutton(self):
                self.icon_pushbutton = QPushButton()
                self.layout.addWidget(self.icon_pushbutton)
                # Geometry
                # Icon
                icon_path = self.parent()._style.icon_path
                icon_filename = os.path.join(icon_path, 'subtask.png')
                self.icon_pushbutton.setIcon(QIcon(icon_filename))

            def make_new_textedit(self):
                self.new_textedit = QTextEdit()
                # Layout
                self.layout.addWidget(self.new_textedit)
                # Geometry

                def callback():
                    if '\n' in self.new_textedit.toPlainText():
                        new_task = Task(name=self.new_textedit.toPlainText()[:-1])
                        self.new_textedit.blockSignals(True)
                        self.new_textedit.setText('')
                        self.new_textedit.blockSignals(False)
                        """
                        For some reason, the cursor is normally reset to the start of the 
                        widget. One then needs to move the cursor to the end and then reset the cursor
                        """
                        # Move cursor to the end
                        cursor = self.new_textedit.textCursor()
                        cursor.movePosition(cursor.Left,
                                            cursor.MoveAnchor,
                                            0)
                        """
                        For some other reason, all text is also automatically selected, so one needs to
                        clear the selection.
                        """
                        cursor.clearSelection()
                        # Add new subtask
                        self.task.add_children_tasks(new_task)

                self.new_textedit.textChanged.connect(lambda: callback())
                self.new_textedit.setPlaceholderText("New Subtask")

            def make_subtask_widgets(self):
                for subtask in self.task.children:
                    if subtask not in [widget.task for widget in self.subtask_widgets]:
                        widget = TaskWidgetSimple(parent=self,
                                                  task=subtask)
                        self.layout.addWidget(widget)
                        self.subtask_widgets += [widget]
                # Remove non-existent sub-tasks
                for widget in self.subtask_widgets:
                    if widget.task not in self.task.children:
                        widget.hide()
                        self.subtask_widgets.remove(widget)

            def update_subtasks(self):
                self.make_subtask_widgets()

        self.subtask_list_widget = SubtaskListWidget(task=self.task,
                                                     parent=self)
        self.layout.addWidget(self.subtask_list_widget)



class TaskWidgetSimple(QWidget):
    """
    This widget contains a tree of widgets representing all the subtasks contained in the input task.
    """

    def __init__(self,
                 task: Task,
                 parent: QWidget = None,
                 hide: bool = False):
        """
        :param task:
            the task associated to this widget
        :param parent:
            the parent widget
        :param hide:
            If 'True', the widget is hidden
        """
        self.task = task
        super().__init__(parent=parent)
        # Layout
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)
        # Define style
        self._style = TaskWidgetStyle(font='light',
                                      color_palette='deep purple')
        # This task
        self.task_line_widget = TaskLineWidget(parent=self,
                                               task=self.task)
        self.layout.addWidget(self.task_line_widget)
        # Subtasks
        self.subtask_widgets = []
        self.make_subtasks()

        # Set style
        set_style(widget=self,
                  stylesheets=self._style.stylesheets['simple view'])
        if hide:
            self.hide()

        slots = [slot for slot in self.task.children_changed._slots if 'TaskWidget.' in str(slot)]
        for slot in slots:
            self.task.children_changed.disconnect(slot)
        self.task.children_changed.connect(lambda **kwargs: self.update_widget())

    def update_widget(self):
        self.make_subtasks()
        if not self.task.is_bottom_level:
            self.task_line_widget.expand_pushbutton.show()
        else:
            self.task_line_widget.expand_pushbutton.hide()
    def make_subtasks(self):
        # Add new subtasks
        for subtask in self.task.children:
            if subtask not in [widget.task for widget in self.subtask_widgets]:
                subtask_widget = TaskWidgetSimple(parent=self,
                                                  task=subtask,
                                                  hide=not self.task_line_widget.expanded)
                self.layout.addWidget(subtask_widget)
                self.subtask_widgets += [subtask_widget]
        # Remove non-existent sub-tasks
        for widget in self.subtask_widgets:
            if widget.task not in self.task.children:
                widget.hide()
                self.subtask_widgets.remove(widget)

class TaskLineWidget(QWidget):
    """
    This widget contains:
        - A pushbutton containing the name of the widget
        - The priority level
        - The end date
        - A pushbutton that enables to view the subtasks
    """

    def __init__(self,
                 parent: QWidget,
                 task: Task):
        """
        :param task:
            the task associated to this widget
        :param parent:
            the parent widget
        """
        self.task = task
        super().__init__(parent=parent)
        # Layout
        self.layout = QHBoxLayout()
        self.layout.setAlignment(Qt.AlignLeft)
        self.setLayout(self.layout)
        # Completed pushbutton
        self.make_completed_pushbutton()
        # Name
        self.make_name_pushbutton()
        # Priority
        self.make_priority_label()
        # End date
        self.make_end_date_label()
        # Remove pushbutton
        self.make_remove_pushbutton()
        # Expand pushbutton
        self.expanded = False
        self.make_expand_pushbutton()
        self.layout.addStretch()

    def make_completed_pushbutton(self):
        # Pushbutton to mark the task as completed
        self.completed_pushbutton = QPushButton()
        self.layout.addWidget(self.completed_pushbutton)
        # Icon
        icon_path = self.parent()._style.icon_path
        icon_filename = os.path.join(icon_path,
                                     'ok.png')
        self.completed_pushbutton.setIcon(QIcon(icon_filename))

        def switch_background(completed: bool):
            stylesheet = self.parent()._style.stylesheets['standard view']['toolbar'][
                'completed_pushbutton']
            if completed:
                stylesheet = stylesheet.replace('/* background-color */', 'background-color:%s;/* main */' % (
                    self.parent()._style.color_palette["completed"]))
            else:
                stylesheet = stylesheet.replace(
                    'background-color:%s;/* main */' % (self.parent()._style.color_palette["completed"]),
                    '/* background-color */')
            self.parent()._style.stylesheets['standard view']['toolbar'][
                'completed_pushbutton'] = stylesheet
            self.completed_pushbutton.setStyleSheet(stylesheet)

        def callback():
            self.task.completed = not self.task.completed
            switch_background(self.task.completed)

        # Set Current Value
        switch_background(self.task.completed)
        self.completed_pushbutton.clicked.connect(lambda: callback())
        self.task.completed_changed.connect(
            lambda **kwargs: switch_background(self.task.completed))
    def make_name_pushbutton(self):
        self.name_pushbutton = QPushButton()
        self.layout.addWidget(self.name_pushbutton)

        # Geometry
        # Callback
        def callback():
            task_widget = TaskWidget(task=self.task)
            task_widget.show()

        def update_widget():
            self.name_pushbutton.setText(self.task.name)

        # Connect task and widget
        self.name_pushbutton.clicked.connect(callback)
        self.task.name_changed.connect(lambda **kwargs: update_widget())
        # Set initial text
        update_widget()

    def make_priority_label(self):
        self.priority_label = QLabel()
        self.layout.addWidget(self.priority_label)
        # Geometry

        def update_widget():
            self.priority_label.setText(self.task.priority)

        # Connect task and widget
        self.task.priority_changed.connect(lambda **kwargs: update_widget())
        # Set initial text
        update_widget()

    def make_end_date_label(self):
        self.end_date_label = QLabel()
        self.layout.addWidget(self.end_date_label)
        # Geometry

        def update_widget():
            year, month, day = self.task.end_date.year, \
                self.task.end_date.month, \
                self.task.end_date.day
            self.end_date_label.setText(f'{day}/{month}/{year}')

        # Connect task and widget
        self.task.end_date_changed.connect(lambda **kwargs: update_widget())
        # Set initial text
        update_widget()

    def make_expand_pushbutton(self):
        self.expand_pushbutton = QPushButton()
        self.layout.addWidget(self.expand_pushbutton)
        # Geometry
        # Icon
        icon_path = self.parent()._style.icon_path
        icon_filename = os.path.join(icon_path,
                                     'subtask-widget_not-expanded.png')
        self.expand_pushbutton.setIcon(QIcon(icon_filename))

        # Callback
        def callback():
            self.expanded = not self.expanded
            for subtask_widget in self.parent().subtask_widgets:
                if subtask_widget.isVisible():
                    subtask_widget.hide()
                else:
                    subtask_widget.show()
            # Icon
            icon_path = self.parent()._style.icon_path
            name = 'expanded' if self.expanded else 'not-expanded'
            icon_filename = os.path.join(icon_path,
                                         f'subtask-widget_{name}.png')
            self.expand_pushbutton.setIcon(QIcon(icon_filename))

        self.expand_pushbutton.clicked.connect(callback)
        if self.task.is_bottom_level:
            self.expand_pushbutton.hide()

    def make_remove_pushbutton(self):
        self.remove_pushbutton = QPushButton()
        self.layout.addWidget(self.remove_pushbutton)
        # Geometry
        # Icon
        icon_path = self.parent()._style.icon_path
        icon_filename = os.path.join(icon_path,
                                     'minus.png')
        self.remove_pushbutton.setIcon(QIcon(icon_filename))

        # Callback
        def callback():
            if self.task.parent is not None:
                self.task.parent.remove_children_tasks(self.task)

        self.remove_pushbutton.clicked.connect(callback)


