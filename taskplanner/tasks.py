'''
This module describes a task and the relation between parent and children tasks.
'''

from datetime import date
from inspect import currentframe, getargvalues
from logging import warning
import os
import textwrap

# %% Imports
from anytree import Node, RenderTree
from signalslot import Signal
from PyQt5.Qt import QColor

# %% Task
PRIORITY_LEVELS = ["low", "high", "urgent"]
PROGRESS_LEVELS = ['not started', 'in progress', 'completed']

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
                 category: object = None,
                 description: object = "",
                 priority: object = "low",
                 start_date: date = date.today(),
                 end_date: date = None,
                 assignee: object = None,
                 color: str = None) -> object:
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
        :param color: str, optional
            The color associated with the task.
        '''
        super().__init__(name=name,
                         parent=parent)  # A task is a node of a tree
        # Get the argument names passed to the __init__ function
        argvalues = getargvalues(currentframe())
        attribute_names = argvalues.args
        attribute_names.remove('parent')
        attribute_names.remove('self')
        for a in attribute_names:
            # Initialize the internal attributes to 'None'
            setattr(self, f"_{a}", None)
        # Set up signals for change of attribute value
        for a in attribute_names + ['progress',
                                    'children',
                                    'parent']:
            setattr(self, f'{a}_changed', Signal())
        for a in attribute_names:
            # Set the corresponding properties to the passed argument values
            setattr(self, a, argvalues.locals[a])
        self._progress = 'not started'

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        if hasattr(self, 'name_changed'):
            self.name_changed.emit()

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value
        self.description_changed.emit()

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        self._category = value
        self.category_changed.emit()

    @property
    def assignee(self):
        return self._assignee

    @assignee.setter
    def assignee(self, value):
        self._assignee = value
        self.assignee_changed.emit()

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
                    raise ValueError(f'Start date ({value}) is greater than end date ({self.end_date})')
            self._start_date = value

        if not self.is_top_level:
            if self.start_date < self.parent.start_date:
                self.parent.start_date = self.start_date
        self.start_date_changed.emit()

    @property
    def end_date(self):
        return self._end_date

    @end_date.setter
    def end_date(self, value):
        if value is None:
            self._end_date = self.start_date
        else:
            if 'datetime.date' not in str(type(value)):
                raise TypeError(f'Invalid end date type {type(value)}. Accepted types are ("datetime.date")')
            if self.end_date is not None:
                if value < self.start_date:
                    raise ValueError(f'end date ({value}) is smaller than start date ({self.start_date})')
            self._end_date = value

        if not self.is_top_level:
            if self.end_date > self.parent.end_date:
                self.parent.end_date = self.end_date
        self.end_date_changed.emit()

    @property
    def priority(self):
        return self._priority

    @priority.setter
    def priority(self, value):
        if value not in PRIORITY_LEVELS:
            raise ValueError(f'Invalid priority level {value}. Accepted values are {PRIORITY_LEVELS}')
        self._priority = value
        for subtask in self.children:
            subtask.priority = self.priority
        self.priority_changed.emit()


    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value):
        if value not in PROGRESS_LEVELS:
            raise ValueError(f"Invalid progress level '{value}'. Accepted values are {PROGRESS_LEVELS}")
        self._progress = value
        '''
        # If all tasks of the same level are completed, consider the parent task as completed
        if not self.is_top_level:
            if all([self.progress == 'completed'] + [task.progress == 'completed' for task in self.siblings]):
                self.parent.progress = 'completed'
        '''
        self.progress_changed.emit()

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        if value is not None:
            if not QColor.isValidColor(value):
                raise ValueError(f'Invalid color {value}.')
        self._color = value
        self.color_changed.emit()

    @property
    def is_top_level(self):
        """
        It returns 'True' if and only if this task has no parent tasks.
        :return:
        """
        return self.is_root

    @property
    def is_bottom_level(self):
        """
        It returns 'True' if and only if the task has no subtasks
        :return:
        """
        return self.is_leaf

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
        # Propagate to all children
        def signal_to_children(task):
            task.parent_changed.emit()
            for child in task.children:
                signal_to_children(child)
        signal_to_children(self)


    def add_children_tasks(self, *children):
        '''
        Adds children tasks as positional arguments.

        :param children: arguments of type :py:class:'anytree.Node'
            children tasks in the form of positional arguments
        :return:
        '''
        if self in children:
            raise ValueError(f'Cannot add task {self.name} to its own children.')
        for child in children:
            if child.start_date == child.end_date and child.start_date == date.today():
                child._start_date = self.start_date
                child.start_date_changed.emit()
                child._end_date = self.end_date
                child.end_date_changed.emit()
            if child.color is None:
                child.color = self.color
        all_children = tuple(list(self.children) + list(children))
        parent = self.parent
        if self.parent in all_children:
            warning(
                f"Task {self.name}: adding parent {self.parent.name} as child! New parent will now be the next ancestor.")
            parent = self.parent.parent
        # Store all attributes
        attribute_names = ['name',
                           'category',
                           'description',
                           'priority',
                           'start_date',
                           'end_date',
                           'assignee']
        attributes = {a: getattr(self, a) for a in attribute_names}
        for name in attribute_names:
            attributes[f'{name}_changed'] = getattr(self, f'{name}_changed')
        super().__init__(name=self.name,
                         parent=parent,
                         children=all_children)
        for name in list(attributes.keys()):
            setattr(self, name, attributes[name])
        # Signal a change of children
        self.children_changed.emit()
        # Propagate the signal to all ancestors
        for a in self.ancestors:
            a.children_changed.emit()

    def remove_children_tasks(self, *children):
        '''
        Removes children tasks, if existent, specified as positional arguments.

        :param children: arguments of type :py:class:'anytree.Node'
            children tasks in the form of positional arguments
        :return:
        '''
        if self in children:
            raise ValueError(f'Cannot remove task {self.name} from its own children.')
        existent_children = tuple(set(self.children) and set(children))
        for child in existent_children:
            child.set_parent_task(None)
        all_children = tuple(set(self.children) - set(children))
        parent = self.parent
        if self.parent in all_children:
            warning(
                f"Task {self.name}: adding parent {self.parent.name} as child! New parent will now be the next ancestor.")
            parent = self.parent.parent
        # Store all attributes
        attribute_names = ['name',
                           'category',
                           'description',
                           'priority',
                           'start_date',
                           'end_date',
                           'assignee']
        attributes = {a: getattr(self, a) for a in attribute_names}
        for name in attribute_names:
            attributes[f'{name}_changed'] = getattr(self, f'{name}_changed')
        super().__init__(name=self.name,
                         parent=parent,
                         children=all_children)
        for name in list(attributes.keys()):
            setattr(self, name, attributes[name])
        # Signal a change of children
        self.children_changed.emit()
        # Propagate the signal to all ancestors
        for a in self.ancestors:
            a.children_changed.emit()

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
                               'assignee',
                               'name']
            self.dict = {a: getattr(self, a) for a in attribute_names}
            for name in attribute_names:
                self.dict[f'{name}_changed'] = getattr(self, f'{name}_changed')

        else:
            for child in self.children:
                child.make_dict()
                self.dict[child.name] = child.dict

    def to_string(self,
                  string: str = '',
                  indent_pattern: str = '\t'):
        # Write all the data except subtasks first
        string += f'___TASK___\n'
        # name
        string += f'name: {self.name}\n'
        # category
        string += f'category: {self.category}\n'
        # description
        string += f'description: {self.description}\n'
        # priority
        string += f'priority: {self.priority}\n'
        # assignee
        string += f'assignee: {self.assignee}\n'
        # start date
        string += f'start date: {self.start_date.day}/{self.start_date.month}/{self.start_date.year}\n'
        # end date
        string += f'end date: {self.end_date.day}/{self.end_date.month}/{self.end_date.year}\n'
        # color
        string += f'color: {self.color}'
        # Write all subtasks
        for subtask in self.children:
            len_before = len(string)
            string = subtask.to_string(string=string+'\n',
                                       indent_pattern=indent_pattern)
            string = string.replace(string[len_before:],
                                    textwrap.indent(string[len_before:],
                                                    indent_pattern))
        return string

    @classmethod
    def from_string(cls,
                    string: str,
                    indent_pattern: str = '\t'):
        lines = string.split('\n')
        # Remove one indentation level from all task strings
        for i in range(len(lines)):
            line = lines[i]
            if indent_pattern in line:
                lines[i] = line[len(indent_pattern):]
        string = "\n".join(lines)
        # Divide all tasks into a list of task strings
        task_strings = string.split('___TASK___\n')[1:]
        # Consider the top-level task string
        main_task_string = task_strings[0]
        # Top-level task properties
        task = Task()
        # Read all the data except subtasks first
        lines = main_task_string.splitlines()
        attributes = ['name',
                      'category',
                      'description',
                      'priority',
                      'assignee',
                      'start date',
                      'end date',
                      'color']
        # Set description
        index = [i for i in range(len(lines)) if 'description: ' in lines[i]][0]
        description = lines[index].replace('description: ', '')
        line = lines[index+1]
        while 'priority: ' not in line:
            line = lines[index + 1]
            if 'priority: ' in line:
                pass
            else:
                description += '\n' + line
                # Delete all the lines that were misleadingly created by the description
                lines.remove(line)
        task.description = description
        # Set name, category, priority, assignee, color
        for i in [0, 1, 3, 4, 7]:
            attr_name = attributes[i].replace(' ', '_')
            value = lines[i].replace(attributes[i]+': ', '')
            if value == 'None':
                value = None
            setattr(task, attr_name, value)
        # Set start and end date
        task._end_date = None
        for i in [5, 6]:
            attr_name = attributes[i].replace(' ', '_')
            value = lines[i].replace(attributes[i]+': ', '')
            day, month, year = [int(v) for v in value.split('/')]
            setattr(task, attr_name, date(year, month, day))
        # Set subtasks
        task_strings = task_strings[1:]
        children_indices = [i for i in range(len(task_strings))
                            if task_strings[i][0] != indent_pattern]
        children_indices += [len(task_strings)]

        for i in range(len(children_indices) - 1):
            subtask_string = task_strings[children_indices[i]:children_indices[i+1]]
            if len(subtask_string) == 0:
                pass
            elif len(subtask_string) == 1:
                subtask_string = '___TASK___\n' + subtask_string[0]
            else:
                subtask_string = '___TASK___\n'.join(subtask_string)
                subtask_string = '___TASK___\n' + subtask_string

            task.add_children_tasks(Task.from_string(subtask_string))
        return task





    def to_file(self,
                filename: str = None,
                access_mode:str = 'r+',
                full_content: bool = True):
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
                raise ValueError(f'Task {self.name} has no file configured.')
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

        if not full_content:
            file.write(self.__str__())
            file.close()
        else:
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
        task = Task.from_string(file.read())
        task.filename = filename
        file.close()
        return task




def _signal_changed_property(task: Task,
                             signal: Signal,
                             property_name: str):
    valid_properties = [attr.replace('_changed', '') for attr in vars(Task()) if '_changed' in attr]
    if property_name not in valid_properties:
        raise ValueError(f'Invalid property "{property_name}". Valid properties are {tuple(valid_properties)}')
    '''
    if task.is_bottom_level:
        getattr(task, f'{property_name}_changed').connect(lambda **kwargs: signal.emit())
    else:
        for subtask in task.children:
            _signal_changed_property(task=subtask,
                                     signal=signal,
                                     property_name=property_name)
    '''
    getattr(task, f'{property_name}_changed').connect(lambda **kwargs: signal.emit())
    for subtask in task.descendants:
        getattr(subtask, f'{property_name}_changed').connect(lambda **kwargs: signal.emit())


