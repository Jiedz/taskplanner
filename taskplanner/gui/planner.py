"""
This module defines a planner widget and related widgets.
"""
import screeninfo
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
    QSlider,
    QFontComboBox,
    )

from signalslot import Signal
import os
from logging import warning
from numpy import floor, ceil
from datetime import date
from dateutil.relativedelta import relativedelta
from taskplanner.tasks import Task
from taskplanner.planner import Planner
from taskplanner.gui.tasks import TaskWidget, TaskWidgetSimple, task_widget_widget_open
from taskplanner.gui.styles import TaskWidgetStyle, PlannerWidgetStyle, ICON_SIZES, COLOR_PALETTES, FONTS
from taskplanner.gui.utilities import set_style, get_primary_screen, select_file, select_directory

SCREEN = get_primary_screen()
SCREEN_WIDTH = SCREEN.width
SCREEN_HEIGHT = SCREEN.height

DEFAULT_PLANNER_STYLE = PlannerWidgetStyle(color_palette=COLOR_PALETTES['dark material'],
                                           font=FONTS['light'])
BUCKET_PROPERTY_NAMES = ['category',
                         'assignee',
                         'priority',
                         'progress']
BUCKET_PROPERTY_NAMES.sort()

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
        # Task buckets tab
        self.make_task_buckets_tab()
        # Settings tab
        self.make_settings_tab()
        # Set style
        self.set_style()
        self.planner.tasks_changed.connect(lambda **kwargs: self.to_file())

    def set_style(self, style: PlannerWidgetStyle = None):
        self._style = style if style is not None else self._style
        if self._style is not None:
            set_style(widget=self,
                      stylesheets=self._style.stylesheets['main'])
            self.planner_tab.set_style(self._style)
            self.task_buckets_tab.set_style(self._style)
            #self.settings_tab.set_style(self._style)

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
                self.upload_task_pushbutton.setFixedSize(int(self.upload_task_pushbutton.iconSize().width()*2),
                                                         int(self.upload_task_pushbutton.iconSize().height()*2))
                self.new_task_settings_layout.addSpacing(int(SCREEN_WIDTH * 0.35)
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
                self.task_list_scrollarea.setFixedWidth(int(SCREEN_WIDTH * 0.35))
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
                                                 style=TaskWidgetStyle(color_palette=self._style.color_palette,
                                                                       font=self._style.font,
                                                                       style_name=self._style.style_name))
                self.view_selector.combobox.setGeometry(task_widget_example.priority_widget.combobox.geometry())
                self.view_selector.setFixedSize(int(SCREEN_WIDTH * 0.08),
                                                int(self.height() * 0.08))
                # Calendar start and end dates
                self.make_start_end_dates()
                self.start_date_widget.setFixedSize(int(SCREEN_WIDTH * 0.05),
                                                    int(self.height() * 0.05))
                self.end_date_widget.setFixedSize(int(SCREEN_WIDTH * 0.05),
                                                  int(self.height() * 0.05))

                self.set_style()
                # Lock the vertical scrollbars of the timelines and the task list
                self.calendar_scrollarea.setVerticalScrollBar(self.task_list_scrollarea.verticalScrollBar())

            def set_style(self, style: PlannerWidgetStyle = None):
                self._style = style if style is not None else self._style
                if self._style is not None:
                    set_style(widget=self,
                              stylesheets=self._style.stylesheets
                              ['planner_tab']['main'])
                    set_style(widget=self,
                              stylesheets=self._style.stylesheets
                              ['planner_tab']['task_list_scrollarea'])
                    set_style(widget=self,
                              stylesheets=self._style.stylesheets
                              ['planner_tab']['task_list_widget'])
                    set_style(widget=self,
                              stylesheets=self._style.stylesheets
                              ['planner_tab']['calendar_scrollarea'])
                    set_style(widget=self,
                              stylesheets=self._style.stylesheets
                              ['planner_tab']['new_task_textedit'])
                    set_style(widget=self.upload_task_pushbutton,
                              stylesheets=self._style.stylesheets
                              ['planner_tab']
                              ['upload_task_pushbutton'])
                    self.task_list_widget.set_style(self._style)
                    self.calendar_widget.set_style(self._style)
                    self.view_selector.set_style(self._style)
                    self.start_date_widget.set_style(self._style)
                    self.end_date_widget.set_style(self._style)



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
                        self.set_style()
                        self.layout.addStretch()

                    def set_style(self, style: PlannerWidgetStyle = None):
                        self._style = style if style is not None else self._style
                        if self._style is not None:
                            set_style(widget=self,
                                      stylesheets=self._style.stylesheets
                                      ['planner_tab']
                                      ['view_selector'])

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
                                                       parent=self,
                                                       style=self._style)

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
                        self.set_style()

                    def set_style(self, style: PlannerWidgetStyle = None):
                        self._style = style if style is not None else self._style
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

    def make_task_buckets_tab(self):
        class TaskBucketsTab(QWidget):
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
                self.property_name = 'assignee'
                super().__init__(parent=parent)
                # Layout
                self.layout = QVBoxLayout(self)
                self.layout.setAlignment(Qt.AlignTop)
                # Geometry
                self.setGeometry(self.parent().geometry())
                # Horizontal layout for settings
                self.settings_layout = QHBoxLayout()
                self.layout.addLayout(self.settings_layout)
                self.settings_layout.setAlignment(Qt.AlignLeft)
                # Horizontal layout for settings
                self.settings_layout = QHBoxLayout()
                self.layout.addLayout(self.settings_layout)
                self.settings_layout.setAlignment(Qt.AlignLeft)
                # Horizontal layout for task buckets
                self.buckets_layout = QHBoxLayout()
                self.layout.addLayout(self.buckets_layout)
                # Bucket list widget
                self.make_bucket_list_widget()
                self.bucket_list_widget.setFixedHeight(int(self.height() * 0.4))
                # Scrollarea for bucket list widget
                self.bucket_list_scrollarea = QScrollArea()
                self.bucket_list_scrollarea.setWidgetResizable(True)
                self.bucket_list_scrollarea.setWidget(self.bucket_list_widget)
                self.layout.addWidget(self.bucket_list_scrollarea)
                self.bucket_list_scrollarea.setFixedHeight(int(self.height() * 0.4))
                self.bucket_list_scrollarea.verticalScrollBar().setDisabled(True)
                self.bucket_list_scrollarea.verticalScrollBar().hide()
                # Property widget
                self.make_property_widget()
                self.property_widget.setFixedSize(int(SCREEN_WIDTH * 0.08),
                                                  int(self.height() * 0.08))
                # Stats widget
                self.make_stats_widget()
                # Style
                self.set_style()


            def set_style(self, style: PlannerWidgetStyle = None):
                self._style = style if style is not None else self._style
                if self._style is not None:
                    #set_style(widget=self,
                    #          stylesheets=self._style.stylesheets
                    #          ['task_buckets_tab']['main'])
                    set_style(widget=self,
                              stylesheets=self._style.stylesheets
                              ['task_buckets_tab']['bucket_list_scrollarea'])
                    self.property_widget.set_style(self._style)
                    self.bucket_list_widget.set_style(self._style)

            def make_property_widget(self):
                class PropertyWidget(QWidget):
                    """
                    This widget contains:
                    - A label, indicating the purpose of selecting the task property
                    - A combobox containing the properties that can be selected for bucket creation
                    """

                    def __init__(self,
                                 planner: Planner,
                                 bucket_list_widget: BucketListWidget,
                                 parent: QWidget = None,
                                 style: PlannerWidgetStyle = DEFAULT_PLANNER_STYLE):
                        """

                        :param planner:
                        :param parent:
                        :param style:
                        """
                        super().__init__(parent=parent)
                        self.planner = planner
                        self.bucket_list_widget = bucket_list_widget
                        self._style = style
                        # Layout
                        self.layout = QVBoxLayout()
                        self.setLayout(self.layout)
                        # Label
                        self.make_label()
                        # Combobox
                        self.make_combobox()
                        # Style
                        self.set_style()

                    def set_style(self, style: PlannerWidgetStyle = None):
                        self._style = style if style is not None else self._style
                        if self._style is not None:
                            set_style(widget=self,
                                      stylesheets=self._style.stylesheets
                                      ['task_buckets_tab']['property_widget'])


                    def make_label(self):
                        self.label = QLabel('Sort By')
                        self.layout.addWidget(self.label)
                        self.label.setAlignment(Qt.AlignLeft)
                        self.label.setAlignment(Qt.AlignBottom)
                        self.label.setContentsMargins(0, 0, 0, 0)

                    def make_combobox(self):
                        self.combobox = QComboBox()
                        # Layout
                        self.layout.addWidget(self.combobox)
                        # Add items
                        self.combobox.addItems([n.title() for n in BUCKET_PROPERTY_NAMES])
                        # User interactions
                        def clicked():
                            self.bucket_list_widget.property_name = self.combobox.currentText().lower()

                        # Connect task and widget
                        self.combobox.currentIndexChanged.connect(clicked)
                        self.bucket_list_widget.property_name_changed.connect(
                            lambda **kwargs: self.combobox.setCurrentText(self.bucket_list_widget.property_name.title()))
                        # Set initial value
                        self.combobox.setCurrentText(self.bucket_list_widget.property_name)

                self.property_widget = PropertyWidget(planner=self.planner,
                                                      bucket_list_widget=self.bucket_list_widget,
                                                      parent=self,
                                                      style=self._style)
                self.settings_layout.addWidget(self.property_widget)

            def make_bucket_list_widget(self):
                self.bucket_list_widget = BucketListWidget(planner=self.planner,
                                                          property_name=self.property_name,
                                                          parent=self,
                                                          style=self._style)

            def make_stats_widget(self):
                class StatsWidget(QFrame):
                    """
                    This widget contains:

                        - A title label
                        - graph widgets containing various stats about the task buckets
                    """
                    def __init__(self,
                                 planner: Planner,
                                 bucket_list_widget: BucketListWidget,
                                 parent: QWidget = None,
                                 style: PlannerWidgetStyle = DEFAULT_PLANNER_STYLE):
                        """

                        :param planner:
                        :param bucket_list_widget:
                        :param parent:
                        :param style:
                        """
                        self.planner = planner
                        self.bucket_list_widget = bucket_list_widget
                        self._style = style
                        super().__init__(parent=parent)
                        # Layout
                        self.layout = QVBoxLayout(self)
                        self.layout.setAlignment(Qt.AlignTop)
                        # Horizontal layout for title label
                        self.title_layout = QHBoxLayout()
                        self.layout.addLayout(self.title_layout)
                        self.title_layout.setAlignment(Qt.AlignLeft)
                        # Title label
                        self.make_title_label()
                        # Horizontal layout for graph widgets
                        self.graphs_layout = QHBoxLayout()
                        self.layout.addLayout(self.graphs_layout)
                        self.graphs_layout.setAlignment(Qt.AlignCenter)
                        # Graph widgets
                        self.make_graph_widgets()
                        # Style
                        self.set_style()

                    def set_style(self, style: PlannerWidgetStyle = None):
                        self._style = style if style is not None else self._style
                        if self._style is not None:
                            set_style(widget=self,
                                      stylesheets=self._style.stylesheets
                                      ['task_buckets_tab']
                                      ['stats_widget']['main'])
                            set_style(widget=self.title_label,
                                      stylesheets=self._style.stylesheets
                                      ['task_buckets_tab']
                                      ['stats_widget']['title_label'])
                            set_style(widget=self.graph_number_of_tasks,
                                      stylesheets=self._style.stylesheets
                                      ['task_buckets_tab']
                                      ['stats_widget']['graph_widget'])
                            set_style(widget=self.graph_time_for_tasks,
                                      stylesheets=self._style.stylesheets
                                      ['task_buckets_tab']
                                      ['stats_widget']['graph_widget'])

                    def make_title_label(self):
                        self.title_label = QLabel()
                        self.title_layout.addWidget(self.title_label)
                        # Set text
                        self.title_label.setText('Stats')

                    def make_graph_widgets(self):
                        from taskplanner.gui.utilities import PyplotWidget
                        width_inches, height_inches = screeninfo.get_monitors()[0].width_mm / 2.54 * 0.075, \
                                                      screeninfo.get_monitors()[0].width_mm / 2.54 * 0.075
                        # Fraction of tasks associated to a certain property value
                        self.graph_number_of_tasks = PyplotWidget()
                        self.graphs_layout.addWidget(self.graph_number_of_tasks)
                        self.graph_number_of_tasks.figure.set_size_inches(width_inches, height_inches, forward=True)
                        self.graph_number_of_tasks.canvas.setFixedSize(int(self.parent().width() * 0.4),
                                                                       int(self.parent().width() * 0.2))
                        self.graph_number_of_tasks.figure.axes[0].grid(False)
                        self.graph_number_of_tasks.figure.axes[0].axis('equal')
                        self.graph_number_of_tasks.figure.patch.set_facecolor(self._style.color_palette['background 1'])
                        # Fraction of time planned for tasks associated to a certain property value
                        self.graph_time_for_tasks = PyplotWidget()
                        self.graphs_layout.addWidget(self.graph_time_for_tasks)
                        # self.graph_number_of_tasks.figure.set_dpi(int(self.parent().width() * 0.05))
                        self.graph_time_for_tasks.figure.set_size_inches(width_inches, height_inches, forward=True)
                        self.graph_time_for_tasks.canvas.setFixedSize(int(self.parent().width() * 0.4),
                                                                      int(self.parent().width() * 0.2))
                        self.graph_time_for_tasks.figure.patch.set_facecolor(self._style.color_palette['background 1'])
                        self.graph_time_for_tasks.figure.axes[0].grid(False)
                        self.graph_time_for_tasks.figure.axes[0].axis('equal')

                        self.update_graphs()

                    def update_graph_number_of_tasks(self, **kwargs):
                        # Fraction of tasks associated to a certain property value
                        self.graph_number_of_tasks.set_title(f'Number of Tasks of Each '
                                                             f'{self.bucket_list_widget.property_name.title()}')
                        self.graph_number_of_tasks.figure.axes[0].cla()
                        if self.planner.all_tasks:
                            patches, outer_labels, inner_labels = self.graph_number_of_tasks.figure.axes[0].pie(
                                x=[len(bucket.task_list_widget.tasks)
                                   for bucket
                                   in self.bucket_list_widget.bucket_widgets],
                                # explode=True,
                                labels=[bucket.label.text()
                                        for bucket
                                        in self.bucket_list_widget.bucket_widgets],
                                autopct='%1.1f%%',
                                shadow=True,
                            )
                            for label in outer_labels:
                                label.set_fontfamily(self._style.font['family'])
                                label.set_fontsize('large')
                                label.set_color(self._style.color_palette['text'])

                            for label in inner_labels:
                                label.set_fontfamily(self._style.font['family'])
                                label.set_fontsize('large')
                                label.set_color(self._style.color_palette['text'])
                        # Connect bucket list changes to graph updates
                        self.bucket_list_widget.property_name_changed.disconnect(self.update_graph_number_of_tasks)
                        self.bucket_list_widget.property_name_changed.connect(self.update_graph_number_of_tasks)

                        self.bucket_list_widget.buckets_updated.disconnect(self.update_graph_number_of_tasks)
                        self.bucket_list_widget.buckets_updated.connect(self.update_graph_number_of_tasks)

                        for widget in self.bucket_list_widget.bucket_widgets:
                            widget.task_list_widget.tasks_updated.disconnect(self.update_graph_number_of_tasks)
                            widget.task_list_widget.tasks_updated.connect(self.update_graph_number_of_tasks)


                    def update_graph_time_for_tasks(self, **kwargs):
                        # Fraction of time planned for tasks associated to a certain property value
                        self.graph_time_for_tasks.set_title(
                            f'Time Planned for Each '
                            f'{self.bucket_list_widget.property_name.title()}')
                        self.graph_time_for_tasks.figure.axes[0].cla()
                        if self.planner.all_tasks:
                            all_tasks = self.planner.all_tasks
                            n_days = []
                            for widget in self.bucket_list_widget.bucket_widgets:
                                n_days += [sum([abs(relativedelta(t.end_date, t.start_date).days + 1)
                                                for t in widget.task_list_widget.tasks])]

                            patches, outer_labels, inner_labels = self.graph_time_for_tasks.figure.axes[0].pie(
                                x=n_days,
                                # explode=True,
                                labels=[bucket.label.text()
                                        for bucket
                                        in self.bucket_list_widget.bucket_widgets],
                                autopct='%1.1f%%',
                                shadow=True,
                            )
                            for label in outer_labels:
                                label.set_fontfamily(self._style.font['family'])
                                label.set_fontsize('large')
                                label.set_color(self._style.color_palette['text'])

                            for label in inner_labels:
                                label.set_fontfamily(self._style.font['family'])
                                label.set_fontsize('large')
                                label.set_color(self._style.color_palette['text'])

                        # Connect bucket list changes to graph updates
                        self.bucket_list_widget.property_name_changed.disconnect(self.update_graph_time_for_tasks)
                        self.bucket_list_widget.property_name_changed.connect(self.update_graph_time_for_tasks)

                        self.bucket_list_widget.buckets_updated.disconnect(self.update_graph_time_for_tasks)
                        self.bucket_list_widget.buckets_updated.connect(self.update_graph_time_for_tasks)

                        for widget in self.bucket_list_widget.bucket_widgets:
                            widget.task_list_widget.tasks_updated.disconnect(self.update_graph_time_for_tasks)
                            widget.task_list_widget.tasks_updated.connect(self.update_graph_time_for_tasks)
                        # Connect task start and end dates to graph updates
                        for task in self.planner.all_tasks:
                            task.start_date_changed.disconnect(self.update_graph_time_for_tasks)
                            task.start_date_changed.connect(self.update_graph_time_for_tasks)

                            task.end_date_changed.disconnect(self.update_graph_time_for_tasks)
                            task.end_date_changed.connect(self.update_graph_time_for_tasks)

                    def update_graphs(self, **kwargs):
                        self.update_graph_number_of_tasks()
                        self.update_graph_time_for_tasks()

                self.stats_widget = StatsWidget(planner=self.planner,
                                                bucket_list_widget=self.bucket_list_widget,
                                                parent=self,
                                                style=self._style)
                self.layout.addWidget(self.stats_widget)

        self.task_buckets_tab = TaskBucketsTab(planner=self.planner,
                                               parent=self,
                                               style=self._style)
        self.addTab(self.task_buckets_tab, 'Task Buckets')

    def make_settings_tab(self):
        class SettingsTab(QFrame):
            """
            This tab contains the widget's settings, including:

                - Style settings (colors, fonts)
            """
            def __init__(self,
                         planner: Planner,
                         planner_widget: PlannerWidget,
                         parent: QWidget = None,
                         style: PlannerWidgetStyle = DEFAULT_PLANNER_STYLE):
                """

                :param planner:
                :param planner_widget:
                :param parent:
                :param style:
                """
                self.planner = planner
                self.planner_widget = planner_widget
                self._style = style
                super().__init__(parent=parent)
                # Layout
                self.layout = QHBoxLayout(self)
                self.layout.setAlignment(Qt.AlignLeft)
                # Graphics settings
                self.make_graphics_settings()
                # Scroll area for the graphics settings
                self.graphics_scrollarea = QScrollArea()
                self.graphics_scrollarea.setWidgetResizable(True)
                self.graphics_scrollarea.setWidget(self.graphics_settings_widget)
                self.layout.addWidget(self.graphics_scrollarea)
                self.graphics_settings_widget.setFixedWidth(self.graphics_settings_widget.example_task_widget.width())
                # Style
                self.set_style()

            def set_style(self, style: PlannerWidgetStyle = None):
                self._style = style if style is not None else self._style
                if self._style is not None:
                    set_style(widget=self,
                              stylesheets=self._style.stylesheets
                              ['settings_tab']
                              ['main'])
                    set_style(widget=self.graphics_scrollarea,
                              stylesheets=self._style.stylesheets
                              ['settings_tab']
                              ['graphics_scrollarea'])
                    self.graphics_settings_widget.set_style(self._style)


            def make_graphics_settings(self):
                class GraphicsSettingsWidget(QFrame):
                    """
                    This widget contains:

                        - A set of color selection widgets that allow the user to select a color palette
                        - A set of font size selector widgets to allow the user to select different font sizes
                        - A font selection widget to allow the user to select a font family
                        - An example TaskWidget that exemplifies, in real time, how the user's changes reflect onto the
                        - widget
                    """

                    def __init__(self,
                                 planner: Planner,
                                 planner_widget: PlannerWidget,
                                 parent: QWidget = None,
                                 style: PlannerWidgetStyle = DEFAULT_PLANNER_STYLE):
                        """

                        :param planner:
                        :param planner_widget:
                        :param parent:
                        :param style:
                        """
                        self.planner = planner
                        self.planner_widget = planner_widget
                        self._style = style
                        self.chosen_style = self._style
                        super().__init__(parent=parent)
                        # Layout
                        self.layout = QVBoxLayout(self)
                        self.layout.setAlignment(Qt.AlignTop)
                        self.layout.setAlignment(Qt.AlignLeft)
                        # Title
                        self.make_title_label()
                        # Color selection widget
                        self.make_color_palette_selection_widget()
                        # Font selection widget
                        self.make_font_selection_widget()
                        # Apply pushbutton
                        self.make_apply_pushbutton()
                        self.apply_pushbutton.setFixedWidth(int(SCREEN_WIDTH*0.05))
                        # Example task widget
                        self.example_task = Task(name='Example Task',
                                                category='Example Category',
                                                description='## Example Description\n- First point',
                                                priority='urgent')
                        self.make_example_task_widget()

                        self.apply_pushbutton.click()
                        # Style
                        self.set_style()

                    def set_style(self, style: PlannerWidgetStyle = None):
                        self._style = style if style is not None else self._style
                        if self._style is not None:
                            set_style(widget=self,
                                      stylesheets=self._style.stylesheets
                                      ['settings_tab']['graphics_settings_widget']
                                      ['main'])
                            set_style(widget=self.title_label,
                                      stylesheets=self._style.stylesheets
                                      ['settings_tab']['graphics_settings_widget']
                                      ['title_label'])
                            set_style(widget=self.apply_pushbutton,
                                      stylesheets=self._style.stylesheets
                                      ['settings_tab']['graphics_settings_widget']
                                      ['apply_pushbutton'])
                            self.color_palette_selection_widget.set_style(self._style)
                            self.font_selection_widget.set_style(self._style)


                    def make_title_label(self):
                        self.title_label = QLabel()
                        self.layout.addWidget(self.title_label)
                        self.title_label.setText('Graphics')

                    def make_color_palette_selection_widget(self):
                        class ColorSelector(QFrame):
                            """
                            This widget contains:
                                - A label that indicates the color's purpose
                                - A push button containing the color
                                - A color picker widget, popping up at the click of the color push button,
                                 that allows the user to select a new color.
                            """
                            def __init__(self,
                                         planner: Planner,
                                         graphics_settings_widget: GraphicsSettingsWidget,
                                         color_property: str,
                                         parent: QWidget = None,
                                         style: PlannerWidgetStyle = DEFAULT_PLANNER_STYLE):
                                """

                                """
                                self.planner = planner
                                self.graphics_settings_widget = graphics_settings_widget
                                self._style = style
                                if color_property not in list(DEFAULT_PLANNER_STYLE.color_palette.keys()):
                                    raise ValueError(f'Invalid color property "{color_property}". '
                                          f'Valid color properties are {list(DEFAULT_PLANNER_STYLE.color_palette.keys())}')
                                self.color_property = color_property
                                super().__init__(parent=parent)
                                # Layout
                                self.layout = QHBoxLayout(self)
                                self.layout.setAlignment(Qt.AlignLeft)
                                # Label
                                self.make_label()
                                # Color button
                                self.chosen_color = self.graphics_settings_widget.chosen_style.color_palette[color_property]
                                self.make_color_button()
                                # Color picking dialog
                                self.make_color_dialog()
                                # Style
                                self.set_style()

                            def set_style(self, style: PlannerWidgetStyle = None):
                                self._style = style if style is not None else self._style
                                if self._style is not None:
                                    set_style(widget=self,
                                              stylesheets=self._style.stylesheets
                                              ['settings_tab']['graphics_settings_widget']
                                              ['color_palette_selection_widget']['color_selector']
                                              ['main'])
                                    set_style(widget=self.label,
                                              stylesheets=self._style.stylesheets
                                              ['settings_tab']['graphics_settings_widget']
                                              ['color_palette_selection_widget']['color_selector']
                                              ['label'])
                                    pushbutton_stylesheet = \
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
                                            ''' % (self.chosen_color,
                                                   self._style.color_palette['background 1'],
                                                   self._style.color_palette['text - highlight'])
                                    set_style(widget=self.color_pushbutton,
                                              stylesheets=pushbutton_stylesheet)

                            def make_label(self):
                                self.label = QLabel(self.color_property.title())
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

                                # Connect task and widget
                                self.color_pushbutton.clicked.connect(clicked)

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
                                def update_color():
                                    self.chosen_color = self.color_dialog.selectedColor().name()
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
                                                ''' % (self.chosen_color,
                                                       self._style.color_palette['background 1'],
                                                       self._style.color_palette['text - highlight'])

                                    self.color_pushbutton.setStyleSheet(stylesheet)

                                    self.graphics_settings_widget.chosen_style.\
                                        color_palette[self.color_property] = self.color_dialog.selectedColor().name()
                                    self.graphics_settings_widget.update_example_task()

                                self.color_dialog.accepted.connect(update_color)
                                # Set the initial color
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
                                            ''' % (self.chosen_color,
                                                   self._style.color_palette['background 1'],
                                                   self._style.color_palette['text - highlight'])
                                self.color_pushbutton.setStyleSheet(stylesheet)

                        class ColorPaletteSelectionWidget(QFrame):
                            """
                            This widget contains:

                                - A title stating the purpose
                                - A color selection widget for each section of a widget's color palette, as defined in
                                  taskplanner.gui.styles module
                            """
                            def __init__(self,
                                         planner: Planner,
                                         graphics_settings_widget: GraphicsSettingsWidget,
                                         parent: QWidget = None,
                                         style: PlannerWidgetStyle = DEFAULT_PLANNER_STYLE):
                                self.planner = planner
                                self.graphics_settings_widget = graphics_settings_widget
                                self._style = style
                                super().__init__(parent=parent)
                                # Layout
                                self.layout = QVBoxLayout(self)
                                self.layout.setAlignment(Qt.AlignTop)
                                self.layout.setAlignment(Qt.AlignLeft)
                                # Label
                                self.make_title_label()
                                # Layout for color selection widgets
                                self.color_selectors_layout = QGridLayout()
                                self.layout.addLayout(self.color_selectors_layout)
                                # Make color selection widgets
                                self.make_color_selectors()
                                # Style
                                self.set_style()
                                
                            def set_style(self, style: PlannerWidgetStyle = None):
                                self._style = style if style is not None else self._style
                                if self._style is not None:
                                    set_style(widget=self,
                                              stylesheets=self._style.stylesheets
                                              ['settings_tab']['graphics_settings_widget']
                                              ['color_palette_selection_widget']
                                              ['main'])
                                    set_style(widget=self.title_label,
                                              stylesheets=self._style.stylesheets
                                              ['settings_tab']['graphics_settings_widget']
                                              ['color_palette_selection_widget']
                                              ['title_label'])
                                    for selector in self.color_selectors.values():
                                        selector.set_style(self._style)

                            def make_title_label(self):
                                self.title_label = QLabel()
                                self.layout.addWidget(self.title_label)
                                # Set text
                                self.title_label.setText('Color Palette')

                            def make_color_selectors(self):
                                self.color_selectors = {}
                                color_properties = list(self.graphics_settings_widget.chosen_style.color_palette.keys())
                                color_properties = [c for c in color_properties if 'text' not in c.lower()] \
                                                 + [c for c in color_properties if 'text' in c.lower()]
                                n_cols = 3
                                n_rows = 2
                                for i in range(len(color_properties)):
                                    col = i % n_cols
                                    row = int(i/n_cols)
                                    color_property = color_properties[i]
                                    widget = ColorSelector(planner=self.planner,
                                                           graphics_settings_widget=self.graphics_settings_widget,
                                                           color_property=color_property,
                                                           parent=self,
                                                           style=self._style)
                                    self.color_selectors_layout.addWidget(widget, row, col)
                                    self.color_selectors[color_property] = widget

                        self.color_palette_selection_widget = ColorPaletteSelectionWidget(planner=self.planner,
                                                                                          graphics_settings_widget=self,
                                                                                          parent=self,
                                                                                          style=self._style)
                        self.layout.addWidget(self.color_palette_selection_widget)


                    def make_font_selection_widget(self):
                        class FontSizeSelector(QFrame):
                            """
                            This widget contains:
                                - A label that indicates the font's purpose
                                - A slider that allows the user to select the font size
                            """

                            def __init__(self,
                                         planner: Planner,
                                         graphics_settings_widget: GraphicsSettingsWidget,
                                         font_property: str,
                                         parent: QWidget = None,
                                         style: PlannerWidgetStyle = DEFAULT_PLANNER_STYLE):
                                """

                                :param planner:
                                :param graphics_settings_widget:
                                :param font_property:
                                :param parent:
                                :param style:
                                """
                                self.planner = planner
                                self.graphics_settings_widget = graphics_settings_widget
                                self._style = style
                                if font_property not in list(DEFAULT_PLANNER_STYLE.font.keys()):
                                    raise ValueError(f'Invalid font property "{font_property}". '
                                                     f'Valid color properties are '
                                                     f'{list(set(DEFAULT_PLANNER_STYLE.font.keys())) - set(["family"])}')
                                self.font_property = font_property
                                super().__init__(parent=parent)
                                # Layout
                                self.layout = QHBoxLayout(self)
                                self.layout.setAlignment(Qt.AlignLeft)
                                # Label
                                self.make_label()
                                # Color button
                                self.chosen_fontsize = int(self.graphics_settings_widget.chosen_style.font[self.font_property].replace('pt', ''))
                                self.make_slider()
                                # Style
                                self.set_style()

                            def set_style(self, style: PlannerWidgetStyle = None):
                                self._style = style if style is not None else self._style
                                if self._style is not None:
                                    set_style(widget=self,
                                              stylesheets=self._style.stylesheets
                                              ['settings_tab']['graphics_settings_widget']
                                              ['font_selection_widget']['fontsize_selector']
                                              ['main'])
                                    set_style(widget=self.label,
                                              stylesheets=self._style.stylesheets
                                              ['settings_tab']['graphics_settings_widget']
                                              ['font_selection_widget']['fontsize_selector']
                                              ['label'])
                                    set_style(widget=self.slider,
                                              stylesheets=self._style.stylesheets
                                              ['settings_tab']['graphics_settings_widget']
                                              ['font_selection_widget']['fontsize_selector']
                                              ['slider'])

                            def make_label(self):
                                self.label = QLabel(self.font_property.title())
                                self.layout.addWidget(self.label)
                                self.label.setAlignment(Qt.AlignLeft)

                            def make_slider(self):
                                self.slider = QSlider()
                                self.slider.setOrientation(Qt.Horizontal)
                                self.slider.setRange(6, 30)
                                self.slider.setValue(self.chosen_fontsize)
                                # Layout
                                self.layout.addWidget(self.slider)

                                # User interactions
                                def changed():
                                    self.chosen_fontsize = self.slider.value()
                                    self.graphics_settings_widget.chosen_style.font[self.font_property] = \
                                    f'{self.chosen_fontsize}pt'
                                    self.graphics_settings_widget.update_example_task()

                                # Connect task and widget
                                self.slider.valueChanged.connect(changed)

                        class FontFamilySelector(QFrame):
                            """
                            This widget contains:
                                - A label that indicates the purpose of choosing the font family
                                - A push button containing the name of the font family
                                - A font picker widget, popping up at the click of the color push button,
                                 that allows the user to select a new font family.
                            """

                            def __init__(self,
                                         planner: Planner,
                                         graphics_settings_widget: GraphicsSettingsWidget,
                                         parent: QWidget = None,
                                         style: PlannerWidgetStyle = DEFAULT_PLANNER_STYLE):
                                """

                                :param planner:
                                :param graphics_settings_widget:
                                :param parent:
                                :param style:
                                """
                                self.planner = planner
                                self.graphics_settings_widget = graphics_settings_widget
                                self._style = style
                                super().__init__(parent=parent)
                                # Layout
                                self.layout = QHBoxLayout(self)
                                self.layout.setAlignment(Qt.AlignLeft)
                                # Label
                                self.make_label()
                                self.chosen_font_family = self.graphics_settings_widget.chosen_style.font['family']
                                # Color font combobox
                                self.make_combobox()
                                # Style
                                self.set_style()

                            def set_style(self, style: PlannerWidgetStyle = None):
                                self._style = style if style is not None else self._style
                                if self._style is not None:
                                    set_style(widget=self,
                                              stylesheets=self._style.stylesheets
                                              ['settings_tab']['graphics_settings_widget']
                                              ['font_selection_widget']['font_family_selector']
                                              ['main'])
                                    set_style(widget=self.label,
                                              stylesheets=self._style.stylesheets
                                              ['settings_tab']['graphics_settings_widget']
                                              ['font_selection_widget']['font_family_selector']
                                              ['label'])
                                    set_style(widget=self.combobox,
                                              stylesheets=self._style.stylesheets
                                              ['settings_tab']['graphics_settings_widget']
                                              ['font_selection_widget']['font_family_selector']
                                              ['combobox'])

                            def make_label(self):
                                self.label = QLabel('Family')
                                self.layout.addWidget(self.label)
                                self.label.setAlignment(Qt.AlignLeft)

                            def make_combobox(self):
                                self.combobox = QFontComboBox()
                                self.layout.addWidget(self.combobox)

                                # User interactions
                                def update_family():
                                    self.chosen_font_family = self.combobox.currentText()

                                    self.graphics_settings_widget.chosen_style. \
                                        font['family'] = self.chosen_font_family
                                    self.graphics_settings_widget.update_example_task()

                                self.combobox.currentTextChanged.connect(update_family)
                                # Set the initial font
                                self.combobox.blockSignals(True)
                                self.combobox.setCurrentText(self.chosen_font_family)
                                self.combobox.blockSignals(False)

                        class FontSelectionWidget(QFrame):
                            """
                            This widget contains:

                                - A title stating the purpose
                                - A font selector widget for each section of a widget's font, as defined in
                                  taskplanner.gui.styles module
                            """
                            def __init__(self,
                                         planner: Planner,
                                         graphics_settings_widget: GraphicsSettingsWidget,
                                         parent: QWidget = None,
                                         style: PlannerWidgetStyle = DEFAULT_PLANNER_STYLE):
                                self.planner = planner
                                self.graphics_settings_widget = graphics_settings_widget
                                self._style = style
                                super().__init__(parent=parent)
                                # Layout
                                self.layout = QVBoxLayout(self)
                                self.layout.setAlignment(Qt.AlignTop)
                                self.layout.setAlignment(Qt.AlignLeft)
                                # Label
                                self.make_title_label()
                                # Layout for font selection widgets
                                self.font_selectors_layout = QGridLayout()
                                self.layout.addLayout(self.font_selectors_layout)
                                # Make font selection widgets
                                self.make_font_selectors()
                                # Style
                                self.set_style()

                            def set_style(self, style: PlannerWidgetStyle = None):
                                self._style = style if style is not None else self._style
                                if self._style is not None:
                                    set_style(widget=self,
                                              stylesheets=self._style.stylesheets
                                              ['settings_tab']['graphics_settings_widget']
                                              ['font_selection_widget']
                                              ['main'])
                                    set_style(widget=self.title_label,
                                              stylesheets=self._style.stylesheets
                                              ['settings_tab']['graphics_settings_widget']
                                              ['font_selection_widget']
                                              ['title_label'])
                                    for selector in self.font_selectors.values():
                                        selector.set_style(self._style)

                            def make_title_label(self):
                                self.title_label = QLabel()
                                self.layout.addWidget(self.title_label)
                                # Set text
                                self.title_label.setText('Font')

                            def make_font_selectors(self):
                                self.font_selectors = {}
                                font_properties = list(self.graphics_settings_widget.chosen_style.font.keys())
                                font_properties.remove('family')
                                n_cols = 3
                                n_rows = 2
                                for i in range(len(font_properties)):
                                    col = i % n_cols
                                    row = int(i/n_cols)
                                    font_property = font_properties[i]
                                    widget = FontSizeSelector(planner=self.planner,
                                                           graphics_settings_widget=self.graphics_settings_widget,
                                                           font_property=font_property,
                                                           parent=self,
                                                           style=self._style)
                                    self.font_selectors_layout.addWidget(widget, row, col)
                                    self.font_selectors[font_property] = widget

                                self.font_selectors['family'] = FontFamilySelector(planner=self.planner,
                                                                                   graphics_settings_widget=self.graphics_settings_widget,
                                                                                   parent=self,
                                                                                   style=self._style)
                                self.font_selectors_layout.addWidget(self.font_selectors['family'], 3, 0)


                        self.font_selection_widget = FontSelectionWidget(planner=self.planner,
                                                                                          graphics_settings_widget=self,
                                                                                          parent=self,
                                                                                          style=self._style)
                        self.layout.addWidget(self.font_selection_widget)

                    def make_apply_pushbutton(self):
                        self.apply_pushbutton = QPushButton('Apply Changes')
                        self.layout.addWidget(self.apply_pushbutton)

                        def clicked():
                            self.planner_widget.set_style(PlannerWidgetStyle(color_palette=self.chosen_style.color_palette,
                                                                             font=self.chosen_style.font,
                                                                             style_name=self.chosen_style.style_name))

                        self.apply_pushbutton.clicked.connect(clicked)

                    def make_example_task_widget(self):
                        planner = Planner()
                        planner.add_tasks(self.example_task)
                        self.example_task_widget = TaskWidget(task=self.example_task,
                                                              planner=planner,
                                                              parent=self,
                                                              style=TaskWidgetStyle(
                                                                  color_palette=self.chosen_style.color_palette,
                                                                  font=self.chosen_style.font,
                                                                  style_name=self.chosen_style.style_name
                                                              ))
                        self.layout.addWidget(self.example_task_widget.scrollarea)
                        self.example_task_widget.title_widget.textedit.setReadOnly(True)
                        task_widget_widget_open.disconnect(self.example_task_widget.hide)

                    def update_example_task(self):
                        self.example_task_widget.hide()
                        self.layout.removeItem(self.layout.itemAt(self.layout.count() - 1))
                        self.make_example_task_widget()


                self.graphics_settings_widget = GraphicsSettingsWidget(planner=self.planner,
                                                                       planner_widget=self.planner_widget,
                                                                       parent=self,
                                                                       style=self._style)


        self.settings_tab = SettingsTab(planner=self.planner,
                                        planner_widget=self,
                                        parent=self,
                                        style=self._style)
        self.addTab(self.settings_tab, 'Settings')



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
        self._style = style
        super().__init__(parent=parent)
        # Layout
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignTop)
        # Subtask widgets
        self.task_widgets = []
        self.layout.addStretch()
        self.make_task_widgets()
        # Set style
        self.set_style()

        slots = [slot for slot in self.planner.tasks_changed._slots if
                 'TaskListWidget.' in str(slot)]
        for slot in slots:
            self.planner.tasks_changed.disconnect(slot)
        self.planner.tasks_changed.connect(lambda **kwargs: self.make_task_widgets())

    def set_style(self, style: PlannerWidgetStyle = None):
        self._style = style if style is not None else self._style
        if self._style is not None:
            for widget in self.task_widgets:
                widget.set_style(TaskWidgetStyle(color_palette=self._style.color_palette,
                                                 font=self._style.font,
                                                 style_name=self._style.style_name))

    def make_task_widgets(self):
        self.layout.removeItem(self.layout.itemAt(self.layout.count() - 1))
        for task in self.planner.tasks:
            if task not in [widget.task for widget in self.task_widgets]:
                widget = TaskWidgetSimple(parent=self,
                                          task=task,
                                          planner=self.planner,
                                          style=TaskWidgetStyle(color_palette=self._style.color_palette,
                                                                font=self._style.font,
                                                                style_name=self._style.style_name)
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
        self.timelines_layout.setSpacing(self.task_list_widget.layout.spacing())
        self.timelines_layout.setAlignment(Qt.AlignTop)
        self.layout.addLayout(self.timelines_layout)
        #self.timelines_layout.addStretch()
        self.make_timelines()

        slots = [slot for slot in self.planner.tasks_changed._slots if
                 'CalendarWidget.' in str(slot)]
        for slot in slots:
            self.planner.tasks_changed.disconnect(slot)
        self.planner.tasks_changed.connect(lambda **kwargs: self.make_timelines())

        self.set_style()
        self.layout.addStretch()

    def set_style(self, style: PlannerWidgetStyle = None):
        self._style = style if style is not None else self._style
        if self._style is not None:
            set_style(widget=self,
                      stylesheets=self._style.stylesheets
                      ['planner_tab']
                      ['calendar_widget']['main'])
            for widget in self.month_widgets:
                widget.set_style(self._style)
            for widget in self.timeline_widgets:
                widget.set_style(self._style)

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
                '''
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
                '''
                if calendar_widget.view_type in ['weekly',
                                                 'daily']:
                    self.layout.setContentsMargins(0, 0, 0, 0)
                    self.week_widgets_layout.setSpacing(0)
                    self.make_week_widgets()
                    self.layout.insertStretch(1)
                else:
                    self.setFixedWidth(int(SCREEN_WIDTH * 0.13))
                # Style
                self.set_style()

            def set_style(self, style: PlannerWidgetStyle = None):
                self._style = style if style is not None else self._style
                if self._style is not None:
                    if self.calendar_widget.view_type in ['weekly',
                                                          'daily']:
                        stylesheet = self._style.stylesheets['planner_tab']['calendar_widget']['month_widget']
                        stylesheet['main'] = stylesheet['main'].replace('border:0.5px', 'border:0px')
                        stylesheet['label'] = stylesheet['label'].replace(
                            'background-color:None',
                            f'background-color:{self._style.color_palette["background 2"]}')
                        self._style.stylesheets['planner_tab']['calendar_widget']['month_widget'] = stylesheet
                        self.layout.setAlignment(Qt.AlignLeft)
                    else:
                        stylesheet = self._style.stylesheets['planner_tab']['calendar_widget']['month_widget']
                        stylesheet['main'] = stylesheet['main'].replace('border:0px', 'border:0.5px')
                        stylesheet['label'] = stylesheet['label'].replace(
                            f'background-color:{self._style.color_palette["background 2"]}',
                            'background-color:None')
                        self._style.stylesheets['planner_tab']['calendar_widget']['month_widget'] = stylesheet
                        self.layout.setAlignment(Qt.AlignCenter)
                    set_style(widget=self,
                              stylesheets=self._style.stylesheets
                              ['planner_tab']
                              ['calendar_widget']
                              ['month_widget'])
                    for widget in self.week_widgets:
                        widget.set_style(self._style)

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
                        '''
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
                        '''
                        if calendar_widget.view_type == 'daily':
                            self.layout.setContentsMargins(0, 0, 0, 0)
                            self.day_widgets_layout.setSpacing(0)
                            self.make_day_widgets()
                        else:
                            self.setFixedWidth(int(SCREEN_WIDTH * 0.05))
                        # Style
                        self.set_style()

                    def set_style(self, style: PlannerWidgetStyle = None):
                        self._style = style if style is not None else self._style
                        if self._style is not None:
                            if self.calendar_widget.view_type == 'daily':
                                stylesheet = self._style.stylesheets['planner_tab']['calendar_widget']['week_widget']
                                stylesheet['main'] = stylesheet['main'].replace('border:0.5px', 'border:0px')
                                self._style.stylesheets['planner_tab']['calendar_widget']['week_widget'] = stylesheet
                                self.layout.setAlignment(Qt.AlignLeft)
                            else:
                                stylesheet = self._style.stylesheets['planner_tab']['calendar_widget']['week_widget']
                                stylesheet['main'] = stylesheet['main'].replace('border:0px', 'border:0.5px')
                                self._style.stylesheets['planner_tab']['calendar_widget']['week_widget'] = stylesheet
                                self.layout.setAlignment(Qt.AlignCenter)

                            set_style(widget=self,
                                      stylesheets=self._style.stylesheets
                                      ['planner_tab']
                                      ['calendar_widget']
                                      ['week_widget'])
                            for widget in self.day_widgets:
                                widget.set_style(self._style)

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
                                self.set_style()

                            def set_style(self, style: PlannerWidgetStyle = None):
                                self._style = style if style is not None else self._style
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
                self.dragging_mode = None # 'start' or 'end'
                super().__init__(parent=parent)
                # Layout
                self.layout = QVBoxLayout(self)
                self.setContentsMargins(0, 0, 0, 0)
                self.layout.setContentsMargins(0, 0, 0, 0)
                if add_to_timelines_layout and hasattr(self.parent(), 'timelines_layout'):
                    self.parent().timelines_layout.addWidget(self)
                self.setFixedHeight(self.task_widget.task_line_widget.height())
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
                # Style
                self.set_style()
                '''
                from PyQt5.Qt import QGraphicsDropShadowEffect, QColor
                self.shadow = QGraphicsDropShadowEffect()
                self.shadow.setColor(QColor(self._style.color_palette['background 2']))
                self.shadow.setBlurRadius(10)
                self.label_pushbutton.setGraphicsEffect(self.shadow)
                '''

            def set_style(self, style: PlannerWidgetStyle = None):
                self._style = style if style is not None else self._style
                if self._style is not None:
                    set_style(widget=self,
                              stylesheets=self._style.stylesheets
                              ['planner_tab']
                              ['calendar_widget']
                              ['timeline']['main'])
                    self.set_color()
                    for widget in self.sub_timelines:
                        widget.set_style(self._style)

            def make_label_pushbutton(self):
                self.label_pushbutton = QPushButton()
                # Layout
                self.label_layout.addWidget(self.label_pushbutton)
                self.set_height()

                def clicked():
                    task_widget = TaskWidget(task=self.task,
                                             planner=self.planner,
                                             style=TaskWidgetStyle(color_palette=self._style.color_palette,
                                                                   font=self._style.font,
                                                                   style_name=self._style.style_name))
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
                                                 style=TaskWidgetStyle(color_palette=self._style.color_palette,
                                                                       font=self._style.font,
                                                                       style_name=self._style.style_name))

                        task_widget.show()
                    elif event.type() == QEvent.MouseButtonPress:
                        if event.pos().x() < self.label_pushbutton.width() / 2:
                            self.dragging_mode = 'start'
                        else:
                            self.dragging_mode = 'end'
                        self.label_pushbutton.setMouseTracking(True)
                    elif event.type() == QEvent.MouseMove and self.label_pushbutton.hasMouseTracking():
                        if self.dragging_mode == 'start':
                            start_date = self.get_start_date(self.label_pushbutton.x() + event.pos().x())
                            try:
                                self.task.start_date = start_date
                            except ValueError:
                                pass
                        else:
                            end_date = self.get_end_date(self.label_pushbutton.x() + event.pos().x())
                            try:
                                self.task.end_date = end_date
                            except ValueError:
                                pass
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
                self.timeline_widgets += [widget]
                if task_widget.task.is_top_level:
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


class TaskBucketWidget(QFrame):
    """
    This widget contains:

        - A label indicating the main property of the task bucket
        - A list of widgets sharing the bucket's property
    """
    def __init__(self,
                 property_name: str,
                 property_value: str,
                 planner: Planner,
                 parent: QWidget = None,
                 style: PlannerWidgetStyle = None):
        """

        :param property_name:
        :param property_value:
        :param planner:
        :param parent:
        :param style:
        """
        if not hasattr(Task(), property_name):
            raise ValueError(f'Tasks have no such property as "{property_name}"')
        self.property_name = property_name
        self.property_value = property_value
        self.planner = planner
        self._style = style
        super().__init__(parent=parent)
        # Layout
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.setContentsMargins(0, 0, 0, 0)
        # Label
        self.make_label()
        self.layout.addSpacing(20)
        # Task List Widget
        self.make_task_list()
        # Scrollarea for task list
        self.task_list_scrollarea = QScrollArea()
        self.task_list_scrollarea.setWidgetResizable(True)
        self.task_list_scrollarea.setWidget(self.task_list_widget)
        self.layout.addWidget(self.task_list_scrollarea)
        # Style
        self.set_style()

    def set_style(self, style: PlannerWidgetStyle = None):
        self._style = style if style is not None else self._style
        if self._style is not None:
            set_style(widget=self,
                      stylesheets=self._style.stylesheets
                      ['task_buckets_tab']['bucket_list_widget']['bucket_widget'])

    def make_label(self):
        self.label = QLabel()
        self.layout.addWidget(self.label)
        self.label.setAlignment(Qt.AlignCenter)
        if self.property_value is None:
            text = f'No {self.property_name.title()}'
        else:
            text = self.property_value.title()
        self.label.setText(text)

    def make_task_list(self):
        class BucketTaskListWidget(QFrame):
            """
            This widget contains a list of widgets sharing the bucket's property
            """
            def __init__(self,
                         property_name: str,
                         property_value: str,
                         planner: Planner,
                         parent: QWidget = None,
                         style: PlannerWidgetStyle = DEFAULT_PLANNER_STYLE
                         ):
                """

                :param property_name:
                :param property_value:
                :param planner:
                :param parent:
                :param style:
                """
                if not hasattr(Task(), property_name):
                    raise ValueError(f'Tasks have no such property as "{property_name}"')
                self.property_name = property_name
                self.property_value = property_value
                self.planner = planner
                self._style = style
                self.task_widgets = []
                self.tasks = []
                self.tasks_updated = Signal()
                super().__init__(parent=parent)
                # Layout
                self.layout = QVBoxLayout(self)
                self.layout.setAlignment(Qt.AlignTop)
                self.layout.setContentsMargins(0, 0, 0, 0)
                self.layout.setSpacing(20)
                # Task widgets
                self.planner.tasks_changed.connect(self.make_task_widgets)
                self.make_task_widgets()
                self.destroyed.connect(self.disconnect_tasks)
                # Style
                self.set_style()

            def set_style(self, style: PlannerWidgetStyle = None):
                self._style = style if style is not None else self._style
                if self._style is not None:
                    set_style(widget=self,
                              stylesheets=self._style.stylesheets
                              ['task_buckets_tab']
                              ['bucket_list_widget']
                              ['bucket_widget']
                              ['task_list_widget']['main'])
                    set_style(widget=self,
                              stylesheets=self._style.stylesheets
                              ['task_buckets_tab']
                              ['bucket_list_widget']
                              ['bucket_widget']
                              ['task_list_scrollarea']['main'])
                    for widget in self.task_widgets:
                        widget.set_style(TaskWidgetStyle(color_palette=self._style.color_palette,
                                                         font=self._style.font,
                                                         style_name=self._style.style_name))

            def make_task_widgets(self, **kwargs):
                all_tasks = self.planner.all_tasks

                for task in all_tasks:
                    if task not in self.tasks and getattr(task, self.property_name) == self.property_value:
                        # Create task widget
                        widget = TaskWidgetSimple(parent=self,
                                                  task=task,
                                                  planner=self.planner,
                                                  style=TaskWidgetStyle(color_palette=self._style.color_palette,
                                                                        font=self._style.font,
                                                                        style_name=self._style.style_name)
                                                  )
                        widget.setContentsMargins(10,
                                                  0,
                                                  int(SCREEN_WIDTH * 0.003),
                                                  0)
                        widget.layout.setContentsMargins(10,
                                                         0,
                                                         int(SCREEN_WIDTH * 0.003),
                                                         0)
                        # Add task widget to layout
                        self.layout.addWidget(widget)
                        self.task_widgets += [widget]
                        # Add new task
                        self.tasks += [task]
                        # Connect task and task list update
                        getattr(task, f'{self.property_name}_changed') \
                            .connect(self.make_task_widgets)
                # Remove non-existent tasks
                for widget in self.task_widgets:
                    if widget.task not in self.planner.all_tasks \
                            or getattr(widget.task, self.property_name) != self.property_value:
                        if widget.task in self.tasks:
                            self.tasks.remove(widget.task)
                        getattr(widget.task, f'{self.property_name}_changed').disconnect(self.make_task_widgets)
                        widget.hide()
                        self.task_widgets.remove(widget)
                        self.layout.removeWidget(widget)
                        if not self.tasks and self.property_name not in ['priority', 'progress']:
                            self.hide()

                self.tasks_updated.emit()


            def disconnect_tasks(self):
                for task in self.tasks:
                    getattr(task, f'{self.property_name}_changed').disconnect(self.make_task_widgets)
                self.planner.tasks_changed.disconnect(self.make_task_widgets)

        self.task_list_widget = BucketTaskListWidget(property_name=self.property_name,
                                                     property_value=self.property_value,
                                                     planner=self.planner,
                                                     parent=self,
                                                     style=self._style)


class BucketListWidget(QFrame):
    """
    This widget contains a list of TaskBucketWidget. Each task bucket is labeled
    with the property value that is common among all tasks of the bucket
    """

    def __init__(self,
                 planner: Planner,
                 property_name: str = 'priority',
                 parent: QWidget = None,
                 style: PlannerWidgetStyle = DEFAULT_PLANNER_STYLE,
                 ):
        self.planner = planner
        self._style = style
        self.bucket_widgets = []
        self.property_name_changed = Signal()
        self.buckets_updated = Signal()
        super().__init__(parent=parent)
        # Layout
        self.layout = QHBoxLayout(self)
        self.layout.setAlignment(Qt.AlignLeft)
        self.layout.setContentsMargins(0, 0, 0, 0)
        # Set property name and automatically make the task buckets
        self.property_name = property_name
        # Style
        self.set_style()

    def set_style(self, style: PlannerWidgetStyle = None):
        self._style = style if style is not None else self._style
        if self._style is not None:
            set_style(widget=self,
                      stylesheets=self._style.stylesheets
                      ['task_buckets_tab']['bucket_list_widget']['main'])
            for widget in self.bucket_widgets:
                widget.set_style(self._style)

    @property
    def property_name(self):
        if not hasattr(self, '_property_name'):
            self._property_name = 'priority'
        return self._property_name

    @property_name.setter
    def property_name(self, value):
        if value not in BUCKET_PROPERTY_NAMES:
            raise ValueError(f'Invalid property name "{value}". Valid property names are '
                             f'{tuple(BUCKET_PROPERTY_NAMES)}')
        if not hasattr(self, '_property_name'):
            self._property_name = value
        self._property_name = value
        self.disconnect_buckets()
        self.make_bucket_widgets()
        self.property_name_changed.emit()

    def disconnect_buckets(self):
        for widget in self.bucket_widgets:
            widget.hide()
            widget.task_list_widget.disconnect_tasks()
        self.bucket_widgets = []

    def make_task_connections(self):
        self.planner.tasks_changed.disconnect(self.make_bucket_widgets)
        self.planner.tasks_changed.connect(self.make_bucket_widgets)
        all_tasks = self.planner.all_tasks
        for task in all_tasks:
            # Connect task and task list update
            getattr(task, f'{self.property_name}_changed').disconnect(self.make_bucket_widgets)
            getattr(task, f'{self.property_name}_changed') \
                .connect(self.make_bucket_widgets)
            # Connect with subtask changes
            task.children_changed.disconnect(self.make_bucket_widgets)
            task.children_changed.connect(self.make_bucket_widgets)

    def make_bucket_widgets(self, **kwargs):
        all_tasks = self.planner.all_tasks
        # Identify the property values
        property_values = []
        if self.property_name not in ['priority',
                                      'progress']:
            property_values = list(set([getattr(task,
                                                self.property_name)
                                        for task in all_tasks]))
            if None in property_values:
                property_values.remove(None)
                property_values.sort()
                property_values = [None] + property_values
            else:
                property_values.sort()
        else:
            from taskplanner.tasks import PRIORITY_LEVELS, PROGRESS_LEVELS
            dictionary = PRIORITY_LEVELS if self.property_name == 'priority' else PROGRESS_LEVELS
            property_values = list(dictionary.keys())
            property_values.sort(key=lambda x: dictionary[x])

        # Add buckets
        for value in property_values:
            if value not in [w.property_value for w in self.bucket_widgets]:
                widget = TaskBucketWidget(property_name=self.property_name,
                                          property_value=value,
                                          planner=self.planner,
                                          parent=self,
                                          style=self._style)
                widget.setFixedWidth(int(SCREEN_WIDTH * 0.295))
                self.layout.addWidget(widget)
                self.bucket_widgets += [widget]
            else:
                widget = [w for w in self.bucket_widgets
                          if w.property_value == value][0]
                widget.task_list_widget.make_task_widgets()

        # Remove buckets associated to non-existent values
        for widget in self.bucket_widgets:
            if widget.property_name not in ['priority', 'progress']:
                if widget.property_name != self.property_name \
                        or widget.property_value not in property_values or not widget.task_list_widget.tasks:
                    widget.task_list_widget.disconnect_tasks()
                    widget.hide()
                    # self.layout.removeWidget(widget)
                    self.bucket_widgets.remove(widget)

        self.buckets_updated.emit()

        self.make_task_connections()



