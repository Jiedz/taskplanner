"""
This module defines a planner widget and related widgets.
"""
from PyQt5.QtCore import Qt, QPoint, QDate, QEvent
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
    QTabWidget,
    QFrame,
    QGridLayout,
    )

from signalslot import Signal
import os
from logging import warning
from numpy import floor, ceil
from datetime import date
from dateutil.relativedelta import relativedelta
from taskplanner.tasks import Task
from taskplanner.planner import Planner
from taskplanner.gui.tasks import TaskWidget, TaskWidgetSimple
from taskplanner.gui.styles import TaskWidgetStyle, PlannerWidgetStyle, ICON_SIZES
from taskplanner.gui.utilities import set_style, get_primary_screen, select_file, select_directory

SCREEN = get_primary_screen()
SCREEN_WIDTH = SCREEN.width
SCREEN_HEIGHT = SCREEN.height

DEFAULT_PLANNER_STYLE = PlannerWidgetStyle(color_palette='dark material',
                                           font='light')

TIMELINE_VIEW_TYPES = ['daily',
                       'weekly',
                       'monthly']


class PlannerWidget(QTabWidget):
    """
    This widget contains:
        - A tab containing the planner widget
        - A tab containing top-level task widgets, grouped by a user-chosen property
    """
    def __init__(self,
                 planner: Planner,
                 parent: QWidget = None,
                 style: PlannerWidgetStyle = DEFAULT_PLANNER_STYLE):
        """

        :param planner: :py:class:'taskplanner.planner.Planner'
            The planner associated to this widget
        :param parent: :py:class:'QWidget', optional
            The parent widget
        :param style: :py:class:'PlannerWidgetStyle', optional
            The widget's style
        """
        self.planner, self._style = planner, style
        super().__init__(parent=parent)
        # Layout
        self.layout = QHBoxLayout(self)
        # Geometry
        width, height = int(SCREEN_WIDTH*0.9), int(SCREEN_HEIGHT*0.9)
        self.setFixedSize(width,
                          height)
        # Planner tab
        self.make_planner_tab()
        # Sorted tasks
        # Set style
        if self._style is not None:
            set_style(widget=self,
                      stylesheets=self._style.stylesheets['main'])
        self.planner.tasks_changed.connect(lambda **kwargs: self.to_file())

    def closeEvent(self, a0):
        self.to_file()
        a0.accept()

    def make_planner_tab(self):
        class PlannerTab(QWidget):
            """
            This widget contains:
                - On the left, a widget containing vertical list of :py:class:'taskplanner.gui.TaskWidgetSimple' of top-level tasks
                - On the right, a widget containing timelines corresponding to each task and its related subtasks
            """
            def __init__(self,
                         planner: Planner,
                         parent: QWidget = None,
                         style: PlannerWidgetStyle = DEFAULT_PLANNER_STYLE
                         ):
                """
                :param planner: :py:class:'taskplanner.planner.Planner'
                    The planner associated to this widget
                :param parent: :py:class:'QWidget', optional
                    The parent widget
                """
                self.planner, self._style = planner, style
                super().__init__(parent=parent)
                # Layout
                self.layout = QVBoxLayout(self)
                self.layout.setAlignment(Qt.AlignTop)
                # Geometry
                self.setGeometry(self.parent().geometry())
                # Horizontal layout for (new task textedit, planner settings)
                self.new_task_settings_layout = QHBoxLayout()
                self.new_task_settings_layout.setAlignment(Qt.AlignLeft)
                self.layout.addLayout(self.new_task_settings_layout)
                # New task textedit
                self.make_new_task_textedit()
                self.new_task_textedit.setFixedSize(int(self.width() * 0.15),
                                                    int(self.height() * 0.035))
                # Upload task pushbutton
                self.make_upload_task_pushbutton()
                self.upload_task_pushbutton.setFixedSize(self.upload_task_pushbutton.iconSize())
                self.new_task_settings_layout.addSpacing(int(SCREEN_WIDTH * 0.25)
                                                         - self.new_task_textedit.width()
                                                         - self.upload_task_pushbutton.width())
                # Vertical layout for task list widget
                self.task_list_layout = QVBoxLayout()
                self.task_list_layout.setAlignment(Qt.AlignTop)
                # Horizontal layout for calendar widget
                self.calendar_layout = QHBoxLayout()
                self.calendar_layout.setAlignment(Qt.AlignLeft)
                self.layout.addLayout(self.calendar_layout)
                self.calendar_layout.addLayout(self.task_list_layout)
                # Horizontal layout for task list and timelines
                self.task_timelines_layout = QHBoxLayout()
                self.task_timelines_layout.setAlignment(Qt.AlignLeft)
                self.layout.addLayout(self.task_timelines_layout)
                # Task list widget
                self.make_task_list_widget()
                ## Scroll area
                self.task_list_scrollarea = QScrollArea()
                self.task_list_scrollarea.setWidgetResizable(True)
                self.task_list_scrollarea.setWidget(self.task_list_widget)
                self.task_list_layout.addWidget(self.task_list_scrollarea)
                self.task_list_scrollarea.setFixedWidth(int(SCREEN_WIDTH * 0.25))
                # Calendar widget
                self.make_calendar_widget()
                ## Scroll area
                self.calendar_scrollarea = QScrollArea()
                self.calendar_scrollarea.setWidgetResizable(True)
                self.calendar_scrollarea.setWidget(self.calendar_widget)
                self.calendar_layout.addWidget(self.calendar_scrollarea)
                self.task_timelines_layout.addLayout(self.calendar_widget.timelines_layout)
                # Adjust task list widget vertical position
                self.task_list_layout.insertSpacing(0,
                                                    self.calendar_widget.month_widgets[0].height())
                # View selector
                self.make_view_selector()
                task_widget_example = TaskWidget(task=Task(),
                                                 style=TaskWidgetStyle(color_palette=self._style.color_palette_name,
                                                                       font=self._style.font_name))
                self.view_selector.combobox.setGeometry(task_widget_example.priority_widget.combobox.geometry())
                self.view_selector.setFixedSize(int(SCREEN_WIDTH * 0.08),
                                                int(self.height() * 0.08))
                # Calendar start and end dates
                self.make_start_end_dates()
                self.start_date_widget.setFixedSize(int(SCREEN_WIDTH * 0.05),
                                                int(self.height() * 0.05))
                self.end_date_widget.setFixedSize(int(SCREEN_WIDTH * 0.05),
                                                    int(self.height() * 0.05))


                if self._style is not None:
                    set_style(widget=self,
                              stylesheets=self._style.stylesheets
                              ['planner_tab']['main'])
                    set_style(widget=self,
                              stylesheets=self._style.stylesheets
                              ['planner_tab']['task_list_scrollarea'])
                    set_style(widget=self,
                              stylesheets=self._style.stylesheets
                              ['planner_tab']['calendar_scrollarea'])
                    set_style(widget=self,
                              stylesheets=self._style.stylesheets
                              ['planner_tab']['new_task_textedit'])

                # Lock the vertical scrollbars of the timelines and the task list
                self.calendar_scrollarea.setVerticalScrollBar(self.task_list_scrollarea.verticalScrollBar())


            def make_new_task_textedit(self):
                # textedit to define a new assignee when the 'plus' button is clicked
                self.new_task_textedit = QTextEdit()
                # Layout
                self.new_task_settings_layout.addWidget(self.new_task_textedit)

                def callback():
                    if '\n' in self.new_task_textedit.toPlainText():
                        new_task = Task(name=self.new_task_textedit.toPlainText()[:-1])
                        self.new_task_textedit.blockSignals(True)
                        self.new_task_textedit.setText('')
                        self.new_task_textedit.blockSignals(False)
                        """
                        For some reason, the cursor is normally reset to the start of the 
                        widget. One then needs to move the cursor to the end and then reset the cursor
                        """
                        # Move cursor to the end
                        cursor = self.new_task_textedit.textCursor()
                        cursor.movePosition(cursor.Left,
                                            cursor.MoveAnchor,
                                            0)
                        """
                        For some other reason, all text is also automatically selected, so one needs to
                        clear the selection.
                        """
                        cursor.clearSelection()
                        # Add new subtask
                        self.planner.add_tasks(new_task)

                self.new_task_textedit.textChanged.connect(lambda: callback())
                self.new_task_textedit.setPlaceholderText("+ New Task")

            def make_upload_task_pushbutton(self):
                self.upload_task_pushbutton = QPushButton()
                self.new_task_settings_layout.addWidget(self.upload_task_pushbutton)
                # Icon
                icon_path = self._style.icon_path
                icon_filename = os.path.join(icon_path, 'upload.png')
                self.upload_task_pushbutton.setIcon(QIcon(icon_filename))

                # User interactions
                def callback():
                    # Show the new textedit
                    filename = select_file(title=f'Select the File Containing the Task to Be Uploaded')
                    try:
                        self.planner.add_tasks(Task.from_file(filename=filename))
                    except Exception as e:
                        print(e)

                self.upload_task_pushbutton.clicked.connect(lambda: callback())
                # Set style
                if self._style is not None:
                    set_style(widget=self.upload_task_pushbutton,
                              stylesheets=self._style.stylesheets
                              ['planner_tab']
                              ['upload_task_pushbutton'])

            def make_view_selector(self):
                class ViewSelector(QFrame):
                    """
                    This widget contains:
                        - A label indicating that this is a view selector
                        - A combobox containing the view types
                    """

                    def __init__(self,
                                 calendar_widget: CalendarWidget,
                                 parent: QWidget = None,
                                 style: PlannerWidgetStyle = None):
                        self._style = style
                        self.calendar_widget = calendar_widget
                        super().__init__(parent=parent)
                        # Layout
                        self.layout = QVBoxLayout(self)
                        # Label
                        self.make_label()
                        # Combobox
                        self.make_combobox()
                        # Style
                        if self._style is not None:
                            set_style(widget=self,
                                      stylesheets=self._style.stylesheets
                                      ['planner_tab']
                                      ['view_selector'])
                        self.layout.addStretch()

                    def make_label(self):
                        self.label = QLabel('Planner View')
                        self.layout.addWidget(self.label)
                        self.label.setAlignment(Qt.AlignLeft)

                    def make_combobox(self):
                        self.combobox = QComboBox()
                        # Layout
                        self.layout.addWidget(self.combobox)
                        # Add items
                        self.combobox.addItems([view.title() for view in TIMELINE_VIEW_TYPES])

                        # User interactions
                        def clicked():
                            self.calendar_widget.view_type = self.combobox.currentText().lower()

                        def update():
                            self.combobox.blockSignals(True)
                            self.combobox.setCurrentText(self.calendar_widget.view_type.title())
                            self.combobox.blockSignals(False)

                        # Connect task and widget
                        self.combobox.currentIndexChanged.connect(clicked)
                        self.calendar_widget.view_type_changed.connect(lambda **kwargs: update())
                        # Set initial value
                        update()

                self.view_selector = ViewSelector(calendar_widget=self.calendar_widget,
                                                  parent=self,
                                                  style=self._style)
                self.new_task_settings_layout.addWidget(self.view_selector)


            def make_task_list_widget(self):
                self.task_list_widget = TaskListWidget(planner=self.planner,
                                                       parent=self)

            def make_calendar_widget(self):
                self.calendar_widget = CalendarWidget(planner=self.planner,
                                                        task_list_widget=self.task_list_widget,
                                                        parent=self,
                                                        start_date=date.today(),
                                                        end_date=date.today() + relativedelta(months=6),
                                                        style=self._style)

            def make_start_end_dates(self):
                class DateWidget(QWidget):
                    """
                    This widget contains:
                        - An icon symbolizing the type of time mode (start, end, ...)
                        - A label indicating the selected date
                        - A calendar widget that allows the user to select a day
                    """

                    def __init__(self,
                                 planner: Planner,
                                 calendar_timelines_widget: CalendarWidget,
                                 parent: QWidget = None,
                                 time_mode: str = 'start',
                                 style: PlannerWidgetStyle = None):
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
                            raise ValueError(
                                f'Unrecognized time more {time_mode}. Possible time modes are {tuple(TIME_MODES)}')
                        self.planner = planner
                        self.calendar_timelines_widget = calendar_timelines_widget
                        self.time_mode = time_mode
                        self._style = style
                        super().__init__(parent=parent)
                        # Layout
                        self.layout = QVBoxLayout()
                        self.setLayout(self.layout)
                        self.layout.setContentsMargins(0, 0, 0, 0)
                        # Label
                        self.make_label()
                        # Label
                        self.make_pushbutton()
                        # Calendar widget
                        self.make_calendar_widget()
                        if self._style is not None:
                            set_style(widget=self,
                                      stylesheets=self._style.stylesheets
                                      ['planner_tab']
                                      [f'{self.time_mode}_date_widget'])

                    def make_label(self):
                        self.label = QLabel(f'{self.time_mode.title()} Date')
                        self.layout.addWidget(self.label)
                        self.label.setAlignment(Qt.AlignCenter)

                    def make_pushbutton(self):
                        self.pushbutton = QPushButton()
                        # Layout
                        self.layout.addWidget(self.pushbutton)
                        # Connect tasks and date widget
                        for task in self.planner.tasks:
                            all_descendants = [task] + list(task.descendants)
                            for t in all_descendants:
                                getattr(t, f'{self.time_mode}_date_changed').connect
                                (lambda **kwargs: self.update_label())
                        self.update_label()

                        def clicked():
                            self.calendar_widget.show()
                            self.calendar_widget.blockSignals(True)
                            current_date = getattr(self.calendar_timelines_widget, f'{self.time_mode}_date')
                            self.calendar_widget.setSelectedDate(QDate(current_date.year,
                                                                       current_date.month,
                                                                       current_date.day))
                            self.calendar_widget.blockSignals(False)

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
                        self.calendar_widget.setGeometry(int(x + 1.5 * w),
                                                         int(y + h / 2),
                                                         self.calendar_widget.width(),
                                                         self.calendar_widget.height())

                        def callback():
                            from datetime import date as dt
                            # Get the extreme start and end dates among all tasks of the planner
                            first_start_date, last_end_date = [], []
                            for task in self.planner.tasks:
                                first_start_date += [min([t.start_date for t in [task] + list(task.descendants)])]
                                last_end_date += [max([t.end_date for t in [task] + list(task.descendants)])]
                            if first_start_date:
                                first_start_date = min(first_start_date)
                            else:
                                first_start_date = dt.today()
                            if last_end_date:
                                last_end_date = max(last_end_date)
                            else:
                                last_end_date = first_start_date + relativedelta(months=6)
                            # Get date from calendar
                            date = self.calendar_widget.selectedDate()
                            date = dt(year=date.year(), month=date.month(), day=1)
                            if self.time_mode == 'start':
                                if date > self.calendar_timelines_widget.end_date:
                                    warning(f'CalendarWidget: start date {date.strftime("%d/%m/%y")} '
                                            f'is greater than end date '
                                            f'{self.calendar_timelines_widget.end_date.strftime("%d/%m/%y")}')
                                    date = dt.today()
                                    date = dt(date.year, date.month, 1)
                                    self.calendar_timelines_widget.end_date = date + relativedelta(months=6)
                            else:
                                if date < self.calendar_timelines_widget.start_date:
                                    warning(f'CalendarWidget: end date {date.strftime("%d/%m/%y")} '
                                            f'is smaller than end date '
                                            f'{self.calendar_timelines_widget.start_date.strftime("%d/%m/%y")}')
                                    date = self.calendar_timelines_widget.start_date + relativedelta(months=6)
                                    date = dt(date.year, date.month, 1)

                            if self.time_mode == 'start' and date <= first_start_date\
                                or self.time_mode == 'end' and date >= last_end_date:
                                # Set date to calendar
                                setattr(self.calendar_timelines_widget, f'{self.time_mode}_date', date)

                            self.update_label()
                            # Hide calendar
                            self.calendar_widget.hide()

                        self.calendar_widget.clicked.connect(callback)

                    # User interactions
                    def update_label(self):
                        # Get the extreme start and end dates among all tasks of the planner
                        from datetime import date as dt
                        first_start_date, last_end_date = [], []
                        for task in self.planner.tasks:
                            first_start_date += [min([t.start_date for t in [task] + list(task.descendants)])]
                            last_end_date += [max([t.end_date for t in [task] + list(task.descendants)])]
                        if first_start_date:
                            first_start_date = min(first_start_date)
                        else:
                            first_start_date = dt.today()
                        if last_end_date:
                            last_end_date = max(last_end_date)
                        else:
                            last_end_date = first_start_date + relativedelta(months=6)

                        date = first_start_date if self.time_mode == 'start' else last_end_date
                        date = dt(date.year, date.month, 1)
                        if date < self.calendar_timelines_widget.start_date \
                            or date > self.calendar_timelines_widget.end_date:
                            setattr(self.calendar_timelines_widget, f'{self.time_mode}_date', date)
                        else:
                            date = getattr(self.calendar_timelines_widget, f'{self.time_mode}_date')
                            date = dt(date.year, date.month, 1)
                        # Handle the definition of end date in the calendar widget, which includes the whole month
                        if self.time_mode == 'end':
                            date += relativedelta(months=1)
                        self.pushbutton.setText(f'{date.day}/{date.month}/{date.year}')

                self.new_task_settings_layout.addSpacing(int(self.width() * 0.1))
                self.start_date_widget = DateWidget(planner=self.planner,
                                                    calendar_timelines_widget=self.calendar_widget,
                                                    parent=self,
                                                    time_mode='start',
                                                    style=self._style)
                self.new_task_settings_layout.addWidget(self.start_date_widget)

                self.new_task_settings_layout.addSpacing(int(self.width() * 0.1))

                self.end_date_widget = DateWidget(planner=self.planner,
                                                    calendar_timelines_widget=self.calendar_widget,
                                                    parent=self,
                                                    time_mode='end',
                                                    style=self._style)
                self.new_task_settings_layout.addWidget(self.end_date_widget)


        self.planner_tab = PlannerTab(planner=self.planner,
                                      parent=self,
                                      style=self._style)
        self.addTab(self.planner_tab, 'Planner')

    def to_string(self):
        # Write all the data except subtasks first
        string = '___PLANNER WIDGET___'
        # Add style
        string += f'\n{self._style.to_string()}'
        # Add planner
        string += f'\n{self.planner.to_string()}'
        return string

    @classmethod
    def from_string(cls,
                    string: str):
        s = ''.join(string.split('___PLANNER WIDGET___')[1:])
        # Planner
        planner_string = '___PLANNER___'+s.split('___PLANNER___')[1]
        planner = Planner.from_string(planner_string)
        string = s.split('___PLANNER___')[0]
        # Style
        style_string = '___PLANNER WIDGET STYLE___'+s.split('___PLANNER WIDGET STYLE___')[1]
        style = PlannerWidgetStyle.from_string(style_string)
        string = s.split('___PLANNER WIDGET STYLE___')[0]
        widget = PlannerWidget(planner=planner,
                               style=style)
        return widget

    def to_file(self,
                filename: str = None,
                access_mode: str = 'r+'):
        '''
        Writes the content of the tree into a .txt file.

        Parameters
        ----------
        filename : str, optional
            The absolute path of the file where the object tree is saved.


        Returns
        -------
        None.

        '''
        # Recognize the input file name or use the internally defined file name, if any.
        # Else, raise an error.
        if filename is None:
            if not hasattr(self, 'filename'):
                from taskplanner.gui.utilities import select_file
                filename = select_file(title=f'Select an empty configuration file'
                                             f'to save the task planner.')
                self.filename = filename
            else:
                directory = os.path.sep.join(os.path.abspath(self.filename).split(os.path.sep)[:-1])
                if not os.path.exists(directory):
                    warning(f'No such directory "{directory}". Asking user to select '
                                     f'an empty configuration file')
                    from taskplanner.gui.utilities import select_file
                    filename = select_file(title=f'Select an empty configuration file '
                                                 f'to save task planner')
                    self.filename = filename
        else:
            directory = os.path.sep.join(os.path.abspath(filename).split(os.path.sep)[:-1])
            if not os.path.exists(directory):
                warning(f'No such directory "{directory}". '
                        f'Attempting to use internal file name {self.filename}')
                self.to_file(filename=self.filename)
            else:
                self.filename = filename
        if ".txt" not in self.filename:
            self.filename += ".txt"
        access_mode = 'w' # if not os.path.exists(filename) else access_mode
        # Define file
        file = open(self.filename, mode=access_mode, encoding='utf-8')

        file.write(self.to_string())
        file.close()

    @classmethod
    def from_file(cls,
                  filename: str = None,
                  full_content: bool = True):
        # Recognize the input file name or use the internally defined file name, if any.
        # Else, raise an error.
        if filename is None or not os.path.exists(filename):
            from taskplanner.gui.utilities import select_file
            filename = select_file(title=f'Select a non-empty configuration file to load a task planner')
        if ".txt" not in filename:
            filename += ".txt"
        # Define file
        file = open(filename, mode='r', encoding='utf-8')
        widget = PlannerWidget.from_string(file.read())
        widget.filename = filename
        file.close()
        return widget


class TaskListWidget(QWidget):
    """
    This widget contains:
        - A textedit that allows the user to add a new top-level task to the planner
        - A vertical list of :py:class:'taskplanner.gui.TaskWidgetSimple' of top-level tasks
    """

    def __init__(self,
                 planner: Planner,
                 parent: QWidget = None,
                 style: PlannerWidgetStyle = DEFAULT_PLANNER_STYLE
                 ):
        """
        :param planner: :py:class:'taskplanner.planner.Planner'
            The planner associated to this widget
        :param parent: :py:class:'QWidget', optional
            The parent widget
        """
        self.planner, self._style = planner, style
        self.task_widgets_updated = Signal()
        super().__init__(parent=parent)
        # Layout
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignTop)
        # Subtask widgets
        self.task_widgets = []
        self.layout.addStretch()
        self.make_task_widgets()

        slots = [slot for slot in self.planner.tasks_changed._slots if
                 'TaskListWidget.' in str(slot)]
        for slot in slots:
            self.planner.tasks_changed.disconnect(slot)
        self.planner.tasks_changed.connect(lambda **kwargs: self.make_task_widgets())

    def make_task_widgets(self):
        self.layout.removeItem(self.layout.itemAt(self.layout.count() - 1))
        for task in self.planner.tasks:
            if task not in [widget.task for widget in self.task_widgets]:
                widget = TaskWidgetSimple(parent=self,
                                          task=task,
                                          planner=self.planner,
                                          style=TaskWidgetStyle(color_palette=self._style.color_palette_name,
                                                                font=self._style.font_name)
                                          )
                self.layout.addWidget(widget)
                self.task_widgets += [widget]
        # Remove non-existent tasks
        for widget in self.task_widgets:
            if widget.task not in self.planner.tasks:
                widget.hide()
                self.task_widgets.remove(widget)
                self.layout.removeWidget(widget)
        self.layout.addStretch()
        self.task_widgets_updated.emit()


class CalendarWidget(QWidget):
    """
    This widget contains:
        - A top panel indicating months
        - A top panel indicating weeks, below months,
        - A top panel indicating days, below weeks
        - A set of timelines, each associated to a respective task
    """

    def __init__(self,
                 planner: Planner,
                 task_list_widget: TaskListWidget,
                 parent: QWidget = None,
                 view_type: str = 'weekly',
                 start_date: date = date.today(),
                 end_date: date = date.today() + relativedelta(months=6),
                 style: PlannerWidgetStyle = None):
        """

        :py:class:'taskplanner.planner.Planner'
            The planner associated to this widget
        :param task_list_widget: :py:class:'taskplanner.gui.planner.TaskListWidget'
            Widget containing the task list connected to this timelines widget
        :param parent: :py:class:'QWidget', optional
            The parent widget
        :param view_type: str, optional
            A string that defines the level of detail of the displayed timelines:
                - daily,
                - weekly,
                - monthly
        :param start_date: :py:class:'datetime.date', optional
            The displayed timelines begin at the start of the month of the inserted date.
        :param end_date: :py:class:'datetime.date', optional
            The displayed timelines end at the end of the month of the inserted date.
        :param style: :py:class:'taskplanner.gui.styles.PlannerWidgetStyle', optional
            The style of this widget.
        """
        self.planner = planner
        self.task_list_widget = task_list_widget
        self._start_date = start_date
        self._end_date = end_date
        self.dates_changed = Signal()
        self.n_months = 12 \
                        * (self.end_date.year - self.start_date.year) \
                        + (self.end_date.month - self.start_date.month) \
                        + 1
        self._style = style
        self.month_widgets = []
        self.timeline_widgets = []
        self._view_type = view_type
        self.view_type_changed = Signal()
        self.timelines_updated = Signal()
        super().__init__(parent=parent)
        # Layout
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignTop)
        self.setContentsMargins(0, 0, 0, 0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        # Horizontal layout for settings
        self.settings_layout = QHBoxLayout()
        self.layout.addLayout(self.settings_layout)
        # Start date widget
        # End date widget
        self.settings_layout.addStretch()
        # Horizontal layout for month widgets
        self.month_widgets_layout = QHBoxLayout()
        self.layout.addLayout(self.month_widgets_layout)
        self.month_widgets_layout.setContentsMargins(0, 0, 0, 0)
        self.month_widgets_layout.setSpacing(0)
        # Month widgets
        self.month_widgets_updated = Signal()
        self.make_month_widgets()
        # Timelines
        self.timelines_layout = QVBoxLayout()
        self.timelines_layout.setAlignment(Qt.AlignTop)
        self.layout.addLayout(self.timelines_layout)
        #self.timelines_layout.addStretch()
        self.make_timelines()

        slots = [slot for slot in self.planner.tasks_changed._slots if
                 'CalendarWidget.' in str(slot)]
        for slot in slots:
            self.planner.tasks_changed.disconnect(slot)
        self.planner.tasks_changed.connect(lambda **kwargs: self.make_timelines())

        if self._style is not None:
            set_style(widget=self,
                      stylesheets=self._style.stylesheets
                      ['planner_tab']
                      ['calendar_widget']['main'])
        self.layout.addStretch()

    @property
    def view_type(self):
        return self._view_type

    @view_type.setter
    def view_type(self, value):
        if value not in TIMELINE_VIEW_TYPES:
            raise ValueError(f'Invalid  timeline view type {value}.'
                             f' Valid view types are {TIMELINE_VIEW_TYPES}')
        self._view_type = value
        self.update_all()
        self.view_type_changed.emit()

    @property
    def start_date(self):
        return self._start_date

    @start_date.setter
    def start_date(self, value):
        self._start_date = value
        self.n_months = 12 \
                        * (self.end_date.year - self.start_date.year) \
                        + (self.end_date.month - self.start_date.month) \
                        + 1
        self.update_all()
        self.dates_changed.emit()

    @property
    def end_date(self):
        return self._end_date

    @end_date.setter
    def end_date(self, value):
        self._end_date = value
        self.n_months = 12 \
                        * (self.end_date.year - self.start_date.year) \
                        + (self.end_date.month - self.start_date.month) \
                        + 1
        self.update_all()
        self.dates_changed.emit()

    def update_all(self):
        self.make_month_widgets()
        self.make_timelines()

    def make_start_end_date_widgets(self):
        warning(f'Funtion "make_start_end_date_widgets" of widget {self} is not implemented yet.')

    def make_month_widgets(self):
        # Make month widget
        class MonthWidget(QFrame):
            """
            This widget contains:
                - A label containing the month
                - A set of labels containing the weeks of the month
            """

            def __init__(self,
                         planner: Planner,
                         task_list_widget: TaskListWidget,
                         calendar_widget: CalendarWidget,
                         date: date,
                         parent: QWidget = None,
                         style: PlannerWidgetStyle = None):
                self.planner = Planner
                self.task_list_widget = task_list_widget
                self.calendar_widget = calendar_widget
                self._style = style
                self.date = date
                self.week_widgets = []
                super().__init__(parent=parent)
                # Layout
                self.layout = QVBoxLayout(self)
                self.layout.setAlignment(Qt.AlignCenter)
                self.setFixedHeight(int(SCREEN_HEIGHT * 0.1))
                # Month label
                self.make_label()
                # Horizontal layout for week widgets
                self.week_widgets_layout = QHBoxLayout()
                self.week_widgets_layout.setAlignment(Qt.AlignLeft)
                self.layout.addLayout(self.week_widgets_layout)

                # Week widgets
                if calendar_widget.view_type in ['weekly',
                                                 'daily']:
                    if self._style is not None:
                        stylesheet = self._style.stylesheets['planner_tab']['calendar_widget']['month_widget']
                        stylesheet['main'] = stylesheet['main'].replace('border:0.5px', 'border:0px')
                        stylesheet['label'] = stylesheet['label'].replace(
                            'background-color:None',
                            f'background-color:{self._style.color_palette["background 2"]}')
                        self._style.stylesheets['planner_tab']['calendar_widget']['month_widget'] = stylesheet
                        set_style(widget=self,
                                  stylesheets=self._style.stylesheets
                                  ['planner_tab']
                                  ['calendar_widget']
                                  ['month_widget'])
                        self.layout.setAlignment(Qt.AlignLeft)
                    self.layout.setContentsMargins(0, 0, 0, 0)
                    self.week_widgets_layout.setSpacing(0)
                    self.make_week_widgets()
                    self.layout.insertStretch(1)
                else:
                    if self._style is not None:
                        stylesheet = self._style.stylesheets['planner_tab']['calendar_widget']['month_widget']
                        stylesheet['main'] = stylesheet['main'].replace('border:0px', 'border:0.5px')
                        stylesheet['label'] = stylesheet['label'].replace(f'background-color:{self._style.color_palette["background 2"]}',
                                                                          'background-color:None')
                        self._style.stylesheets['planner_tab']['calendar_widget']['month_widget'] = stylesheet
                        set_style(widget=self,
                                  stylesheets=self._style.stylesheets
                                  ['planner_tab']
                                  ['calendar_widget']
                                  ['month_widget'])
                        self.layout.setAlignment(Qt.AlignCenter)
                    self.setFixedWidth(int(SCREEN_WIDTH*0.13))
                # Set style
                if self._style is not None:
                    set_style(widget=self,
                              stylesheets=self._style.stylesheets
                              ['planner_tab']
                              ['calendar_widget']
                              ['month_widget'])

            def make_label(self):
                self.label = QLabel()
                # Layout
                self.layout.addWidget(self.label)
                self.label.setAlignment(Qt.AlignLeft)
                self.label.setAlignment(Qt.AlignVCenter)
                # Set text
                self.label.setText(self.date.strftime('%B %Y'))

            def make_week_widgets(self):
                class WeekWidget(QFrame):
                    """
                    This widget contains:
                        - A label containing the week
                        - A set of labels containing the days of the week
                    """

                    def __init__(self,
                                 planner: Planner,
                                 task_list_widget: TaskListWidget,
                                 calendar_widget: CalendarWidget,
                                 date: date,
                                 parent: QWidget = None,
                                 style: PlannerWidgetStyle = None):
                        self.planner = Planner
                        self.task_list_widget = task_list_widget
                        self.calendar_widget = CalendarWidget
                        self._style = style
                        self.date = date
                        self.dates = []
                        self.day_widgets = []
                        super().__init__(parent=parent)
                        # Layout
                        self.layout = QVBoxLayout(self)
                        self.layout.setAlignment(Qt.AlignTop)
                        # Week label
                        self.make_label()
                        # Horizontal layout for week widgets
                        self.day_widgets_layout = QHBoxLayout()
                        self.day_widgets_layout.setAlignment(Qt.AlignLeft)
                        self.layout.addLayout(self.day_widgets_layout)
                        # Day widgets
                        if calendar_widget.view_type == 'daily':
                            if self._style is not None:
                                stylesheet = self._style.stylesheets['planner_tab']['calendar_widget']['week_widget']
                                stylesheet['main'] = stylesheet['main'].replace('border:0.5px', 'border:0px')
                                self._style.stylesheets['planner_tab']['calendar_widget']['week_widget'] = stylesheet
                                set_style(widget=self,
                                          stylesheets=self._style.stylesheets
                                          ['planner_tab']
                                          ['calendar_widget']
                                          ['week_widget'])
                                self.layout.setAlignment(Qt.AlignLeft)
                            self.layout.setContentsMargins(0, 0, 0, 0)
                            self.day_widgets_layout.setSpacing(0)
                            self.make_day_widgets()
                        else:
                            self.setFixedWidth(int(SCREEN_WIDTH*0.05))
                            if self._style is not None:
                                stylesheet = self._style.stylesheets['planner_tab']['calendar_widget']['week_widget']
                                stylesheet['main'] = stylesheet['main'].replace('border:0px', 'border:0.5px')
                                self._style.stylesheets['planner_tab']['calendar_widget']['week_widget'] = stylesheet
                                set_style(widget=self,
                                          stylesheets=self._style.stylesheets
                                          ['planner_tab']
                                          ['calendar_widget']
                                          ['week_widget'])
                                self.layout.setAlignment(Qt.AlignCenter)

                        # Set style
                        if self._style is not None:
                            set_style(widget=self,
                                      stylesheets=self._style.stylesheets
                                      ['planner_tab']
                                      ['calendar_widget']
                                      ['week_widget'])

                    def make_label(self):
                        self.label = QLabel()
                        # Layout
                        self.layout.addWidget(self.label)
                        self.label.setAlignment(Qt.AlignVCenter)
                        # Set text
                        self.label.setText(self.date.strftime('Week %W'))

                    def make_day_widgets(self):
                        class DayWidget(QFrame):
                            """
                            This widget contains:
                                - A label containing the day
                            """

                            def __init__(self,
                                         planner: Planner,
                                         task_list_widget: TaskListWidget,
                                         date: date,
                                         parent: QWidget = None,
                                         style: PlannerWidgetStyle = None):
                                self.planner = Planner
                                self.task_list_widget = task_list_widget
                                self._style = style
                                self.date = date
                                super().__init__(parent=parent)
                                # Layout
                                self.layout = QVBoxLayout(self)
                                self.layout.setAlignment(Qt.AlignTop)
                                self.setFixedWidth(int(SCREEN_WIDTH*0.04))
                                # Day label
                                self.make_label()
                                # Set style
                                if self._style is not None:
                                    set_style(widget=self,
                                              stylesheets=self._style.stylesheets
                                              ['planner_tab']
                                              ['calendar_widget']
                                              ['day_widget'])

                            def make_label(self):
                                self.label = QLabel()
                                # Layout
                                self.layout.addWidget(self.label)
                                self.label.setAlignment(Qt.AlignCenter)
                                # Set text
                                self.label.setText(self.date.strftime('%A')[:3]
                                                   + ' ' + str(self.date.day))

                        self.dates = []
                        self.day_widgets = []
                        import calendar
                        is_day_of_week, is_day_of_month = True, True
                        self.n_days = 0

                        while is_day_of_week and is_day_of_month:
                            d = self.date + relativedelta(days=self.n_days)
                            if d == self.date:
                                d_previous = self.date
                            else:
                                d_previous = self.date + relativedelta(days=self.n_days - 1)
                            if d.weekday() % 7 < d_previous.weekday() % 7:
                                is_day_of_week = False
                            elif d.month != d_previous.month:
                                is_day_of_month = False
                            else:
                                self.dates += [d]
                                self.n_days += 1
                                self.day_widgets += [DayWidget(planner=self.planner,
                                                               task_list_widget=self.task_list_widget,
                                                               date=self.dates[-1],
                                                               parent=self,
                                                               style=self._style)]
                                self.day_widgets_layout.addWidget(self.day_widgets[-1])

                self.dates = []
                self.week_widgets = []
                is_day_of_month = True
                d = date(self.date.year,
                         self.date.month,
                         1)
                while is_day_of_month:
                    self.dates += [d]
                    self.week_widgets += [WeekWidget(planner=self.planner,
                                                     task_list_widget=self.task_list_widget,
                                                     calendar_widget=self.calendar_widget,
                                                     date=self.dates[-1],
                                                     parent=self,
                                                     style=self._style)]
                    self.week_widgets_layout.addWidget(self.week_widgets[-1])
                    is_day_of_week = True
                    while is_day_of_week:
                        d_previous = date(d.year, d.month, d.day)
                        d += relativedelta(days=1)
                        if d.weekday() % 7 < d_previous.weekday() % 7:
                            is_day_of_week = False
                        if d.month != self.date.month:
                            is_day_of_week = False
                            is_day_of_month = False

        # Delete old month widgets
        for widget in self.month_widgets:
            widget.hide()
            self.layout.removeWidget(widget)
        # Make new month widgets
        self.dates = []
        self.month_widgets = []
        reference_date = date(self.start_date.year,
                              self.start_date.month,
                              1)
        for count in range(self.n_months):
            self.dates += [reference_date + relativedelta(months=count)]
            self.month_widgets += [MonthWidget(planner=self.planner,
                                               task_list_widget=self.task_list_widget,
                                               calendar_widget=self,
                                               date=self.dates[-1],
                                               parent=self,
                                               style=self._style)]
            # If the month widgets don't fill in all the available space in 'monthly' view, the timeline geometry
            # calculations are wrong.
            if self.n_months <= 4 and self.view_type == 'monthly':
                self.month_widgets[-1].setFixedWidth(int(self.month_widgets[-1].width()*1.5))
            self.month_widgets_layout.addWidget(self.month_widgets[-1])
        self.month_widgets_updated.emit()

    def make_timelines(self):
        class Timeline(QFrame):
            """
            This widget contains a label which:
                - Has the same color as the associated task. Its color must follow the associated
                  task's color.
                - Has same vertical position as the associated task in the task list widget.
                  Its position must change whenever the vertical position of the associated
                  task changes. In particular, if the associated task is hidden or shown
                  in the task list widget of the planner, so must the timeline be hidden or shown.
                  Similarly, if the task is removed from the planner.
                - Has position and a horizontal extension such that it matches the start and end date
                  of the associated task, according to the CalendarWidget that contains it.
                  Its geometry must change whenever the start or end date of the task change, and
                  whenever the planner view type is changed (e.g., from daily to weekly)
            """

            def __init__(self,
                         task_widget: TaskWidgetSimple,
                         calendar_widget: CalendarWidget,
                         parent: QWidget = None,
                         style: PlannerWidgetStyle = None,
                         add_to_timelines_layout: bool = False):
                self.task_widget = task_widget
                self.planner = self.task_widget.planner
                self.task = self.task_widget.task
                self.calendar_widget = calendar_widget
                self._style = style
                self.start_position_changed = Signal()
                self.length_changed = Signal()
                super().__init__(parent=parent)
                # Layout
                self.layout = QVBoxLayout(self)
                self.setContentsMargins(0, 0, 0, 0)
                self.layout.setContentsMargins(0, 0, 0, 0)
                if add_to_timelines_layout and hasattr(self.parent(), 'timelines_layout'):
                    self.parent().timelines_layout.addWidget(self)
                # Horizontal layout for label
                self.label_layout = QHBoxLayout()
                self.label_layout.setAlignment(Qt.AlignLeft)
                self.layout.addLayout(self.label_layout)
                # Insert first spacing
                self.label_layout.insertSpacing(0, 0)
                # Label pushbutton
                self.make_label_pushbutton()
                # Sub-timelines
                self.sub_timelines = []
                self.make_sub_timelines()
                slots = [slot for slot in self.task.children_changed._slots if
                         'Timeline.' in str(slot)]
                for slot in slots:
                    self.task.children_changed.disconnect(slot)
                self.task.children_changed.connect(lambda **kwargs: self.make_sub_timelines())
                if self._style is not None:
                    set_style(widget=self,
                              stylesheets=self._style.stylesheets
                              ['planner_tab']
                              ['calendar_widget']
                              ['timeline']['main'])

            def make_label_pushbutton(self):
                self.label_pushbutton = QPushButton()
                # Layout
                self.label_layout.addWidget(self.label_pushbutton)
                self.set_height()

                def clicked():
                    task_widget = TaskWidget(task=self.task,
                                             planner=self.planner,
                                             style=TaskWidgetStyle(color_palette=self._style.color_palette_name,
                                                                   font=self._style.font_name))
                    task_widget.show()

                def update_label():
                    self.label_pushbutton.setText(f'({len(self.task.ancestors)}) {self.task.name}')

                # Connect task and widget
                self.label_pushbutton.installEventFilter(self)
                # Set initial text
                update_label()
                self.task.name_changed.connect(lambda **kwargs: update_label())
                # Set background color, border
                self.set_color()
                self.task.color_changed.connect(lambda **kwargs: self.set_color())
                # Set geometry
                self.set_geometry()
                self.task.start_date_changed.connect(lambda **kwargs: self.set_geometry())
                self.task.end_date_changed.connect(lambda **kwargs: self.set_geometry())
                self.calendar_widget.month_widgets_updated.connect(lambda **kwargs: self.set_geometry())
                # Set visibility
                self.set_visibility()
                self.task_widget.visibility_changed.connect(lambda **kwargs: self.set_visibility())


            def set_color(self):
                style_sheet = '''
                QPushButton
                {
                    background-color:%s;
                    border:0px solid %s;
                    font-size:%s;
                    text-align:left;
                    padding-left:10px;
                }
                QPushButton:hover
                {
                    text-decoration:underline;
                }
                ''' % (self.task.color,
                       self.task.color,
                       self._style.font['size - text - small'])
                self.label_pushbutton.setStyleSheet(style_sheet)

            def set_height(self):
                self.label_pushbutton.setFixedHeight(self.task_widget.task_line_widget.height())

            def set_start_position(self):
                delta_date = self.task.start_date - self.calendar_widget.month_widgets[0].date
                spacing = 0
                # Remove spacing
                self.label_layout.removeItem(self.label_layout.itemAt(0))
                if self.calendar_widget.view_type == 'daily':
                    day_width = self.calendar_widget.month_widgets[0].week_widgets[0].day_widgets[0].width()
                    n_day_widths = delta_date.days #+ 2
                    spacing = n_day_widths * day_width
                elif self.calendar_widget.view_type == 'weekly':
                    week_width = self.calendar_widget.month_widgets[0].week_widgets[0].width()
                    month_widgets = [m for m in self.calendar_widget.month_widgets if m.date <= self.task.start_date]
                    n_weeks = 0
                    for m in month_widgets:
                        week_widgets = [w for w in m.week_widgets if w.date <= self.task.start_date]
                        n_weeks += len(week_widgets)
                    n_weeks = n_weeks - 1 + (self.task.start_date.weekday()) / 7
                    spacing = int(week_width * n_weeks)
                elif self.calendar_widget.view_type == 'monthly':
                    month_width = self.calendar_widget.month_widgets[0].width()

                    month_widgets = [m for m in self.calendar_widget.month_widgets
                                     if m.date <= self.task.start_date]
                    n_months = len(month_widgets) - 1
                    month_date = self.calendar_widget.month_widgets[n_months].date
                    n_days_in_month = (month_date + relativedelta(months=1, days=-1)).day
                    n_months = n_months + (self.task.start_date.day - 1) / n_days_in_month
                    spacing = int(n_months * month_width)
                # Add left spacing
                self.label_layout.insertSpacing(0, spacing)
                self.start_position_changed.emit()

            def get_start_date(self,
                               start_position: int = None):
                start_position = start_position if start_position is not None else self.label_pushbutton.x()
                return self.get_date(position=start_position)


            def get_date(self,
                         position: int):
                if self.calendar_widget.view_type == 'daily':
                    day_width = self.calendar_widget.month_widgets[0].week_widgets[0].day_widgets[0].width()
                    n_days = int(ceil(position / day_width)) - 1
                    dt = self.calendar_widget.start_date + relativedelta(days=n_days)
                elif self.calendar_widget.view_type == 'weekly':
                    month_width = self.calendar_widget.month_widgets[0].width()
                    week_width = self.calendar_widget.month_widgets[0].week_widgets[0].width()
                    month_index = int(position / month_width)
                    month_widget = self.calendar_widget.month_widgets[month_index]
                    week_index = int((position - month_index * month_width) / week_width)
                    total_width = month_index * month_width + week_index * week_width
                    week_fraction = (position - total_width) / week_width
                    week = month_widget.week_widgets[week_index]
                    week_date = week.date
                    dt = week_date + relativedelta(days=int(7*week_fraction))
                elif self.calendar_widget.view_type == 'monthly':
                    month_width = self.calendar_widget.month_widgets[0].width()
                    month_index = int(position / month_width)
                    total_width = month_index * month_width
                    month_fraction = (position - total_width) / month_width
                    month_date = self.calendar_widget.month_widgets[month_index].date
                    n_days_in_month = int(((month_date + relativedelta(months=1, days=-1)).day - 1) * month_fraction)
                    dt = month_date + relativedelta(days=n_days_in_month)
                return dt


            def set_length(self):
                view_type = self.calendar_widget.view_type
                if view_type == 'daily':
                    day_width = self.calendar_widget.month_widgets[0].week_widgets[0].day_widgets[0].width()
                    n_days = (self.task.end_date - self.task.start_date).days + 1
                    self.label_pushbutton.setFixedWidth(max([0, day_width*n_days]))
                elif view_type == 'weekly':
                    week_width = self.calendar_widget.month_widgets[0].week_widgets[0].width()
                    month_widgets = [m for m in self.calendar_widget.month_widgets
                                     if m.date > self.task.start_date - relativedelta(months=1) and m.date <= self.task.end_date + relativedelta(months=1)]
                    n_weeks = 0
                    for m in month_widgets:
                        week_widgets = [w for w in m.week_widgets
                                        if w.date > self.task.start_date and w.date <= self.task.end_date]
                        n_weeks += len(week_widgets)
                    n_weeks = n_weeks + (self.task.end_date.weekday() - self.task.start_date.weekday() + 1) / 7
                    self.label_pushbutton.setFixedWidth(max([0, int(week_width * n_weeks)]))
                elif view_type == 'monthly':
                    month_width = self.calendar_widget.month_widgets[0].width()

                    month_widgets = [m for m in self.calendar_widget.month_widgets
                                     if m.date > self.task.start_date and m.date <= self.task.end_date]
                    n_months = len(month_widgets)
                    n_months = n_months + (self.task.end_date.day - self.task.start_date.day + 1) / 30
                    self.label_pushbutton.setFixedWidth(max([0, int(n_months * month_width)]))

                self.length_changed.emit()

            def get_end_date(self,
                             end_position: int = None):
                end_position = end_position if end_position is not None \
                    else (self.label_pushbutton.x() + self.label_pushbutton.width())
                return self.get_date(position=end_position)

            def set_geometry(self):
                self.set_start_position()
                self.set_length()

            def eventFilter(self, obj, event):
                """
                This function allows to handle all kinds of events for all subwidgets in this widget.
                :param obj:
                :param event:
                :return:
                """
                if obj == self.label_pushbutton:
                    if event.type() == QEvent.MouseButtonDblClick:
                        task_widget = TaskWidget(task=self.task,
                                                 planner=self.planner,
                                                 style=TaskWidgetStyle(color_palette=self._style.color_palette_name,
                                                                       font=self._style.font_name))

                        task_widget.show()
                    elif event.type() == QEvent.MouseButtonPress:
                        self.label_pushbutton.setMouseTracking(True)
                    elif event.type() == QEvent.MouseMove and self.label_pushbutton.hasMouseTracking():
                        if event.pos().x() <= self.label_pushbutton.width()/2:
                            start_date = self.get_start_date(self.label_pushbutton.x() + event.pos().x())
                            self.task.start_date = start_date
                        else:
                            end_date = self.get_end_date(self.label_pushbutton.x() + event.pos().x())
                            self.task.end_date = end_date
                    elif event.type() == QEvent.MouseButtonRelease:
                        self.label_pushbutton.setMouseTracking(False)
                return super().eventFilter(obj, event)

            def set_visibility(self):
                self.setVisible(self.task_widget.isVisible())

            def make_sub_timelines(self):
                l = self.calendar_widget.timelines_layout
                # Add new sub-timelines
                for subtask in self.task.children:
                    if subtask not in [widget.task for widget in self.sub_timelines]:
                        subtask_widget = [w for w in self.task_widget.subtask_widgets
                                          if w.task == subtask][0]
                        sub_timeline = Timeline(task_widget=subtask_widget,
                                                calendar_widget=self.calendar_widget,
                                                parent=self.parent(),
                                                style=self._style,
                                                add_to_timelines_layout=True)
                        # Add the sub-timeline to the main timelines layout
                        # Find the correct position in the layout
                        # where the sub-timeline is inserted
                        l.removeWidget(sub_timeline)
                        index = self.task.descendants.index(subtask)
                        index += l.indexOf(self) + 1
                        l.insertWidget(index, sub_timeline)
                        # sub_timeline.setFixedHeight(self.height())
                        self.sub_timelines += [sub_timeline]
                # Remove non-existent sub-timelines
                for widget in self.sub_timelines:
                    if widget.task not in self.task.children:
                        index = l.indexOf(widget)
                        w = widget
                        while w == widget or (w is not None and w.task in widget.task.descendants):
                            w.hide()
                            try:  # It may be that the widget had been removed from the list, but not hidden
                                self.calendar_widget.timeline_widgets.remove(w)
                            except:
                                pass
                            l.removeWidget(w)
                            if l.count() > 0:
                                try:
                                    index += 1
                                    w = l.itemAt(index).widget()
                                except:
                                    break
                            else:
                                break

        def add_timeline(task_w):
            if task not in [widget.task_widget.task for widget in self.timeline_widgets]:
                task_widget = [w for w in self.task_list_widget.task_widgets
                               if w.task == task][0]
                widget = Timeline(task_widget=task_widget,
                                  calendar_widget=self,
                                  parent=self,
                                  style=self._style,
                                  add_to_timelines_layout=True)
                #self.timelines_layout.addWidget(widget)
                self.timeline_widgets += [widget]
                if not widget.isVisible():
                    widget.show()

        for task in self.planner.tasks:
            add_timeline(task)

        # Remove non-existent timelines and all of those related to descendant tasks
        # This cannot be handled easily from within the nested structure of a Timeline object
        # and removing its sub-timelines, because the information about "ancestor" timelines
        # is absent in the current implementation. Only descendant timelines are available, hence,
        # a top-down deletion.
        for widget in self.timeline_widgets:
            if widget.task not in self.planner.tasks:
                index = self.timelines_layout.indexOf(widget)
                w = widget
                while w == widget or w.task in widget.task.descendants:
                    w.hide()
                    try:  # It may be that the widget had been removed from the list, but not hidden
                        self.timeline_widgets.remove(w)
                    except:
                        pass
                    self.timelines_layout.removeWidget(w)
                    if self.timelines_layout.count() > 0:
                        try:
                            index += 1
                            w = self.timelines_layout.itemAt(index).widget()
                        except:
                            break
                    else:
                        break
        self.timelines_updated.emit()
