"""
This module defines a planner widget and related widgets.
"""
from PyQt5.QtCore import Qt
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
    QFrame
    )

from datetime import date
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
                self.layout = QHBoxLayout(self)
                self.layout.setAlignment(Qt.AlignLeft)
                # Geometry
                self.setGeometry(self.parent().geometry())
                # Task list widget
                self.make_task_list_widget()
                ## Scroll area
                self.task_list_scrollarea = QScrollArea()
                self.task_list_scrollarea.setWidgetResizable(True)
                self.task_list_scrollarea.setFixedSize(int(self.width()*0.3),
                                                       int(self.height()*0.95))
                self.task_list_scrollarea.setWidget(self.task_list_widget)
                self.layout.addWidget(self.task_list_scrollarea)
                ## New task textedit
                self.task_list_widget.new_task_textedit.setFixedSize(int(self.width()*0.15),
                                                                     int(self.height() * 0.035))
                # Timelines widget
                self.make_timelines_widget()
                ## Scroll area
                self.timelines_scrollarea = QScrollArea()
                self.timelines_scrollarea.setWidgetResizable(True)
                self.timelines_scrollarea.setWidget(self.timelines_widget)
                self.layout.addWidget(self.timelines_scrollarea)
                ## Relative size of month, week and day widgets
                for month_widget in self.timelines_widget.month_widgets:
                    month_widget.setFixedWidth(int(self.timelines_widget.width()*0.2))
                    month_widget.label.setFixedHeight(int(self.height()*0.05))
                    for week_widget in month_widget.week_widgets:
                        week_widget.setFixedWidth(int(month_widget.width() / 5))
                        for day_widget in week_widget.day_widgets:
                            day_widget.setFixedWidth(int(week_widget.width() / 7))
                if self._style is not None:
                    set_style(widget=self,
                              stylesheets=self._style.stylesheets
                              ['planner_tab'])



            def make_task_list_widget(self):
                self.task_list_widget = TaskListWidget(planner=self.planner,
                                                       parent=self)

            def make_timelines_widget(self):
                class TimelinesWidget(QWidget):
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
                                 start_date: date=date.today(),
                                 n_months: int=3,
                                 style: PlannerWidgetStyle = None):
                        """
                        :param planner:
                        :param task_list_widget:
                        :param parent:
                        """
                        self.planner = planner
                        self.task_list_widget = task_list_widget
                        self.start_date = start_date
                        self._style = style
                        self.month_widgets = []
                        N_MAX = 24
                        self.n_months = n_months
                        if n_months > N_MAX:
                            raise ValueError(
                                f'Visualizing too many months ({n_months}). Maximum number of months is {N_MAX}')
                        super().__init__(parent=parent)
                        # Layout
                        self.layout = QVBoxLayout(self)
                        self.layout.setSpacing(0)
                        # Horizontal layout for month widgets
                        self.month_widgets_layout = QHBoxLayout()
                        self.layout.addLayout(self.month_widgets_layout)
                        # Months Panel
                        self.make_month_widgets()


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
                                         date: date,
                                         parent: QWidget=None,
                                         style: PlannerWidgetStyle=None):
                                self.planner = Planner
                                self.task_list_widget = task_list_widget
                                self._style = style
                                self.date = date
                                self.week_widgets = []
                                super().__init__(parent=parent)
                                # Layout
                                self.layout = QVBoxLayout(self)
                                self.layout.setAlignment(Qt.AlignTop)
                                # Month label
                                self.make_label()
                                # Horizontal layout for week widgets
                                self.week_widgets_layout = QHBoxLayout()
                                self.week_widgets_layout.setAlignment(Qt.AlignLeft)
                                self.layout.addLayout(self.week_widgets_layout)
                                # Week widgets
                                self.make_week_widgets()
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
                                                 date: date,
                                                 parent: QWidget = None,
                                                 style: PlannerWidgetStyle = None):
                                        self.planner = Planner
                                        self.task_list_widget = task_list_widget
                                        self._style = style
                                        self.date = date
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
                                        self.day_widgets_layout.setSpacing(0)
                                        self.layout.addLayout(self.day_widgets_layout)
                                        # Day widgets
                                        self.make_day_widgets()
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
                                        is_day_of_week = True
                                        self.n_days = 0

                                        while is_day_of_week:
                                            d = self.date + relativedelta(days=self.n_days)
                                            if d == self.date:
                                                d_previous = self.date
                                            else:
                                                d_previous = self.date + relativedelta(days=self.n_days-1)
                                            if d.weekday() % 7 < d_previous.weekday() % 7:
                                                is_day_of_week = False
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
                                                                       date=self.dates[-1],
                                                                       parent=self,
                                                                       style=self._style)]
                                    self.dates += [self.week_widgets[-1].dates[-1] + relativedelta(days=1)]
                                    self.week_widgets_layout.addWidget(self.week_widgets[-1])

                        self.dates = []
                        reference_date = date(self.start_date.year,
                                              self.start_date.month,
                                              1)
                        for count in range(self.n_months):
                            self.dates += [reference_date + relativedelta(months=count)]
                            self.month_widgets += [MonthWidget(planner=self.planner,
                                                               task_list_widget=self.task_list_widget,
                                                               date=self.dates[-1],
                                                               parent=self,
                                                               style=self._style)]
                            self.month_widgets_layout.addWidget(self.month_widgets[-1])

                self.timelines_widget = TimelinesWidget(planner=self.planner,
                                                        task_list_widget=self.task_list_widget,
                                                        parent=self,
                                                        start_date=date.today(),
                                                        style=self._style,
                                                        n_months=6)
                self.layout.addWidget(self.timelines_widget)


        self.planner_tab = PlannerTab(planner=self.planner,
                                      parent=self,
                                      style=self._style)
        self.addTab(self.planner_tab, 'Planner')



    def show(self):
        super().show()


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
        super().__init__(parent=parent)
        # Layout
        self.layout = QVBoxLayout(self)
        # self.layout.setAlignment(Qt.AlignTop)
        # New task textedit
        self.make_new_task_textedit()
        # Subtask widgets
        self.task_widgets = []
        self.layout.addStretch()
        self.make_task_widgets()

        slots = [slot for slot in self.planner.tasks_changed._slots if
                 'TaskListWidget.' in str(slot)]
        for slot in slots:
            self.planner.tasks_changed.disconnect(slot)
        self.planner.tasks_changed.connect(lambda **kwargs: self.make_task_widgets())

    def make_new_task_textedit(self):
        # textedit to define a new assignee when the 'plus' button is clicked
        self.new_task_textedit = QTextEdit()
        # Layout
        self.layout.addWidget(self.new_task_textedit)

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
        self.layout.addStretch()