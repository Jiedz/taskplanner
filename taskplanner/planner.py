"""
This module defines a task planner.
"""
from taskplanner.tasks import Task, _signal_changed_property
from signalslot import Signal

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

    def remove_task(self,
                    *tasks: Task):
        for task in tasks:
            if task in self.tasks:
                self._tasks = self._tasks.remove(task)
                _signal_changed_property(task=task,
                                         signal=self.tasks_changed,
                                         property_name='children')
                self.tasks_changed.emit()

    def add_categories(self,
                      categories: str):
        for category in categories:
            if category not in self.categories:
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
            if assignee not in self.assignee:
                self._assignee += [assignee]
                self.assignee_changed.emit()

    def remove_assignees(self,
                         *assignees: str):
        for assignee in assignees:
            if assignee in self.assignee:
                self._assignee.remove(assignee)
                self.assignee_changed.emit()

    def _add_new_values(self,
                        task: Task,
                        signal: Signal,
                        property_name: str):
        if property_name not in ['category',
                                 'assignee']:
            raise ValueError(f'Invalid property "{property_name}". Valid properties are (category, assignee)')
        plural_form = f'{property_name[:-1]}ies' if property_name[-1]=='y' else f'{property_name}s'
        if task.is_bottom_level and getattr(task, property_name) not in getattr(self, plural_form):
            getattr(self, plural_form).append(getattr(task, property_name))
            getattr(task, f'{property_name}_changed').connect(
                lambda **kwargs: signal.emit())
        else:
            for subtask in task.children:
                self._add_new_values(task=subtask,
                                     signal=signal,
                                     property_name=property_name)

