"""
This module defines a task planner.
"""
from taskplanner.tasks import Task, _signal_changed_property
from signalslot import Signal
from PyQt5.Qt import QCalendar
from logging import warning
import textwrap
import os

class Planner:
    """
    This class defines a task planner.
    Its main function is to administer (keep track of) a set of tasks,
    as well as global features associated to task management -e.g., a list of categories and assignees.

    A task planner contains:

        - An updated list of tasks
        - An updated list of all categories
        - An updated list of all assignees
    """
    def __init__(self):
        for attr in ['tasks',
                     'categories',
                     'assignees']:
            setattr(self, f'_{attr}', [])

        for attr in ['tasks',
                     'categories',
                     'assignees']:
            setattr(self, f'{attr}_changed', Signal())

        self.calendar = QCalendar()

    @property
    def tasks(self):
        return self._tasks

    @property
    def categories(self):
        return self._categories

    @property
    def assignees(self):
        return self._assignees

    def add_tasks(self,
                  *tasks: Task):
        for task in tasks:
            if task not in self.tasks:
                self._tasks += [task]
                _signal_changed_property(task=task,
                                         signal=self.tasks_changed,
                                         property_name='children')
                self._add_new_values(task=task,
                                     signal=self.categories_changed,
                                     property_name='category')
                self._add_new_values(task=task,
                                     signal=self.categories_changed,
                                     property_name='assignee')
                self.tasks_changed.emit()

    def remove_tasks(self,
                     *tasks: Task):
        for task in tasks:
            if task in self.tasks:
                self._tasks.remove(task)
                '''
                _signal_changed_property(task=task,
                                         signal=self.tasks_changed,
                                         property_name='children')
                '''
                self.tasks_changed.emit()

    def add_categories(self,
                       *categories: str):
        for category in categories:
            if (category not in self.categories) and (category is not None):
                self._categories += [category]
                self.categories_changed.emit()

    def remove_categories(self,
                          *categories: str):
        for category in categories:
            if category in self.categories:
                self._categories.remove(category)
                self.categories_changed.emit()

    def add_assignees(self,
                      *assignees: str):
        for assignee in assignees:
            if (assignee not in self.assignees) and (assignee is not None):
                self._assignees += [assignee]
                self.assignees_changed.emit()

    def remove_assignees(self,
                         *assignees: str):
        for assignee in assignees:
            if assignee in self.assignees:
                self._assignees.remove(assignee)
                self.assignees_changed.emit()

    def _add_new_values(self,
                        task: Task,
                        signal: Signal,
                        property_name: str):
        if property_name not in ['category',
                                 'assignee']:
            raise ValueError(f'Invalid property "{property_name}". Valid properties are (category, assignee)')
        plural_form = f'{property_name[:-1]}ies' if property_name[-1]=='y' else f'{property_name}s'
        getattr(self, f'add_{plural_form}')(getattr(task, property_name))
        getattr(task, f'{property_name}_changed').connect(
            lambda **kwargs: signal.emit())
        for subtask in task.descendants:
            getattr(self, f'add_{plural_form}')(getattr(subtask, property_name))
            getattr(subtask, f'{property_name}_changed').connect(
                lambda **kwargs: signal.emit())
        '''
        if task.is_bottom_level and getattr(task, property_name) not in getattr(self, plural_form):
            getattr(self, plural_form).append(getattr(task, property_name))
            getattr(task, f'{property_name}_changed').connect(
                lambda **kwargs: signal.emit())
        else:
            for subtask in task.children:
                self._add_new_values(task=subtask,
                                     signal=signal,
                                     property_name=property_name)
        '''

    def to_string(self):
        # Write all the data except subtasks first
        string = '___PLANNER___'
        # Add tasks
        for task in self.tasks:
            string += f'\n___TOP LEVEL TASK___\n{task.to_string()}'
        return string

    @classmethod
    def from_string(cls,
                    string: str):
        planner = Planner()
        s = ''.join(string.split('___PLANNER___')[1:])
        task_strings = s.split('\n___TOP LEVEL TASK___')[1:]
        for task_string in task_strings:
            planner.add_tasks(Task.from_string(task_string))
        return planner

    def to_file(self,
                filename: str = None,
                access_mode:str = 'r+'):
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
                raise ValueError(f'Planner {self.name} has no file configured.')
            else:
                directory = os.path.sep.join(os.path.abspath(self.filename).split(os.path.sep)[:-1])
                if not os.path.exists(directory):
                    raise ValueError(f'No such directory "{directory}".')
        else:
            directory = os.path.sep.join(os.path.abspath(filename).split(os.path.sep)[:-1])
            if not os.path.exists(directory):
                warning(f'No such directory "{directory}". '
                        f'Attempting to use internal file name {self.filename}')
                self.to_file(filename=self.filename)
            else:
                self.filename = filename
        if ".txt" not in filename:
            filename += ".txt"
        access_mode = 'w' if not os.path.exists(filename) else access_mode
        # Define file
        file = open(filename, mode=access_mode, encoding='utf-8')
        file.write(self.to_string())
        file.close()

    @classmethod
    def from_file(cls,
                  filename: str,
                  full_content: bool = True):
        # Recognize the input file name or use the internally defined file name, if any.
        # Else, raise an error.
        if ".txt" not in filename:
            filename += ".txt"
        if not os.path.exists(filename):
            raise ValueError(f'No such file or directory "{filename}".')
        # Define file
        file = open(filename, mode='r', encoding='utf-8')
        planner = Planner.from_string(file.read())
        planner.filename = filename
        file.close()
        return planner

