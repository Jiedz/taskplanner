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
    QTabWidget
    )

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
        width, height = int(SCREEN_WIDTH), int(SCREEN_HEIGHT)
        self.setFixedSize(width,
                          height)
        # Scroll area
        self.scrollarea = QScrollArea()
        self.scrollarea.setWidgetResizable(True)
        self.scrollarea.setGeometry(self.geometry())
        self.scrollarea.setWidget(self)
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
                self.task_list_widget.setFixedSize(int(self.width()*0.5),
                                                   self.height())
                ## New task textedit
                self.task_list_widget.new_task_textedit.setFixedSize(int(self.width()*0.15),
                                                                     int(self.height() * 0.035))
                # Timelines widget

            def make_task_list_widget(self):
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
                        #self.layout.setAlignment(Qt.AlignTop)
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
                        self.layout.removeItem(self.layout.itemAt(self.layout.count()-1))
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

                self.task_list_widget = TaskListWidget(planner=self.planner,
                                                       parent=self)
                self.layout.addWidget(self.task_list_widget)

        self.planner_tab = PlannerTab(planner=self.planner,
                                      parent=self,
                                      style=self._style)
        self.addTab(self.planner_tab, 'Planner')



    def show(self):
        super().show()
        self.scrollarea.show()