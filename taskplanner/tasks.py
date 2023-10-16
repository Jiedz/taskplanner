'''
This module describes a task and the relation between parent and children tasks.
'''

#%% Imports
from anytree import Node
from datetime import datetime
#%% Task
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
                 parent:Node=None,
                 name:str="A Task",
                 category="No Category",
                 description="",
                 priority="medium",
                 due_date:list[int]=None,
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
        :param due_date: list[int], optional
            The task's due date, as a list or tuple of (year, month, day)
        :param assignee: str, optional
            The name of the person who is assigned the task.
        '''
        if due_date is None:
            due_date = datetime.now()
            self.due_date = (due_date.year,
                        due_date.month,
                        due_date.day)
        else:
            try:
                assert len(due_date) == 3, f"Invalid due date {due_date}. Due date needs to be a list or a tuple of (year, month, day)."
            except:
                raise ValueError(f"Invalid due date {due_date}. Due date needs to be a list or a tuple of (year, month, day).")
        self.name, self.description, self.assignee = \
        name, description, assignee
        self._priority = None
        self.priority = priority
        raise NotImplementedError("Change due date into start date.)

    @property
    def start_date(self):
        return self._start_date

    @start_date.setter
    def start_date(self, value):
        try:
            assert len(value) == 3, f"Invalid start date {value}. Start date needs to be a list or a tuple of (year, month, day)."
        except:
            raise ValueError(
                f"Invalid start date {value}. Start date needs to be a list or a tuple of (year, month, day)."
        self._start_date = value\

    @property
    def priority(self):
        return self._priority
    @priority.setter
    def priority(self, value):
        assert value in PRIORITY_LEVELS, \
            f"Invalid priority level {value}. Accepted values are {PRIORITY_LEVELS}"
        self._priority = value
