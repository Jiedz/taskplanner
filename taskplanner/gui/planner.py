"""
This module defines a planner widget and related widgets.
"""
from PyQt5.QtCore import Qt, QPoint
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
    QGridLayout
    )

from signalslot import Signal
from numpy import floor, ceil
from datetime import date
import logging
from dateutil.relativedelta import relativedelta
from taskplanner.tasks import Task
from taskplanner.planner import Planner
from taskplanner.gui.tasks import TaskWidget, TaskWidgetSimple
from taskplanner.gui.styles import TaskWidgetStyle, PlannerWidgetStyle, ICON_SIZES
from taskplanner.gui.utilities import set_style, get_primary_screen

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
                 style: PlannerWidgetStyle = DEFAULT_PLANNER_STYLE
                 ):
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
                      stylesheets=self._style.stylesheets)

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
                self.new_task_settings_layout.addSpacing(int(SCREEN_WIDTH * 0.25)
                                                         - self.new_task_textedit.width())
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
                self.view_selector.setFixedHeight(int(self.height() * 0.08))

                if self._style is not None:
                    set_style(widget=self,
                              stylesheets=self._style.stylesheets
                              ['planner_tab'])

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
                                                        style=self._style,
                                                        n_months=6)

        self.planner_tab = PlannerTab(planner=self.planner,
                                      parent=self,
                                      style=self._style)
        self.addTab(self.planner_tab, 'Planner')


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
                 view_type: str = 'daily',
                 start_date: date = date.today(),
                 n_months: int = 3,
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
        :param n_months: int, optional
            The number of months to be displayed in the timeline
        :param style: :py:class:'taskplanner.gui.styles.PlannerWidgetStyle', optional
            The style of this widget.
        """
        self.planner = planner
        self.task_list_widget = task_list_widget
        self.start_date = start_date
        self._style = style
        self.month_widgets = []
        self.timeline_widgets = []
        self._view_type = view_type
        self.n_months = n_months
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
        self.timelines_layout.addStretch()
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
                      ['calendar_widget'])

    @property
    def view_type(self):
        return self._view_type

    @view_type.setter
    def view_type(self, value):
        if value not in TIMELINE_VIEW_TYPES:
            raise ValueError(f'Invalid  timeline view type {value}.'
                             f' Valid view types are {TIMELINE_VIEW_TYPES}')
        self._view_type = value
        self.view_type_changed.emit()
        self.make_month_widgets()

    def update_all(self):
        self.make_month_widgets()
        self.make_timelines()

    def make_start_end_date_widgets(self):
        logging.warning(f'Funtion "make_start_end_date_widgets" of widget {self} is not implemented yet.')

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
                    self.layout.setContentsMargins(0, 0, 0, 0)
                    self.week_widgets_layout.setSpacing(0)
                    self.make_week_widgets()
                    self.layout.insertStretch(1)
                else:
                    self.setFixedWidth(int(SCREEN_WIDTH*0.13))
                # Set style
                if self._style is not None:
                    set_style(widget=self,
                              stylesheets=self._style.stylesheets
                              ['planner_tab']
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
                            self.layout.setContentsMargins(0, 0, 0, 0)
                            self.day_widgets_layout.setSpacing(0)
                            self.make_day_widgets()
                        else:
                            self.setFixedWidth(int(SCREEN_WIDTH*0.05))
                        # Set style
                        if self._style is not None:
                            set_style(widget=self,
                                      stylesheets=self._style.stylesheets
                                      ['planner_tab']
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
                import calendar
                self.n_weeks = len(calendar.monthcalendar(self.date.year,
                                                          self.date.month)
                                   )
                reference_date = date(self.date.year,
                                      self.date.month,
                                      1)
                self.dates += [reference_date]
                for count in range(self.n_weeks):
                    self.week_widgets += [WeekWidget(planner=self.planner,
                                                     task_list_widget=self.task_list_widget,
                                                     calendar_widget=self.calendar_widget,
                                                     date=self.dates[-1],
                                                     parent=self,
                                                     style=self._style)]
                    if len(self.week_widgets[-1].dates) > 0:
                        self.dates += [self.week_widgets[-1].dates[-1] + relativedelta(days=1)]
                    else:
                        self.dates += [self.week_widgets[-1].date + relativedelta(weeks=1)]
                    self.week_widgets_layout.addWidget(self.week_widgets[-1])

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
                         style: PlannerWidgetStyle = None):
                self.task_widget = task_widget
                self.task = self.task_widget.task
                self.calendar_widget = calendar_widget
                self._style = style
                super().__init__(parent=parent)
                # Layout
                self.layout = QVBoxLayout(self)
                self.setContentsMargins(0, 0, 0, 0)
                self.layout.setContentsMargins(0, 0, 0, 0)
                # Horizontal layout for label
                self.label_layout = QHBoxLayout()
                self.label_layout.setAlignment(Qt.AlignLeft)
                self.layout.addLayout(self.label_layout)
                # Insert first spacing
                self.label_layout.insertSpacing(0, 0)
                # Label
                self.make_label()
                # Sub-timelines
                self.sub_timelines = []
                self.make_sub_timelines()
                slots = [slot for slot in self.task.children_changed._slots if
                         'Timeline.' in str(slot)]
                for slot in slots:
                    self.task.children_changed.disconnect(slot)
                self.task.children_changed.connect(lambda **kwargs: self.make_sub_timelines())

            def make_label(self):
                self.label = QLabel()
                # Layout
                self.label_layout.addWidget(self.label)
                self.set_height()
                # Set text
                self.label.setText(self.task.name)
                self.task.name_changed.connect(lambda **kwargs: self.label.setText(self.task.name))
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
                QLabel
                {
                    background-color:%s;
                    border:1px solid %s;
                }
                ''' % (self.task.color,
                       self.task.color)
                self.setStyleSheet(style_sheet)

            def set_height(self):
                self.label.setFixedHeight(int(SCREEN_HEIGHT * 0.041))

            def set_start_position(self):
                delta_date = self.task.start_date - self.calendar_widget.start_date
                spacing = 0
                # Remove spacing
                self.label_layout.removeItem(self.label_layout.itemAt(0))
                if self.calendar_widget.view_type == 'daily':
                    day_width = self.calendar_widget.month_widgets[0].week_widgets[0].day_widgets[0].width()
                    n_day_widths = delta_date.days + 2
                    spacing = n_day_widths * day_width
                elif self.calendar_widget.view_type == 'weekly':
                    week_width = self.calendar_widget.month_widgets[0].week_widgets[0].width()
                    n_days = delta_date.days + 2
                    month_widgets = [m for m in self.calendar_widget.month_widgets if m.date <= self.task.start_date]
                    import calendar
                    n_weeks = 0
                    for m in month_widgets:
                        #week_widgets = [w for w in m.week_widgets if w.dates <= self.task.start_date]
                        n_weeks += len(calendar.monthcalendar(m.date.year,
                                                              m.date.month))
                    n_weeks = n_weeks - 1 + (self.task.start_date.weekday()) / 7
                    print(f'Number of weeks: {n_weeks}')
                    #print(f'Last week dates: {[d for d in week_widgets[-1].dates]}')
                    spacing = int(week_width * n_weeks)
                elif self.calendar_widget.view_type == 'monthly':
                    month_width = self.calendar_widget.month_widgets[0].width()

                    month_widgets = [m for m in self.calendar_widget.month_widgets
                                     if m.date <= self.task.start_date]
                    n_months = len(month_widgets) - 1
                    n_months = n_months + self.task.start_date.day / 30
                    spacing = int(n_months * month_width)
                # Add left spacing
                self.label_layout.insertSpacing(0, spacing)

            def set_length(self):
                view_type = self.calendar_widget.view_type
                if view_type == 'daily':
                    day_width = self.calendar_widget.month_widgets[0].week_widgets[0].day_widgets[0].width()
                    n_days = (self.task.end_date - self.task.start_date).days + 1
                    self.label.setFixedWidth(day_width*n_days)
                elif view_type == 'weekly':
                    week_width = self.calendar_widget.month_widgets[0].week_widgets[0].width()
                    n_days = (self.task.end_date - self.task.start_date).days + 1
                    n_weeks = int(n_days / 7) + n_days % 7 / 7
                    self.label.setFixedWidth(int(week_width * n_weeks))

            def set_geometry(self):
                self.set_start_position()
                self.set_length()

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
                                                parent=self,
                                                style=self._style)
                        # Add the sub-timeline to the main timelines layout
                        l.removeItem(l.itemAt(l.count() - 1))
                        # Find the correct position in the layout
                        # where the sub-timeline is inserted
                        index = self.task.descendants.index(subtask)
                        index += l.indexOf(self) + 1
                        l.insertWidget(index, sub_timeline)
                        # sub_timeline.setFixedHeight(self.height())
                        l.addStretch()
                        self.sub_timelines += [sub_timeline]
                # Remove non-existent sub-timelines
                for widget in self.sub_timelines:
                    if widget.task not in self.task.children:
                        index = l.indexOf(widget)
                        w = widget
                        while w == widget or (w is not None and widget.task in w.task.ancestors):
                            w.hide()
                            try:  # It may be that the widget had been removed from the list, but not hidden
                                self.calendar_widget.timeline_widgets.remove(w)
                            except:
                                pass
                            l.removeWidget(w)
                            if l.count() > 0:
                                try:
                                    w = l.itemAt(index).widget()
                                except:
                                    break
                            else:
                                break

        # Remove stretch
        self.timelines_layout.removeItem(self.timelines_layout.itemAt(self.timelines_layout.count() - 1))

        def add_timeline(task_w):
            if task not in [widget.task_widget.task for widget in self.timeline_widgets]:
                task_widget = [w for w in self.task_list_widget.task_widgets
                               if w.task == task][0]
                widget = Timeline(task_widget=task_widget,
                                  calendar_widget=self,
                                  parent=self,
                                  style=self._style)
                self.timelines_layout.addWidget(widget)
                self.timeline_widgets += [widget]

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
                while w == widget or widget.task in w.task.ancestors:
                    w.hide()
                    try:  # It may be that the widget had been removed from the list, but not hidden
                        self.timeline_widgets.remove(w)
                    except:
                        pass
                    self.timelines_layout.removeWidget(w)
                    if self.timelines_layout.count() > 0:
                        try:
                            w = self.timelines_layout.itemAt(index).widget()
                        except:
                            break
                    else:
                        break

            self.timelines_updated.emit()

        # Add stretch back
        self.timelines_layout.addStretch()
