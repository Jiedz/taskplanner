"""
This module defines a task widget.
"""
import logging
import os
from datetime import date as dt

# %% Imports
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon
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
    QCalendarWidget,
    QColorDialog,
    QFrame
    )
from signalslot import Signal
from taskplanner.gui.styles import TaskWidgetStyle, ICON_SIZES
from taskplanner.gui.utilities import set_style, get_primary_screen
from taskplanner.tasks import Task, PROGRESS_LEVELS, PRIORITY_LEVELS
from taskplanner.planner import Planner

SCREEN = get_primary_screen()
SCREEN_WIDTH = SCREEN.width
SCREEN_HEIGHT = SCREEN.height

# Signals
task_widget_widget_open = Signal()

class TaskWidget(QWidget):
    """
    This class defines a task widget.
    """

    def __init__(self,
                 task: Task,
                 planner: Planner = None,
                 parent: QWidget = None,
                 style: TaskWidgetStyle = None):
        """
        :param task: :py:class:'taskplanner.tasks.Task'
            The task associated to this widget
        :param planner: :py:class:'taskplanner.planner.Planner'
            The planner associated to this task.
        :param parent: :py:class:'QWidget', optional
            The parent widget
        :param style: :py:class:'TaskWidgetStyle', optional
            The widget's style
        """
        self.task, self.planner = task, planner
        super().__init__(parent=parent)
        # Layout
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignHCenter)
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)
        # Geometry
        # Get screen size
        width, height = int(SCREEN_WIDTH * 0.37), int(SCREEN_HEIGHT * 0.65)
        self.setGeometry(int(SCREEN_WIDTH / 2) - int(width / 2),
                         int(SCREEN_HEIGHT / 2) - int(height / 2),
                         width,  # width
                         height)  # height
        # Define style
        self._style = style
        # Scroll area
        self.scrollarea = QScrollArea()
        self.scrollarea.setWidgetResizable(True)
        self.scrollarea.setGeometry(self.geometry())
        self.scrollarea.setWidget(self)
        # Path widget
        self.make_path_widget()
        if self.task.is_top_level:
            self.path_widget.hide()
        # Horizontal layout for (title, color, dates)
        self.title_color_dates_layout = QHBoxLayout()
        self.layout.addLayout(self.title_color_dates_layout)
        # Title widget
        self.make_title_widget()
        self.title_widget.setFixedHeight(int(self.height()*0.08))
        # Color widget
        self.make_color_widget()
        ## Color pushbutton
        #self.color_widget.color_pushbutton.setFixedSize(ICON_SIZES['small'])
        # Start and end date widgets
        self.make_date_widgets()
        self.title_color_dates_layout.addStretch()
        ## Textedit
        self.title_widget.textedit.setFixedHeight(int(self.title_widget.height()))
        self.title_widget.textedit.setMinimumWidth(int(self.width() * 0.5))
        # Horizontal layout for (category, assignee)
        self.category_assignee_layout = QHBoxLayout()
        self.layout.addLayout(self.category_assignee_layout)
        # Category
        self.make_category_widget()
        ## Combobox
        self.category_widget.combobox.setMinimumWidth(int(self.width()*0.2))
        ## New textedit
        self.category_widget.new_textedit.setMaximumWidth(self.category_widget.combobox.width())
        self.category_widget.new_textedit.setMaximumHeight(int(self.category_widget.combobox.height() * 1.5))
        self.category_assignee_layout.addStretch()
        # Assignee
        self.make_assignee_widget()
        ## Combobox
        self.assignee_widget.combobox.setMinimumWidth(int(self.width() * 0.2))
        ## New textedit
        self.assignee_widget.new_textedit.setMaximumWidth(self.category_widget.new_textedit.width())
        self.assignee_widget.new_textedit.setMaximumHeight(self.category_widget.new_textedit.height())
        self.category_assignee_layout.addStretch()
        # Horizontal layout for (priority, start date, end date)
        self.priority_progress_layout = QHBoxLayout()
        self.layout.addLayout(self.priority_progress_layout)
        # Priority
        self.make_priority_widget()
        ## Combobox
        self.priority_widget.combobox.setMinimumWidth(int(self.width() * 0.2))
        self.priority_progress_layout.addStretch()
        # Progress widget
        self.make_progress_widget()
        ## Combobox
        self.progress_widget.combobox.setMinimumWidth(int(self.width() * 0.2))
        self.priority_progress_layout.addStretch()
        # Task Description
        self.make_description_textedit()
        self.description_textedit.setMaximumWidth(int(self.width()*1))
        self.description_textedit.setMinimumHeight(int(self.height() * 0.15))
        # Sub-tasks
        self.make_subtask_list_widget()
        self.subtask_list_widget.setMaximumWidth(int(self.width()*2))
        ## Icon pushbutton
        self.subtask_list_widget.icon_label.setFixedSize(int(self.height()*0.05),
                                                         int(self.height()*0.05))
        ## New textedit
        self.subtask_list_widget.new_textedit.setFixedWidth(int(self.width()*0.5))
        self.subtask_list_widget.new_textedit.setFixedHeight(int(self.category_widget.new_textedit.height()))
        self.layout.addStretch()
        # Set style
        if self._style is not None:
            set_style(widget=self,
                      stylesheets=self._style.stylesheets['standard view'])
        task_widget_widget_open.emit()
        task_widget_widget_open.connect(lambda **kwargs: self.hide())

    def show(self):
        super().show()
        self.scrollarea.show()

    def hide(self):
        super().hide()
        self.scrollarea.hide()


    def make_path_widget(self):
        class PathWidget(QWidget):
            """
            This widget contains:
                - A pushbutton for each super-task
                - A "/" label between each pair of super-tasks, as a separator
            """

            def __init__(self,
                         task: Task,
                         planner: Planner = None,
                         parent: QWidget = None):
                """
                :param task: :py:class:'taskplanner.tasks.Task'
                    The task associated to this widget
                :param planner: :py:class:'taskplanner.planner.Planner'
                    The planner associated to this task.
                :param parent: :py:class:'QWidget', optional
                    The parent widget
                """
                super().__init__(parent=parent)
                self.task, self.planner = task, planner
                # Layout
                self.layout = QHBoxLayout()
                self.setLayout(self.layout)
                # Geometry
                # Icon pushbutton
                self.make_icon_label()
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

            def make_icon_label(self):
                self.icon_label = QLabel()
                self.layout.addWidget(self.icon_label)
                # Icon
                icon_path = self.parent()._style.icon_path
                icon_filename = os.path.join(icon_path, 'supertask.png')
                pixmap = QIcon(icon_filename).pixmap(ICON_SIZES['regular'])
                self.icon_label.setPixmap(pixmap)

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
                    task_widget = TaskWidget(task=supertask,
                                             planner=self.planner,
                                             style=self.parent()._style)
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
                                      planner=self.planner,
                                      parent=self)
        self.layout.addWidget(self.path_widget)

    def make_title_widget(self):
        class TitleWidget(QWidget):
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
                # Textedit
                self.make_textedit()
                self.layout.addStretch()


            def make_textedit(self):
                self.textedit = QTextEdit()
                # Layout
                self.layout.addWidget(self.textedit)
                self.textedit.setAlignment(Qt.AlignLeft)

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

        self.title_widget = TitleWidget(task=self.task,
                                        parent=self)
        self.title_color_dates_layout.addWidget(self.title_widget)

    def make_color_widget(self):
        class ColorWidget(QWidget):
            """
            This task containt:
            - A label that indicates the task's color
            - A push button containing the color of the widget
            - A color picker widget, popping up at the click of the color push button,
             that allows the user to select a new color.
            """
            def __init__(self,
                         task: Task,
                         planner: Planner = None,
                         parent: QWidget = None):
                """
                :param task: :py:class:'taskplanner.tasks.Task'
                    The task associated to this widget
                :param planner: :py:class:'taskplanner.planner.Planner'
                    The planner associated to this task.
                :param parent: :py:class:'QWidget', optional
                    The parent widget
                """
                self.task, self.planner = task, planner
                super().__init__(parent=parent)
                # Layout
                self.layout = QVBoxLayout(self)
                # Label
                self.make_label()
                # Color button
                self.make_color_button()
                # Color picking dialog
                self.make_color_dialog()

            def make_label(self):
                self.label = QLabel('Color')
                self.layout.addWidget(self.label)
                self.label.setAlignment(Qt.AlignLeft)

            def make_color_button(self):
                self.color_pushbutton = QPushButton()
                # Layout
                self.layout.addWidget(self.color_pushbutton)
                # User interactions
                def clicked():
                    if not self.color_dialog.isVisible():
                        self.color_dialog.show()

                def update_color():
                    if self.task.color is None:
                        self.task.color = self.parent()._style.color_palette['background 2']
                    stylesheet = '''
                                QPushButton
                                {
                                    background-color:%s;
                                    border-color:%s;
                                }
                                QPushButton:hover
                                {
                                    border:2px solid %s;
                                }
                                ''' % (self.task.color,
                                       self.parent()._style.color_palette['background 1'],
                                       self.parent()._style.color_palette['text - highlight'])
                    self.parent()._style.stylesheets['standard view']['color_widget']['color_pushbutton'] = stylesheet
                    self.color_pushbutton.setStyleSheet(stylesheet)
                # Connect task and widget
                self.color_pushbutton.clicked.connect(clicked)
                # Keep connecting
                self.task.color_changed.connect(lambda **kwargs: update_color())
                # Set initial value
                update_color()



            def make_color_dialog(self):
                self.color_dialog = QColorDialog()
                # Geometry
                x, y, w, h = [getattr(self.parent().geometry(), f'{z}')() for z in ['x',
                                                                                    'y',
                                                                                    'width',
                                                                                    'height']]
                self.color_dialog.setWindowTitle(f'Widget Color')
                self.color_dialog.setGeometry(int(x + 1.5 * w),
                                                 int(y + h / 2),
                                                 self.color_dialog.width(),
                                                 self.color_dialog.height())
                # User interactions
                def accepted():
                    self.task.color = self.color_dialog.selectedColor().name()

                self.color_dialog.accepted.connect(accepted)

        self.color_widget = ColorWidget(task=self.task,
                                        planner=self.planner,
                                        parent=self)
        self.title_color_dates_layout.addWidget(self.color_widget)

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
                self.layout = QVBoxLayout()
                self.setLayout(self.layout)
                # Label
                self.make_label()
                # Label
                self.make_pushbutton()
                # Calendar widget
                self.make_calendar_widget()

            def make_label(self):
                self.label = QLabel(f'{self.time_mode.title()} Date')
                self.layout.addWidget(self.label)
                self.label.setAlignment(Qt.AlignLeft)

            def make_pushbutton(self):
                self.pushbutton = QPushButton()
                # Layout
                self.layout.addWidget(self.pushbutton)
                # User interactions
                def update_label():
                    date = getattr(self.task, f'{self.time_mode}_date')
                    self.pushbutton.setText(f'{date.day}/{date.month}/{date.year}')

                getattr(self.task, f'{self.time_mode}_date_changed').connect(lambda **kwargs: update_label())
                update_label()

                def clicked():
                    self.calendar_widget.show()

                self.pushbutton.clicked.connect(clicked)



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
        self.title_color_dates_layout.addWidget(self.start_date_widget)
        self.end_date_widget = DateWidget(task=self.task,
                                          parent=self,
                                          time_mode='end')
        self.title_color_dates_layout.addWidget(self.end_date_widget)

    def make_progress_widget(self):
        class ProgressWidget(QWidget):
            """
            This widget contains:
            - A label, indicating progress
            - A combobox containing icons that indicate progress levels
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
                # Label
                self.make_label()
                # Combobox
                self.make_combobox()

            def make_label(self):
                self.label = QLabel('Progress')
                self.layout.addWidget(self.label)
                self.label.setAlignment(Qt.AlignLeft)

            def make_combobox(self):
                self.combobox = QComboBox()
                # Layout
                self.layout.addWidget(self.combobox)
                # Add items
                for i in range(len(PROGRESS_LEVELS)):
                    level = PROGRESS_LEVELS[i]
                    icon_path = self.parent()._style.icon_path
                    icon_filename = os.path.join(icon_path, f'progress_{level.replace(" ", "-")}.png')
                    self.combobox.addItem(level)
                    self.combobox.setItemIcon(i,
                                              QIcon(icon_filename))
                # User interactions
                def clicked():
                    self.task.progress = self.combobox.currentText()
                # Connect task and widget
                self.combobox.currentIndexChanged.connect(clicked)
                self.task.progress_changed.connect(lambda **kwargs: self.combobox.setCurrentText(self.task.progress))
                # Set initial value
                self.combobox.setCurrentText(self.task.progress)

        self.progress_widget = ProgressWidget(task=self.task,
                                        parent=self)
        self.priority_progress_layout.addWidget(self.progress_widget)


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
                         planner: Planner = None,
                         parent: QWidget = None):
                """
                :param task: :py:class:'taskplanner.tasks.Task'
                    The task associated to this widget
                :param planner: :py:class:'taskplanner.planner.Planner'
                    The planner associated to this task.
                :param parent: :py:class:'QWidget', optional
                    The parent widget
                """
                super().__init__(parent=parent)
                self.task, self.planner = task, planner
                # Layout
                self.layout = QVBoxLayout()
                self.setLayout(self.layout)
                self.layout.setAlignment(Qt.AlignLeft)
                # Label
                self.make_label()
                # Horizontal layout for (combobox, add pushbutton)
                self.combobox_add_layout = QHBoxLayout()
                self.layout.addLayout(self.combobox_add_layout)
                # Categories combobox
                self.make_combobox()
                # Add category pushbutton
                self.make_add_pushbutton()
                self.combobox_add_layout.addStretch()
                # New Textedit
                self.make_new_textedit()
                self.layout.addStretch()

            def make_label(self):
                self.label = QLabel('Category')
                self.layout.addWidget(self.label)
                self.label.setAlignment(Qt.AlignLeft)

            def make_combobox(self):
                self.combobox = QComboBox(parent=self)
                # Layout
                self.combobox_add_layout.addWidget(self.combobox)
                # Add categories
                if self.planner is not None:
                    self.combobox.addItems(self.planner.categories)
                elif self.task.category is not None:
                    self.combobox.addItems(self.task.category)
                # User interactions
                def clicked():
                    self.task.category = self.combobox.currentText()
                # Connect task and widget
                self.combobox.currentIndexChanged.connect(clicked)
                self.task.category_changed.connect(
                    lambda **kwargs: self.combobox.setCurrentText(self.task.category))
                # Connect planner and widget
                if self.planner is not None:
                    def update_categories():
                        self.combobox.blockSignals(True)
                        for i in range(self.combobox.count()):
                            self.combobox.removeItem(0)
                        self.combobox.addItems(self.planner.categories)
                        self.combobox.setCurrentText(self.task.category)
                        self.combobox.blockSignals(False)
                    self.planner.categories_changed.connect(lambda **kwargs: update_categories())
                # Set initial value
                self.combobox.setCurrentText(self.task.category)

            def make_add_pushbutton(self):
                # Pushbutton to mark the task as add
                self.add_pushbutton = QPushButton()
                self.combobox_add_layout.addWidget(self.add_pushbutton)
                # Icon
                icon_path = self.parent()._style.icon_path
                icon_filename = os.path.join(icon_path, 'add.png')
                self.add_pushbutton.setIcon(QIcon(icon_filename))
                # User interactions
                def callback():
                    # Show the new textedit
                    self.new_textedit.setText('')
                    self.new_textedit.show()

                self.add_pushbutton.clicked.connect(lambda: callback())

            def make_new_textedit(self):
                # textedit to define a new assignee when the 'plus' button is clicked
                self.new_textedit = QTextEdit()
                # Layout
                self.layout.addWidget(self.new_textedit)

                def callback():
                    text = self.new_textedit.toPlainText()
                    if '\n' in text:
                        text = text.replace('\n', '')
                        all_items = [self.combobox.itemText(i) for i in range(self.combobox.count())]
                        if text not in all_items:
                            self.combobox.addItem(text)
                            self.task.category = text if text != '' else None
                            if self.planner is not None:
                                self.planner.add_categories(self.task.category)
                        self.new_textedit.hide()

                self.new_textedit.textChanged.connect(lambda: callback())
                self.new_textedit.setPlaceholderText("+ New Category")
                self.new_textedit.hide()

        self.category_widget = CategoryWidget(task=self.task,
                                              planner=self.planner,
                                              parent=self)
        self.category_assignee_layout.addWidget(self.category_widget)

    def make_assignee_widget(self):
        class AssigneeWidget(QWidget):
            """
            This widget contains:

                - A combobox of assignee names
                - A "+" button to add a new assignee
                - A linedit that pops up when the "+" button is clicked
            """

            def __init__(self,
                         task: Task,
                         planner: Planner = None,
                         parent: QWidget = None):
                """
                :param task: :py:class:'taskplanner.tasks.Task'
                    The task associated to this widget
                :param planner: :py:class:'taskplanner.planner.Planner'
                    The planner associated to this task.
                :param parent: :py:class:'QWidget', optional
                    The parent widget
                """
                super().__init__(parent=parent)
                self.task, self.planner = task, planner
                # Layout
                self.layout = QVBoxLayout()
                self.setLayout(self.layout)
                self.layout.setAlignment(Qt.AlignLeft)
                # Label
                self.make_label()
                # Horizontal layout for (combobox, add pushbutton)
                self.combobox_add_layout = QHBoxLayout()
                self.layout.addLayout(self.combobox_add_layout)
                # Categories combobox
                self.make_combobox()
                # Add category pushbutton
                self.make_add_pushbutton()
                self.combobox_add_layout.addStretch()
                # New Textedit
                self.make_new_textedit()
                self.layout.addStretch()

            def make_label(self):
                self.label = QLabel('Assignee')
                self.layout.addWidget(self.label)
                self.label.setAlignment(Qt.AlignLeft)

            def make_combobox(self):
                self.combobox = QComboBox(parent=self)
                # Layout
                self.combobox_add_layout.addWidget(self.combobox)
                # Add items
                if self.planner is not None:
                    self.combobox.addItems(self.planner.assignees)
                elif self.task.assignee is not None:
                    self.combobox.addItems(self.task.assignee)
                # User interactions
                def clicked():
                    self.task.assignee = self.combobox.currentText()
                # Connect task and widget
                self.combobox.currentIndexChanged.connect(clicked)
                self.task.assignee_changed.connect(
                    lambda **kwargs: self.combobox.setCurrentText(self.task.assignee))
                # Connect planner and widget
                if self.planner is not None:
                    def update_assignees():
                        self.combobox.blockSignals(True)
                        for i in range(self.combobox.count()):
                            self.combobox.removeItem(0)
                        self.combobox.addItems(self.planner.assignees)
                        self.combobox.setCurrentText(self.task.assignee)
                        self.combobox.blockSignals(False)
                    self.planner.assignees_changed.connect(lambda **kwargs: update_assignees())
                # Set initial value
                self.combobox.setCurrentText(self.task.assignee)

            def make_add_pushbutton(self):
                # Pushbutton to mark the task as add
                self.add_pushbutton = QPushButton()
                self.combobox_add_layout.addWidget(self.add_pushbutton)
                # Icon
                icon_path = self.parent()._style.icon_path
                icon_filename = os.path.join(icon_path, 'add.png')
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
                    text = self.new_textedit.toPlainText()
                    if '\n' in text:
                        text = text.replace('\n', '')
                        all_items = [self.combobox.itemText(i) for i in range(self.combobox.count())]
                        if text not in all_items:
                            self.combobox.addItem(text)
                            self.task.assignee = text if text != '' else None
                            if self.planner is not None:
                                self.planner.add_assignees(self.task.assignee)
                        self.new_textedit.hide()

                self.new_textedit.textChanged.connect(lambda: callback())
                self.new_textedit.setPlaceholderText("+ New Assignee")
                self.new_textedit.hide()

        self.assignee_widget = AssigneeWidget(task=self.task,
                                              parent=self,
                                              planner=self.planner)
        self.category_assignee_layout.addWidget(self.assignee_widget)

    def make_priority_widget(self):
        class PriorityWidget(QWidget):
            """
            This widget contains:
            - A label, indicating priority
            - A combobox containing icons that indicate priority levels
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
                # Label
                self.make_label()
                # Combobox
                self.make_combobox()

            def make_label(self):
                self.label = QLabel('Priority')
                self.layout.addWidget(self.label)
                self.label.setAlignment(Qt.AlignLeft)

            def make_combobox(self):
                self.combobox = QComboBox()
                # Layout
                self.layout.addWidget(self.combobox)
                # Add items
                for i in range(len(PRIORITY_LEVELS)):
                    level = PRIORITY_LEVELS[len(PRIORITY_LEVELS)-i-1]
                    icon_path = self.parent()._style.icon_path
                    icon_filename = os.path.join(icon_path, f'priority_{level.replace(" ", "-")}.png')
                    self.combobox.addItem(level)
                    self.combobox.setItemIcon(i,
                                              QIcon(icon_filename))
                # User interactions
                def clicked():
                    self.task.priority = self.combobox.currentText()
                # Connect task and widget
                self.combobox.currentIndexChanged.connect(clicked)
                self.task.priority_changed.connect(lambda **kwargs: self.combobox.setCurrentText(self.task.priority))
                # Set initial value
                self.combobox.setCurrentText(self.task.priority)

        self.priority_widget = PriorityWidget(task=self.task,
                                              parent=self)
        self.priority_progress_layout.addWidget(self.priority_widget)

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
                         planner: Planner = None,
                         parent: QWidget = None):
                """
                :param task: :py:class:'taskplanner.tasks.Task'
                    The task associated to this widget
                :param planner: :py:class:'taskplanner.planner.Planner'
                    The planner associated to this task.
                :param parent: :py:class:'QWidget', optional
                    The parent widget
                """
                super().__init__(parent=parent)
                self.task, self.planner = task, planner
                # Layout
                self.layout = QVBoxLayout()
                self.setLayout(self.layout)
                # Icon
                self.make_icon_label()
                # New Textedit
                self.make_new_textedit()
                # Subtasks
                self.subtask_widgets = []
                self.make_subtask_widgets()

                slots = [slot for slot in self.task.children_changed._slots if 'SubtaskListWidget.' in str(slot)]
                for slot in slots:
                    self.task.children_changed.disconnect(slot)
                self.task.children_changed.connect(lambda **kwargs: self.make_subtask_widgets())

            def make_icon_label(self):
                
                self.icon_label = QLabel()
                self.layout.addWidget(self.icon_label)
                # Icon
                icon_path = self.parent()._style.icon_path
                icon_filename = os.path.join(icon_path, 'subtask.png')
                pixmap = QIcon(icon_filename).pixmap(ICON_SIZES['regular'])
                self.icon_label.setPixmap(pixmap)

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
                self.new_textedit.setPlaceholderText("+ New Subtask")

            def make_subtask_widgets(self):
                for subtask in self.task.children:
                    if subtask not in [widget.task for widget in self.subtask_widgets]:
                        widget = TaskWidgetSimple(parent=self,
                                                  task=subtask,
                                                  planner=self.planner,
                                                  style=self.parent()._style
                                                  )
                        self.layout.addWidget(widget)
                        self.subtask_widgets += [widget]
                # Remove non-existent sub-tasks
                for widget in self.subtask_widgets:
                    if widget.task not in self.task.children:
                        widget.hide()
                        self.subtask_widgets.remove(widget)

        self.subtask_list_widget = SubtaskListWidget(task=self.task,
                                                     planner=self.planner,
                                                     parent=self)
        self.layout.addWidget(self.subtask_list_widget)


class TaskWidgetSimple(QWidget):
    """
    This widget contains a tree of widgets representing all the subtasks contained in the input task.
    """

    def __init__(self,
                 task: Task,
                 planner: Planner = None,
                 parent: QWidget = None,
                 hide: bool = False,
                 style: TaskWidgetStyle = TaskWidgetStyle()):
        """
        :param task:
            the task associated to this widget
        :param parent:
            the parent widget
        :param hide:
            If 'True', the widget is hidden
        """
        self.task, self.planner = task, planner
        self.is_visible = True
        super().__init__(parent=parent)
        # Layout
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)
        # Define style
        self._style = style
        # This task
        self.task_line_widget = TaskLineWidget(parent=self,
                                               task=self.task,
                                               planner=self.planner,
                                               style=self._style)
        ## Offset the task line widget to the right, by an amount proportional to its depth in the task tree
        ## up to the main task. The latter may not necessarily be a top-level task.
        self.setContentsMargins(int(SCREEN_WIDTH*0.005)*len(self.task.ancestors),
                                0,
                                int(SCREEN_WIDTH*0.003),
                                0)
        self.layout.setContentsMargins(int(SCREEN_WIDTH*0.005)*len(self.task.ancestors),
                                       0,
                                       int(SCREEN_WIDTH * 0.003),
                                       0)
        self.layout.addWidget(self.task_line_widget)
        self.visibility_changed = Signal()
        # Subtasks
        self.subtask_widgets = []
        self.make_subtasks()

        # Set style
        if self._style is not None:
            set_style(widget=self,
                      stylesheets=self._style.stylesheets['simple view'])
        if hide:
            self.hide()
        else:
            self.show()

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
                                                  planner=self.planner,
                                                  hide=True,#not self.task_line_widget.expanded,
                                                  style=self._style
                                                  )
                self.layout.addWidget(subtask_widget)
                self.subtask_widgets += [subtask_widget]
        # Remove non-existent sub-tasks
        for widget in self.subtask_widgets:
            if widget.task not in self.task.children:
                widget.hide()
                self.subtask_widgets.remove(widget)
                self.layout.removeWidget(widget)


    def show(self):
        super().show()
        self.is_visible = True
        self.visibility_changed.emit()

    def hide(self):
        super().hide()
        self.is_visible = False
        self.visibility_changed.emit()


class TaskLineWidget(QFrame):
    """
    This widget contains:
        - A pushbutton containing the name of the widget
        - The priority level
        - The end date
        - A pushbutton that allows to view the subtasks
    """

    def __init__(self,
                 task: Task,
                 planner: Planner = None,
                 parent: QWidget = None,
                 style: TaskWidgetStyle = TaskWidgetStyle()):
        """
        :param task:
            the task associated to this widget
        :param parent:, optional
            the parent widget
        :param style: :py:class:'TaskWidgetStyle', optional
            The widget's style
        """
        self.task, self.planner = task, planner
        self._style = style
        super().__init__(parent=parent)
        # Layout
        self.layout = QHBoxLayout(self)
        self.layout.setAlignment(Qt.AlignLeft)
        # Priority
        self.make_priority_label()
        # Progress
        self.make_progress_label()
        # Name
        self.make_name_pushbutton()
        # End date
        self.make_end_date_label()
        # Remove pushbutton
        self.make_remove_pushbutton()
        # Expand pushbutton
        self.expanded = False
        self.make_expand_pushbutton()
        self.layout.addStretch()
        # Set style
        self.set_style()
        self.task.color_changed.connect(lambda **kwargs: self.set_style())

    def set_style(self):
        if self._style is not None:
            self._style.stylesheets['simple view']['task_line_widget']['main'] \
                = '''
                  QWidget
                  {
                    border:2px solid %s;
                  }
                  ''' % self.task.color
            set_style(widget=self,
                      stylesheets=self._style.stylesheets
                      ['simple view']
                      ['task_line_widget'])


    def make_name_pushbutton(self):
        self.name_pushbutton = QPushButton()
        self.layout.addWidget(self.name_pushbutton)

        # Geometry
        # Callback
        def clicked():
            task_widget = TaskWidget(task=self.task,
                                     planner=self.planner,
                                     style=self._style)
            task_widget.show()

        def update_widget():
            self.name_pushbutton.setText(self.task.name)

        # Connect task and widget
        self.name_pushbutton.clicked.connect(clicked)
        self.task.name_changed.connect(lambda **kwargs: update_widget())
        # Set initial text
        update_widget()

    def make_priority_label(self):
        self.priority_label = QLabel()
        # Layout
        self.layout.addWidget(self.priority_label)
        # Geometry

        def update_widget():
            # Set icon
            icon_path = self.parent()._style.icon_path
            icon_filename = os.path.join(icon_path, f'priority_{self.task.priority}.png')
            pixmap = QIcon(icon_filename).pixmap(ICON_SIZES['small'])
            self.priority_label.setPixmap(pixmap)

        # Connect task and widget
        self.task.priority_changed.connect(lambda **kwargs: update_widget())
        # Set initial text
        update_widget()

    def make_progress_label(self):
        self.progress_label = QLabel()
        # Layout
        self.layout.addWidget(self.progress_label)
        # Geometry

        def update_widget():
            # Set icon
            icon_path = self.parent()._style.icon_path
            icon_filename = os.path.join(icon_path, f'progress_{self.task.progress.replace(" ", "-")}.png')
            pixmap = QIcon(icon_filename).pixmap(ICON_SIZES['small'])
            self.progress_label.setPixmap(pixmap)

        # Connect task and widget
        self.task.progress_changed.connect(lambda **kwargs: update_widget())
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
            # Hide or show all descendant TaskWidgetSimple according to the expanded state of this TaskLineWidget
            def set_visibilities(task_widget: TaskWidgetSimple):
                if task_widget.parent().task_line_widget.expanded:
                    task_widget.show()
                else:
                    task_widget.hide()
                for subtask_widget in task_widget.subtask_widgets:
                    set_visibilities(subtask_widget)

            for subtask_widget in self.parent().subtask_widgets:
                set_visibilities(subtask_widget)
            # Set icon
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
                                     'remove.png')
        self.remove_pushbutton.setIcon(QIcon(icon_filename))

        # Callback
        def callback():
            if not self.task.is_top_level:
                self.task.parent.remove_children_tasks(self.task)
            elif self.planner is not None:
                self.planner.remove_tasks(self.task)
                self.hide()

        self.remove_pushbutton.clicked.connect(callback)


