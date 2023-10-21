'''
This module describes a task and the relation between parent and children tasks.
'''

# %% Imports
from anytree import Node
from inspect import currentframe, getargvalues
from datetime import datetime, date

# %% Task
PRIORITY_LEVELS = ["low", "medium", "high"]


class Task(Node):
    '''
    This class defines a task.

    A task contains:

    - A name
    - A category
    - A description
    - A priority level
    - A due date
    - An assignee

    A task is also represented as a node of a tree. Therefore, every task except top-level tasks, has a parent.
    '''

    def __init__(self,
                 parent = None,
                 name: str = "A Task",
                 category = "No Category",
                 description = "",
                 priority = "medium",
                 start_date: date = date.today(),
                 end_date: date = None,
                 assignee=None):
        '''
        :param parent: py:class:'Node', optional
            The parent of the current task. If 'None', the task is considered as a top-level task.
        :param name: str, optional
            The name of the task.
        :param category: str, optional
            The category to which this task belongs.
        :param description: str, optional
        :param priority: str, optional
            Priority of the task: "low", "medium" and "high"
        :param start_date: :py:class:'datetime.date', optional
            The task's start date. If not specified, the current date is used.
        :param end_date: :py:class:'datetime.date', optional
            The task's end date. If not specified, the current date is used.
        :param assignee: str, optional
            The name of the person who is assigned the task.
        '''
        super().__init__(name=name,
                         parent=parent) # A task is a node of a tree
        # Get the argument names passed to the __init__ function
        argvalues = getargvalues(currentframe())
        attribute_names = argvalues.args
        attribute_names.remove('parent')
        for a in attribute_names:
            # Initialize the internal attributes to 'None'
            setattr(self, f"_{a}", None)
        for a in attribute_names:
            # Set the corresponding properties to the passed argument values
            setattr(self, a, argvalues.locals[a])

    @property
    def start_date(self):
        return self._start_date

    @start_date.setter
    def start_date(self, value):
        if value is None:
            self._start_date = date.today()
        else:
            if 'datetime.date' not in str(type(value)):
                raise TypeError(f'Invalid start date type {type(value)}. Accepted types are ("datetime.date")')
            if self.end_date is not None:
                if value > self.end_date:
                    assert ValueError('Start date ({value}) is greater than end date ({self.end_date})')
            self._start_date = value

    @property
    def end_date(self):
        return self._end_date

    @end_date.setter
    def end_date(self, value):
        if value is None:
            self._end_date = date.today()
        else:
            if 'datetime.date' not in str(type(value)):
                raise TypeError(f'Invalid end date type {type(value)}. Accepted types are ("datetime.date")')
            if self.end_date is not None:
                if value < self.start_date:
                    assert ValueError('end date ({value}) is smaller than start date ({self.start_date})')
            self._end_date = value

    @property
    def priority(self):
        return self._priority

    @priority.setter
    def priority(self, value):
        if value not in PRIORITY_LEVELS:
            raise ValueError(f"Invalid priority level {value}. Accepted values are {PRIORITY_LEVELS}")
        self._priority = value