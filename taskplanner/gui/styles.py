"""
This module define the styles to be used by the task-related widgets.
"""
import ast
import os
from signalslot import Signal

from taskplanner.gui.utilities import get_primary_screen
from PyQt5.Qt import QSize

COLOR_PALETTES = {
    'dark material':
        {
            'background 1': '#232426',
            'background 2': '#3a3c3f',
            'text': '#ededecff',
            'text - light': '#bcbec4',
            'text - highlight': '#bcbec4', #'#4273bc',
            'border': '#3a3c3f',
        },
}

FONTS = {'light':
    {
        'family': 'Sans Serif',
        'size - title 1': '20pt',
        'size - title 2': '18pt',
        'size - text': '12pt',
        'size - text - small': '10pt'
    },
}

from taskplanner.gui.utilities import set_style, get_primary_screen
SCREEN = get_primary_screen()
SCREEN_WIDTH = SCREEN.width
SCREEN_HEIGHT = SCREEN.height

ICON_SIZES = {'regular': QSize(int(SCREEN_WIDTH/70), int(SCREEN_WIDTH/70)),
              'small': QSize(int(SCREEN_WIDTH/100), int(SCREEN_WIDTH/100))}

class TaskWidgetStyle:
    def __init__(self,
                 color_palette: dict = COLOR_PALETTES['dark material'],
                 font: dict = FONTS['light'],
                 style_name: str = 'dark material'):
        self.style_name = style_name
        self._font = font
        self._color_palette = color_palette
        self.font_changed = Signal()
        self.color_palette_changed = Signal()
        # Locate icon path
        self.icon_path = os.path.join(*os.path.split(__file__)[:-1])
        self.icon_path = os.path.join(self.icon_path,
                                      'styles/icons',
                                      self.style_name.replace(" ", "-"))
        if not os.path.exists(self.icon_path):
            self.icon_path = os.path.join(self.icon_path,
                                         'styles/icons/dark-material')
        # Get screen size
        screen_size = get_primary_screen()
        # Define style sheets
        self.stylesheets = {
            'standard view':
                {
                    'main':
                        '''
                        QWidget
                        {
                            background-color:%s;
                            border:2px solid %s;
                            border-radius:10px;
                            font-family:%s;
                            color:%s;
                        }
                        ''' % (self.color_palette['background 1'],
                               self.color_palette['border'],
                               self.font['family'],
                               self.color_palette['text']),
                    'scrollarea':
                    '''
                        QScrollArea
                        {
                            background-color:%s;
                            border:2px solid %s;
                            border-radius:10px;
                        }
                        QScrollBar:vertical
                        {
                            background-color:%s;
                            border:2px solid %s;
                            border-radius:10px;
                        }
                        QScrollBar:horizontal
                        {
                            background-color:%s;
                            border:2px solid %s;
                            border-radius:10px;
                        }
                        QScrollBar:handle:vertical
                        {
                            background-color:%s;
                            border:2px solid %s;
                            border-radius:10px;
                        }
                        QScrollBar:handle:horizontal
                        {
                            background-color:%s;
                            border:2px solid %s;
                            border-radius:10px;
                        }
                        QScrollBar:handle
                        {
                            background-color:%s;
                            border:2px solid %s;
                            border-radius:10px;
                        }
                        QScrollBar::groove 
                        {
                            background-color:%s;
                            border:2px solid %s;
                            border-radius:10px;
                        }
                    ''' % (self.color_palette['background 1'],
                           self.color_palette['border'],
                           self.color_palette['background 1'],
                           self.color_palette['border'],
                           self.color_palette['background 1'],
                           self.color_palette['border'],
                           self.color_palette['background 1'],
                           self.color_palette['border'],
                           self.color_palette['background 1'],
                           self.color_palette['border'],
                           self.color_palette['background 1'],
                           self.color_palette['border'],
                           self.color_palette['background 1'],
                           self.color_palette['border'],
                           ),
                    'path_widget':
                        {
                            'main':
                            '''
                            QPushButton
                            {
                                color:%s;
                                font-size:%s;
                                border:2px solid %s;
                            }
                            QPushButton:hover
                            {
                                text-decoration:underline;
                            }
                            ''' % (self.color_palette['text - highlight'],
                                   self.font['size - text - small'],
                                   self.color_palette['border']),
                            'icon_label':
                                '''
                                QLabel
                                {
                                    border:None;   
                                }
                                '''

                        },
                    'title_widget':
                        {
                            'textedit':
                            '''
                            QTextEdit
                            {
                                background-color:%s;
                                border:None;
                                color:%s;
                                font-size:%s
                            }
                            ''' % (self.color_palette['background 2'],
                                   self.color_palette['text'],
                                   self.font['size - title 2'])
                        },
                    'download_pushbutton':
                        '''
                        QPushButton
                        {
                            border-radius:%spx;
                            border:0px solid %s;
                            icon-size:%spx;
                        }
                        QPushButton:hover
                        {
                            background-color:%s;
                        }
                        ''' % (int(screen_size.width / 220),
                               self.color_palette['border'],
                               ICON_SIZES['regular'].width(),
                               self.color_palette['border']),
                    'color_widget':
                        {
                            'label':
                                '''
                                QLabel
                                {
                                    border:None;
                                    color:%s;
                                    font-size:%s;
                                }
                                ''' % (self.color_palette['text - light'],
                                       self.font['size - text']),
                            'color_pushbutton':
                                '''
                                QPushButton
                                {
                                }
                                ''',
                            'color_dialog':
                                '''
                                QColorDialog
                                {
                                    
                                }
                                ''',
                                'color_change_dialog':
                                '''
                                QWidget
                                {
                                    background-color:%s;
                                    font-size:%s;
                                    font-family:%s;
                                    color:%s;
                                }
                                QPushButton
                                {
                                    background-color:%s;
                                    font-size:%s;
                                }
                                ''' % (self.color_palette['background 1'],
                                       self.font['size - text'],
                                       self.font['family'],
                                       self.color_palette['text - light'],
                                       self.color_palette['background 2'],
                                       self.font['size - text']),
                        },
                    'progress_widget':
                        {
                            'label':
                                '''
                                QLabel
                                {
                                    border:None;
                                    color:%s;
                                    font-size:%s;
                                }
                                ''' % (self.color_palette['text - light'],
                                       self.font['size - text']),
                            'combobox':
                                '''
                                QComboBox
                                {
                                    border:2px solid %s;
                                    color:%s;
                                    font-size:%s;
                                    icon-size:%spx;
                                }
                                QComboBox:item:selected
                                {
                                    background-color:%s;
                                }
                                ''' % (self.color_palette['border'],
                                       self.color_palette['text'],
                                       self.font['size - text - small'],
                                       ICON_SIZES['small'].width(),
                                       self.color_palette['background 2']),
                        },
                    'category_widget':
                        {
                            'label':
                                '''
                                QLabel
                                {
                                    border:None;
                                    color:%s;
                                    font-size:%s;
                                }
                                ''' % (self.color_palette['text - light'],
                                       self.font['size - text']),
                            'combobox':
                                '''
                                QComboBox
                                {
                                    border:2px solid %s;
                                    color:%s;
                                    font-size:%s;
                                    icon-size:%spx;
                                }
                                QComboBox:item:selected
                                {
                                    background-color:%s;
                                }
                                ''' % (self.color_palette['border'],
                                       self.color_palette['text'],
                                       self.font['size - text - small'],
                                       ICON_SIZES['small'].width(),
                                       self.color_palette['background 2']),
                            'add_pushbutton':
                                '''
                                QPushButton
                                {
                                    border-radius:%spx;
                                    border:2px solid %s;
                                    icon-size:%spx;
                                }
                                QPushButton:hover
                                {
                                    background-color:%s;
                                }
                                ''' % (int(screen_size.width / 220),
                                       self.color_palette['border'],
                                       ICON_SIZES['small'].width(),
                                       self.color_palette['border']),
                        },
                    'assignee_widget':
                        {
                            'label':
                                '''
                                QLabel
                                {
                                    border:None;
                                    color:%s;
                                    font-size:%s;
                                }
                                ''' % (self.color_palette['text - light'],
                                       self.font['size - text']),
                            'combobox':
                                '''
                                QComboBox
                                {
                                    border:2px solid %s;
                                    color:%s;
                                    font-size:%s;
                                    icon-size:%spx;
                                }
                                QComboBox:item:selected
                                {
                                    background-color:%s;
                                }
                                ''' % (self.color_palette['border'],
                                       self.color_palette['text'],
                                       self.font['size - text - small'],
                                       ICON_SIZES['small'].width(),
                                       self.color_palette['background 2']),
                            'add_pushbutton':
                                '''
                                                QPushButton
                                                {
                                                    border-radius:%spx;
                                                    border:2px solid %s;
                                                    icon-size:%spx;
                                                }
                                                QPushButton:hover
                                                {
                                                    background-color:%s;
                                                }
                                                ''' % (int(screen_size.width / 220),
                                                       self.color_palette['border'],
                                                       ICON_SIZES['small'].width(),
                                                       self.color_palette['border']),
                        },
                    'priority_widget':
                        {
                            'label':
                                '''
                                QLabel
                                {
                                    border:None;
                                    color:%s;
                                    font-size:%s;
                                }
                                ''' % (self.color_palette['text - light'],
                                       self.font['size - text']),
                            'combobox':
                                '''
                                QComboBox
                                {
                                    border:2px solid %s;
                                    color:%s;
                                    font-size:%s;
                                    icon-size:%spx;
                                }
                                QComboBox:item:selected
                                {
                                    background-color:%s;
                                }
                                ''' % (self.color_palette['border'],
                                       self.color_palette['text'],
                                       self.font['size - text - small'],
                                       ICON_SIZES['small'].width(),
                                       self.color_palette['background 2']),
                        },
                    'start_date_widget':
                        {
                            'label':
                                '''
                                QLabel
                                {
                                    border:None;
                                    color:%s;
                                    font-size:%s;
                                }
                                ''' % (self.color_palette['text - light'],
                                       self.font['size - text']),
                            'pushbutton':
                                '''
                                QPushButton
                                {
                                    color:%s;
                                    font-size:%s;
                                    border:0px solid %s;
                                }
                                QPushButton:hover
                                {
                                    text-decoration:underline;
                                }
                                ''' % (self.color_palette['text - highlight'],
                                   self.font['size - text'],
                                   self.color_palette['border']),
                            'calendar_widget':
                                '''
                                QCalendarWidget QWidget
                                {
                                    background-color:%s;
                                }
                                ''' % (self.color_palette['background 2']),
                        },
                    'end_date_widget':
                        {
                            'label':
                                '''
                                QLabel
                                {
                                    border:None;
                                    color:%s;
                                    font-size:%s;
                                }
                                ''' % (self.color_palette['text - light'],
                                       self.font['size - text']),
                            'pushbutton':
                                '''
                                QPushButton
                                {
                                    color:%s;
                                    font-size:%s;
                                    border:0px solid %s;
                                }
                                QPushButton:hover
                                {
                                    text-decoration:underline;
                                }
                                ''' % (self.color_palette['text - highlight'],
                                       self.font['size - text'],
                                       self.color_palette['border']),
                            'calendar_widget':
                                '''
                                QCalendarWidget QWidget
                                {
                                    background-color:%s;
                                }
                                ''' % (self.color_palette['background 2']),
                        },
                    'link_dates_widget':
                        {
                            'main':
                                '''
                                QFrame
                                {
                                    border:None;
                                }
                                ''',
                            'label':
                                '''
                                QLabel
                                {
                                    border:None;
                                    color:%s;
                                    font-size:%s;
                                }
                                ''' % (self.color_palette['text - light'],
                                       self.font['size - text']),
                            'pushbutton':
                                '''
                                QPushButton
                                {
                                    background-color:%s;
                                    border:3px solid %s;
                                    border-radius:%spx;
                                }
                                QPushButton:hover
                                {
                                    background-color:%s;
                                }
                                ''' % (self.color_palette['background 1'],
                                       self.color_palette['text - highlight'],
                                       15,
                                       self.color_palette['background 2']),
                        },
                    'description_widget':
                        {
                            'main':
                            '''
                            QFrame
                            {
                                border:None;
                            }
                            ''',
                            'combobox':
                                '''
                                QComboBox
                                {
                                    border:1px solid %s;
                                    color:%s;
                                    font-size:%s;
                                }
                                QComboBox:item:selected
                                {
                                    background-color:%s;
                                }
                                ''' % (self.color_palette['border'],
                                       self.color_palette['text'],
                                       self.font['size - text - small'],
                                       self.color_palette['background 2']),
                            'textbrowser':
                                '''
                                QTextBrowser
                                {
                                    /* background-color:%s; */
                                    font-size:%s;
                                    border:2px solid %s;
                                    border-radius:%s;
                                }
                                ''' % (self.color_palette['background 2'],
                                               self.font['size - text'],
                                               self.color_palette['border'],
                                               int(SCREEN_WIDTH / 220)),
                            'label':
                                '''
                                QLabel
                                {
                                    border:None;
                                    font-size:%s;
                                    color:%s;
                                }
                                ''' % (self.font['size - text - small'],
                                       self.color_palette['text - light'])
                        },
                    'subtask_list_widget':
                        {
                            'icon_label':
                                '''
                                QLabel
                                {
                                    border:None;   
                                }
                                ''',
                            'new_textedit':
                                '''
                                QTextEdit
                                {
                                    font-size:%s;
                                }
                                ''' % (self.font['size - text - small']),
                            'upload_pushbutton':
                                '''
                                QPushButton
                                {
                                    border-radius:%spx;
                                    border:0px solid %s;
                                    icon-size:%spx;
                                }
                                QPushButton:hover
                                {
                                    background-color:%s;
                                }
                                ''' % (int(screen_size.width / 220),
                                       self.color_palette['border'],
                                       ICON_SIZES['regular'].width(),
                                       self.color_palette['border']),
                        },
                },
            'simple view':
                {
                    'task_line_widget':
                        {
                            'name_pushbutton':
                                '''
                                QPushButton
                                {
                                    color:%s;
                                    font-size:%s;
                                    border:0px solid %s;
                                }
                                QPushButton:hover
                                {
                                    text-decoration:underline;
                                }
                                ''' % (self.color_palette['text - highlight'],
                                       self.font['size - text'],
                                       self.color_palette['border']),
                            'priority_label':
                                '''
                                QLabel
                                {
                                    border:None;
                                    color:%s;
                                    font-size:%s;
                                }
                                ''' % (self.color_palette['text - light'],
                                       self.font['size - text']),
                            'progress_label':
                                '''
                                QLabel
                                {
                                    border:None;
                                    color:%s;
                                    font-size:%s;
                                }
                                ''' % (self.color_palette['text - light'],
                                       self.font['size - text']),
                            'remove_pushbutton':
                                '''
                                QPushButton
                                {
                                    icon-size:%spx;
                                    border:None;
                                }
                                QPushButton:hover
                                {
                                    background-color:%s;
                                }
                                ''' % (ICON_SIZES['small'].width(),
                                       self.color_palette['background 2']),
                            'remove_dialog':
                                '''
                                QWidget
                                {
                                    background-color:%s;
                                    font-size:%s;
                                    font-family:%s;
                                    color:%s;
                                }
                                QPushButton
                                {
                                    background-color:%s;
                                    font-size:%s;
                                }
                                ''' % (self.color_palette['background 1'],
                                       self.font['size - text'],
                                       self.font['family'],
                                       self.color_palette['text - light'],
                                       self.color_palette['background 2'],
                                       self.font['size - text']),
                            'expand_pushbutton':
                                '''
                                QPushButton
                                {
                                    icon-size:%spx;
                                    border:None
                                }
                                QPushButton:hover
                                {
                                    background-color:%s;
                                }
                                ''' % (ICON_SIZES['small'].width(),
                                       self.color_palette['background 2']),
                            'start_date_widget':
                            {
                                'label':
                                    '''
                                    QLabel
                                    {
                                        border:None;
                                        color:%s;
                                        font-size:%s;
                                    }
                                    ''' % (self.color_palette['text - light'],
                                           self.font['size - text']),
                                'pushbutton':
                                    '''
                                    QPushButton
                                    {
                                        color:%s;
                                        font-size:%s;
                                        border:None;
                                    }
                                    QPushButton:hover
                                    {
                                        text-decoration:underline;
                                    }
                                    ''' % (self.color_palette['text - highlight'],
                                       self.font['size - text'],
                                       ),
                                'calendar_widget':
                                    '''
                                    QCalendarWidget QWidget
                                    {
                                        background-color:%s;
                                    }
                                    ''' % (self.color_palette['background 2']),
                            },
                            'end_date_widget':
                                {
                                    'label':
                                        '''
                                        QLabel
                                        {
                                            border:None;
                                            color:%s;
                                            font-size:%s;
                                        }
                                        ''' % (self.color_palette['text - light'],
                                               self.font['size - text']),
                                    'pushbutton':
                                        '''
                                        QPushButton
                                        {
                                            color:%s;
                                            font-size:%s;
                                            border:None;
                                        }
                                        QPushButton:hover
                                        {
                                            text-decoration:underline;
                                        }
                                        ''' % (self.color_palette['text - highlight'],
                                               self.font['size - text'],
                                               ),
                                    'calendar_widget':
                                        '''
                                        QCalendarWidget QWidget
                                        {
                                            background-color:%s;
                                        }
                                        ''' % (self.color_palette['background 2']),
                                },
                        }
                }
        }

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, value):
        if set(value.keys()) != set(FONTS['light'].keys()):
            raise ValueError(f'Invalid font {value}. A valid font must contain the keys {list(FONTS["light"].keys())}')
        self.__init__(color_palette=self.color_palette,
                      font=value)

    @property
    def color_palette(self):
        return self._color_palette

    @color_palette.setter
    def color_palette(self,value):
        if set(value.keys()) != set(COLOR_PALETTES['light'].keys()):
            raise ValueError(f'Invalid font {value}. A valid font must contain the keys '
                             f'{list(COLOR_PALETTES["light"].keys())}')
        self.__init__(color_palette=value,
                      font=self.font)


class PlannerWidgetStyle:
    def __init__(self,
                 color_palette: dict = COLOR_PALETTES['dark material'],
                 font: dict = FONTS['light'],
                 style_name: str = 'dark material'):
        self.style_name = style_name
        self._font = font
        self._color_palette = color_palette
        self.font_changed = Signal()
        self.color_palette_changed = Signal()
        # Locate icon path
        self.icon_path = os.path.join(*os.path.split(__file__)[:-1])
        self.icon_path = os.path.join(self.icon_path,
                                      'styles/icons',
                                      self.style_name.replace(" ", "-"))
        if not os.path.exists(self.icon_path):
            self.icon_path = os.path.join(self.icon_path,
                                      'styles/icons/dark-material')
        # Get screen size
        screen_size = get_primary_screen()
        # Define style sheets
        self.stylesheets = \
            {
                'main':
                    '''
                    QWidget
                    {
                        background-color:%s;
                        border:2px solid %s;
                        border-radius:10px;
                        font-family:%s;
                        color:%s;
                    }
                    QTabWidget
                    {
                        border:None;
                    }
                    QTabWidget:tab-bar
                    {
                        width:%spx;
                        height:%spx;
                    }
                    QTabBar:tab
                    {
                        background-color:%s;
                        color:%s;
                        font-size:%s;
                    }
                    QTabBar:tab:hover
                    {
                        background-color:%s;
                    }
                    ''' % (self.color_palette['background 1'],
                           self.color_palette['border'],
                           self.font['family'],
                           self.color_palette['text'],
                           int(SCREEN_WIDTH*0.3),
                           int(1.5*int(self.font['size - text'].split('p')[0])),
                           self.color_palette['background 2'],
                           self.color_palette['text'],
                           self.font['size - text'],
                           self.color_palette['background 1']),
                'planner_tab':
                    {
                        'main':
                            '''
                            QWidget
                            {
                                border:
                            }
                            ''',
                        'task_list_widget':
                            {
                                'main':
                                    {
                                        '''
                                        QWidget
                                        {
                                            border:2px solid %s;
                                        }
                                        ''' % self.color_palette['border']
                                    }
                            },
                        'task_list_scrollarea':
                            '''
                            QScrollArea
                            {
                                background-color:%s;
                                border:2px solid %s;
                                border-radius:10px;
                            }
                            QScrollBar:vertical
                            {
                                background-color:%s;
                                border:2px solid %s;
                                border-radius:10px;
                            }
                            QScrollBar:horizontal
                            {
                                background-color:%s;
                                border:2px solid %s;
                                border-radius:10px;
                            }
                            QScrollBar:handle:vertical
                            {
                                background-color:%s;
                                border:2px solid %s;
                                border-radius:10px;
                            }
                            QScrollBar:handle:horizontal
                            {
                                background-color:%s;
                                border:2px solid %s;
                                border-radius:10px;
                            }
                            QScrollBar:handle
                            {
                                background-color:%s;
                                border:2px solid %s;
                                border-radius:10px;
                            }
                            QScrollBar::groove 
                            {
                                background-color:%s;
                                border:2px solid %s;
                                border-radius:10px;
                            }
                            '''
                            % (self.color_palette['background 1'],
                           self.color_palette['border'],
                           self.color_palette['background 1'],
                           self.color_palette['border'],
                           self.color_palette['background 1'],
                           self.color_palette['border'],
                           self.color_palette['background 1'],
                           self.color_palette['border'],
                           self.color_palette['background 1'],
                           self.color_palette['border'],
                           self.color_palette['background 1'],
                           self.color_palette['border'],
                           self.color_palette['background 1'],
                           self.color_palette['border'],
                           ),
                        'calendar_scrollarea':
                            '''
                                QWidget
                                {
                                    border:None;
                                    margin-top:0px;
                                }
                            ''',
                        'calendar_widget':
                            {
                                'main':
                                    '''
                                    QWidget
                                    {
                                        border:None;
                                    }
                                    ''',
                                'month_widget':
                                    {
                                        'main':
                                            '''
                                            QFrame
                                            {
                                                background-color:None;
                                                border:0px solid %s;
                                                padding:0px;
                                            }
                                            ''' % (self.color_palette['border']),
                                        'label':
                                            '''
                                            QLabel
                                            {   
                                                border:None;
                                                color:%s;
                                                font-size:%s;
                                                background-color:%s;
                                            }
                                            ''' % (
                                                   self.color_palette['text - light'],
                                                   self.font['size - title 2'],
                                                   self.color_palette['background 2']),
                                    },
                                'week_widget':
                                    {
                                        'main':
                                            '''
                                            QWidget
                                            {                      
                                                background-color:None;
                                                border:0px solid %s;
                                                padding:0px;
                                            }
                                            ''' % (self.color_palette['border']),
                                        'label':
                                            '''
                                            QLabel
                                            {   
                                                border:0px solid %s;
                                                color:%s;
                                                font-size:%s;
                                            }
                                            ''' % (self.color_palette['border'],
                                                   self.color_palette['text - light'],
                                                   self.font['size - text']),
                                    },
                                'day_widget':
                                    {
                                        'main':
                                            '''
                                            QWidget
                                            {
                                                background-color:None;
                                                border:0.5px solid %s;
                                            }
                                            ''' % (self.color_palette['border']),
                                        'label':
                                            '''
                                            QLabel
                                            {   
                                                border:None;
                                                color:%s;
                                                font-size:%s;
                                            }
                                            ''' % (
                                                   self.color_palette['text - light'],
                                                   self.font['size - text - small']),
                                    },
                                'timeline':
                                    {
                                        'main':
                                            '''
                                            QWidget
                                            {
                                                border:2px solid %s;
                                            }
                                            ''' % (self.color_palette['border']),
                                    }
                            },
                        'new_task_textedit':
                            '''
                            QTextEdit
                            {
                                font-size:%s;
                                border:2px solid %s;
                            }
                            ''' % (self.font['size - text'],
                                   self.color_palette['border']),
                        'upload_task_pushbutton':
                            '''
                            QPushButton
                            {
                                border-radius:%spx;
                                border:0px solid %s;
                                icon-size:%spx;
                            }
                            QPushButton:hover
                            {
                                background-color:%s;
                            }
                            ''' % (int(screen_size.width / 220),
                                   self.color_palette['border'],
                                   ICON_SIZES['regular'].width(),
                                   self.color_palette['border']),
                        'view_selector':
                            {
                                'main':
                                    '''
                                    QWidget
                                    {
                                        border:None;
                                    }
                                    ''',
                                'label':
                                '''
                                QLabel
                                {
                                    border:None;
                                    color:%s;
                                    font-size:%s;
                                }
                                ''' % (self.color_palette['text - light'],
                                       self.font['size - text']),
                                'combobox':
                                    '''
                                    QComboBox
                                    {
                                        border:2px solid %s;
                                        color:%s;
                                        font-size:%s;
                                        icon-size:%spx;
                                    }
                                    QComboBox:item:selected
                                    {
                                        background-color:%s;
                                    }
                                    ''' % (self.color_palette['border'],
                                           self.color_palette['text'],
                                           self.font['size - text - small'],
                                           ICON_SIZES['small'].width(),
                                           self.color_palette['background 2']),
                            },
                        'start_date_widget':
                            {
                                'label':
                                    '''
                                    QLabel
                                    {
                                        border:None;
                                        color:%s;
                                        font-size:%s;
                                    }
                                    ''' % (self.color_palette['text - light'],
                                           self.font['size - text']),
                                'pushbutton':
                                    '''
                                    QPushButton
                                    {
                                        color:%s;
                                        font-size:%s;
                                        border:None;
                                    }
                                    QPushButton:hover
                                    {
                                        text-decoration:underline;
                                    }
                                    ''' % (self.color_palette['text - highlight'],
                                           self.font['size - text'],
                                           ),
                                'calendar_widget':
                                    '''
                                    QCalendarWidget QWidget
                                    {
                                        background-color:%s;
                                    }
                                    ''' % (self.color_palette['background 2']),
                            },
                        'end_date_widget':
                            {
                                'label':
                                    '''
                                    QLabel
                                    {
                                        border:None;
                                        color:%s;
                                        font-size:%s;
                                    }
                                    ''' % (self.color_palette['text - light'],
                                           self.font['size - text']),
                                'pushbutton':
                                    '''
                                    QPushButton
                                    {
                                        color:%s;
                                        font-size:%s;
                                        border:None;
                                    }
                                    QPushButton:hover
                                    {
                                        text-decoration:underline;
                                    }
                                    ''' % (self.color_palette['text - highlight'],
                                           self.font['size - text'],
                                           ),
                                'calendar_widget':
                                    '''
                                    QCalendarWidget QWidget
                                    {
                                        background-color:%s;
                                    }
                                    ''' % (self.color_palette['background 2']),
                            },
                    },
                'task_buckets_tab':
                    {
                        'property_widget':
                            {
                                'label':
                                    '''
                                    QLabel
                                    {
                                        font-size:%s;
                                        color:%s;
                                        border:None;
                                    }
                                    ''' % (self.font['size - text'],
                                           self.color_palette['text - light']),
                                'combobox':
                                    '''
                                    QComboBox
                                    {
                                        font-size:%s;
                                        color:%s;
                                        border:1px solid %s;
                                    }
                                    ''' % (self.font['size - text'],
                                           self.color_palette['text'],
                                           self.color_palette['border']),
                            },
                        'bucket_list_scrollarea':
                            '''
                            QScrollArea
                            {
                                border:None;
                            }
                            ''',
                        'bucket_list_widget':
                            {
                                'main':
                                    '''
                                    QFrame
                                    {
                                        border:None;
                                    }
                                    ''',
                                'bucket_widget':
                                    {
                                        'main':
                                            '''
                                            QFrame
                                            {
                                                border:3px solid %s;
                                            }
                                            ''' % self.color_palette['border'],
                                        'label':
                                            '''
                                            QLabel
                                            {
                                                font-size:%s;
                                                color:%s;
                                                border:None;
                                            }
                                            ''' % (self.font['size - title 2'],
                                                   self.color_palette['text - light']),
                                        'task_list_widget':
                                            {
                                                'main':
                                                    '''
                                                    QFrame
                                                    {
                                                        border:None;
                                                    }
                                                    '''
                                            },
                                        'task_list_scrollarea':
                                            {
                                                'main':
                                                    '''
                                                    QFrame
                                                    {
                                                        border:None;
                                                    }
                                                    '''
                                            },
                                    }
                            },
                        'stats_widget':
                            {
                                'main':
                                    '''
                                    QFrame
                                    {
                                        border:*3px solid %s;
                                    }
                                    ''' % self.color_palette['border'],
                                'title_label':
                                    '''
                                    QLabel
                                    {
                                        border:None;
                                        font-size:%s;
                                        color:%s;
                                    }
                                    ''' % (self.font['size - title 2'],
                                           self.color_palette['text - light']),
                                'graph_widget':
                                    {
                                        'main':
                                            '''
                                            QFrame
                                            {
                                                border:2px solid %s;
                                            }
                                            ''' % self.color_palette['border'],
                                        'title_label':
                                            '''
                                            QLabel
                                            {
                                                border:None;
                                                font-size:%s;
                                                color:%s;
                                            }
                                            ''' % (self.font['size - text'],
                                                   self.color_palette['text'])
                                    }
                            }
                    },
                'settings_tab':
                    {
                        'main':
                            '''
                            QWidget
                            {
                            }
                            ''',
                        'graphics_scrollarea':
                            '''
                            QScrollArea
                            {
                                border:None;
                            }
                            ''',
                        'graphics_settings_widget':
                            {
                                'main':
                                    '''
                                    QFrame
                                    {
                                        border:3px solid %s;
                                    }
                                    ''' % self.color_palette['border'],
                                'title_label':
                                    '''
                                    QLabel
                                    {
                                        font-size:%s;
                                        color:%s;
                                        border:None;
                                    }
                                    ''' % (self.font['size - title 2'],
                                           self.color_palette['text - light']),
                                'apply_pushbutton':
                                    '''
                                    QPushButton
                                    {
                                        background-color:%s;
                                        font-size:%s;
                                        color:%s;
                                        border:1px solid %s;
                                    }
                                    QPushButton:hover
                                    {
                                        background-color:%s;
                                    }
                                    ''' % (self.color_palette['border'],
                                           self.font['size - text'],
                                           self.color_palette['text'],
                                           self.color_palette['border'],
                                           self.color_palette['background 2']),
                                'color_palette_selection_widget':
                                    {
                                        'main':
                                            '''
                                            QFrame
                                            {
                                                border:1px solid %s;
                                            }
                                            ''' % self.color_palette['border'],
                                        'title_label':
                                            '''
                                            QLabel
                                            {
                                                font-size:%s;
                                                color:%s;
                                                border:None;
                                            }
                                            ''' % (self.font['size - text'],
                                                   self.color_palette['text - light']),
                                        'color_selector':
                                            {
                                                'main':
                                                    '''
                                                    QFrame
                                                    {
                                                        border:None;
                                                    }
                                                    ''',
                                                'label':
                                                    '''
                                                    QLabel
                                                    {
                                                        font-size:%s;
                                                        color:%s;
                                                        border:None;
                                                    }
                                                    ''' % (self.font['size - text - small'],
                                                           self.color_palette['text']),
                                                'color_dialog':
                                                    '''
                                                    QColorDialog
                                                    {
                                                        background-color
                                                    }
                                                    ''',
                                            }
                                    },
                                'font_selection_widget':
                                    {
                                        'main':
                                            '''
                                            QFrame
                                            {
                                                border:1px solid %s;
                                            }
                                            ''' % self.color_palette['border'],
                                        'title_label':
                                            '''
                                            QLabel
                                            {
                                                font-size:%s;
                                                color:%s;
                                                border:None;
                                            }
                                            ''' % (self.font['size - text'],
                                                   self.color_palette['text - light']),
                                        'fontsize_selector':
                                            {
                                                'main':
                                                    '''
                                                    QFrame
                                                    {
                                                        border:None;
                                                    }
                                                    ''',
                                                'label':
                                                    '''
                                                    QLabel
                                                    {
                                                        font-size:%s;
                                                        color:%s;
                                                        border:None;
                                                    }
                                                    ''' % (self.font['size - text - small'],
                                                           self.color_palette['text']),
                                                'slider':
                                                    '''
                                                    QSlider
                                                    {
                                                        border:None;
                                                    }
                                                    QSlider::handle:horizontal
                                                    {
                                                        background-color:%s;
                                                        border:1px solid %s;
                                                    }
                                                    QSlider::handle:horizontal:hover
                                                    {
                                                        background-color:%s;
                                                    }
                                                    ''' % (
                                                        self.color_palette['background 2'],
                                                        self.color_palette['border'],
                                                        self.color_palette['text - highlight'],
                                                    ),
                                            },
                                        'font_family_selector':
                                            {
                                                'main':
                                                    '''
                                                    QFrame
                                                    {
                                                        border:None;
                                                    }
                                                    ''',
                                                'label':
                                                    '''
                                                    QLabel
                                                    {
                                                        font-size:%s;
                                                        color:%s;
                                                        border:None;
                                                    }
                                                    ''' % (self.font['size - text - small'],
                                                           self.color_palette['text']),
                                                'combobox':
                                                    '''
                                                    QCombobox
                                                    {
                                                        font-size:%s;
                                                        color:%s;
                                                        border:None;
                                                    }
                                                    QComboBox:item:selected
                                                    {
                                                        background-color:%s;
                                                    }
                                                    ''' % (
                                                        self.font['size - text - small'],
                                                        self.color_palette['text'],
                                                        self.color_palette['background 2']),
                                            }
                                    },
                            }
                    }
            }

    def to_string(self):
        string = '___PLANNER WIDGET STYLE___'
        # Color Palette
        string += f'\ncolor palette: {self.color_palette}'
        # Font
        string += f'\nfont: {self.font}'
        return string

    import ast

    @classmethod
    def from_string(cls,
                    string: str):
        s = ''.join(string.split('___PLANNER WIDGET STYLE___')[1:])
        lines = s.splitlines()[1:]
        # Color palette
        color_palette = ast.literal_eval(lines[0].replace('color palette: ', ''))
        # Font
        font = ast.literal_eval(lines[1].replace('font: ', ''))
        style = PlannerWidgetStyle()
        style._color_palette = color_palette
        style._font = font
        return style

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, value):
        if set(value.keys()) != set(FONTS['light'].keys()):
            raise ValueError(f'Invalid font {value}. A valid font must contain the keys {list(FONTS["light"].keys())}')
        self.__init__(color_palette=self.color_palette,
                      font=value)

    @property
    def color_palette(self):
        return self._color_palette

    @color_palette.setter
    def color_palette(self, value):
        if set(value.keys()) != set(COLOR_PALETTES['light'].keys()):
            raise ValueError(f'Invalid font {value}. A valid font must contain the keys '
                             f'{list(COLOR_PALETTES["light"].keys())}')
        self.__init__(color_palette=value,
                      font=self.font)
