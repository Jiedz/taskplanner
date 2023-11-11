'''
This module describes a task and the relation between parent and children tasks.
'''

from datetime import date
from inspect import currentframe, getargvalues
from logging import warning

# %% Imports
from anytree import Node, RenderTree
from signalslot import Signal

# %% Task
PRIORITY_LEVELS = ["low", "medium", "high", "urgent"]


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
                 parent: object = None,
                 name: str = "A Task",
                 category: object = "No Category",
                 description: object = "",
                 priority: object = "medium",
                 start_date: date = date.today(),
                 end_date: date = None,
                 assignee: object = None) -> object:
        '''
        :param parent: py:class:'anytree.Node', optional
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
                         parent=parent)  # A task is a node of a tree
        # Get the argument names passed to the __init__ function
        argvalues = getargvalues(currentframe())
        attribute_names = argvalues.args
        attribute_names.remove('parent')
        for a in attribute_names:
            # Initialize the internal attributes to 'None'
            setattr(self, f"_{a}", None)
        # Set up signals for change of attribute value
        for a in attribute_names + ['completed']:
            setattr(self, f'{a}_changed', Signal())
        for a in attribute_names:
            # Set the corresponding properties to the passed argument values
            setattr(self, a, argvalues.locals[a])
        self._completed = False


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
            self.start_date_changed.emit()

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
            self.end_date_changed.emit()

    @property
    def priority(self):
        return self._priority

    @priority.setter
    def priority(self, value):
        if value not in PRIORITY_LEVELS:
            raise ValueError(f"Invalid priority level {value}. Accepted values are {PRIORITY_LEVELS}")
        self._priority = value
        self.priority_changed.emit()

    @property
    def completed(self):
        return self._completed

    @completed.setter
    def completed(self, value):
        if type(value) is not bool:
            raise TypeError('Attribute "completed" must be a boolean')
        self._completed = value
        self.completed_changed.emit()

    @property
    def is_top_level(self):
        '''
        It returns 'True' if and only if this task has no parent tasks.
        :return:
        '''
        return self.parent is None

    def set_parent_task(self, parent):
        '''
        Sets a new parent task.

        :param parent: py:class:'anytree.Node', optional
        :return:
        '''
        if parent == self:
            raise ValueError(f'Task {self.name} cannot be its own parent.')
        if self.parent is not None:
            children = list(self.parent.children)
            children.remove(self)
            self.parent.children = tuple(children)
        super().__init__(name=self.name,
                         parent=parent,
                         children=self.children)

    def add_children_tasks(self, *children):
        '''
        Adds children tasks as positional arguments.

        :param children: arguments of type :py:class:'anytree.Node'
            children tasks in the form of positional arguments
        :return:
        '''
        if self in children:
            raise ValueError(f'Cannot add task {self.name} to its own children.')
        all_children = tuple(list(self.children) + list(children))
        parent = self.parent
        if self.parent in all_children:
            warning(
                f"Task {self.name}: adding parent {self.parent.name} as child! New parent will now be the next ancestor.")
            parent = self.parent.parent
        super().__init__(name=self.name,
                         parent=parent,
                         children=all_children)

    def __str__(self):
        '''
        Returns a string representation of the tree, showing its nodes and
        dependencies.

        Returns
        -------
        s : str
            The string representation of the tree.

        '''
        s = ""
        for pre, fill, node in RenderTree(self):
            s += "%s%s" % (pre, node.name) + "\n"
        return s

    def _print(self):
        '''
        Prints a graphical representation of the tree, showing its nodes and
        dependencies.
        '''
        for pre, fill, node in RenderTree(self):
            print("%s%s" % (pre, node.name))

    def make_dict(self):
        '''
        Creates a dictionary corresponding to the object tree.

        Returns
        -------
        None.

        Notes
        -----
        The same remarks made in the documentation of :py:meth:`add_children`
        remain valid for this method.

        '''
        if self.children == None or len(self.children) == 0:
            attribute_names = ['name',
                               'category',
                               'description',
                               'priority',
                               'start_date',
                               'end_date',
                               'assignee']
            self.dict = {a: getattr(self, a) for a in attribute_names}
        else:
            for child in self.children:
                child.make_dict()
                self.dict[child.name] = child.dict

    def to_file(self, filename: str = None):
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
        access_mode = "w"
        if not hasattr(self, "file") and filename is None:
            '''
            directory = select_directory(
                title=f"Saving Task Tree {self.name} to .txt File: Select the Directory Where the .txt File is Created")
            name = self.name if "/" not in self.name else "task-tree"
            filename = os.path.join(os.path.abspath(directory), name)
            '''
            raise FileNotFoundError(f'File name is needed to save task {self.name} into a file.')
        elif hasattr(self, "file"):
            filename = self.filename
        self.filename = filename
        self.file = open(filename, access_mode, encoding="utf-8")
        if ".txt" not in filename:
            filename += ".txt"
        self.file.write(self.__str__())
        self.file.close()
