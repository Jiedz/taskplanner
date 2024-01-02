"""
This module define the styles to be used by the task-related widgets.
"""
import os

from taskplanner.gui.utilities import get_primary_screen
from PyQt5.Qt import QSize

COLOR_PALETTES = {
    'dark material':
        {
            'background 1': '#232426',
            'background 2': '#3a3c3f',
            'text': '#ededecff',
            'text - light': '#bcbec4',
            'text - highlight': '#4273bc',
            'border': '#3a3c3f',
        },
}

FONTS = {'light':
    {
        'family': 'Sans Serif',
        'size - title 1': '22pt',
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
                 color_palette: str = 'dark material',
                 font='light'):
        if font not in list(FONTS.keys()):
            raise ValueError(f'Invalid font name {font}. Accepted font names are {tuple(FONTS.keys())}')
        self._font = FONTS[font]
        self.font_name = font
        if color_palette not in list(COLOR_PALETTES.keys()):
            raise ValueError(
                f'Invalid font name {color_palette}. Accepted font names are {tuple(COLOR_PALETTES.keys())}')
        self._color_palette = COLOR_PALETTES[color_palette]
        self.color_palette_name = color_palette
        # Locate icon path
        self.icon_path = os.path.join(*os.path.split(__file__)[:-1])
        self.icon_path = os.path.join(self.icon_path,
                                      'styles/icons',
                                      self.color_palette_name.replace(" ", "-"))
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
                            color:%s
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
                                   self.font['size - text'],
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
                                   self.font['size - title 1'])
                        },
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
                                '''
                        }
                    ,
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
                    'description_textedit':
                        '''
                                        QTextEdit
                                        {
                                            /* background-color:%s; */
                                            font-size:%s;
                                            border:2px solid %s;
                                            border-radius:%s;
                                        }
                                        ''' % (self.color_palette['background 2'],
                                               self.font['size - text'],
                                               self.color_palette['border'],
                                               int(screen_size.width / 220)),
                    'subtask_list_widget':
                        {
                            'icon_label':
                                '''
                                QLabel
                                {
                                    border:None;   
                                }
                                '''
                        }
                },
            'simple view':
                {
                    'task_line_widget':
                        {
                            'main':
                                '''
                                QWidget
                                {
                                    /* background-color:%s; */
                                    border:1px solid %s;
                                    margin:0px;
                                    padding:0px;
                                }
                                ''' % (self.color_palette['background 2'],
                                       self.color_palette['border']),
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
                            'end_date_label':
                                '''
                                QLabel
                                {
                                    border:1px solid %s;
                                    color:%s;
                                    font-size:%s;
                                }
                                ''' % (self.color_palette['border'],
                                       self.color_palette['text - light'],
                                       self.font['size - text']),
                        }
                }
        }

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, name):
        if name not in list(FONTS.keys()):
            raise ValueError(f'Invalid font name {name}. Accepted fonts are {FONTS}')
        self.__init__(color_palette=self.color_palette,
                      font=FONTS[name])

    @property
    def color_palette(self):
        return self._color_palette

    @color_palette.setter
    def color_palette(self, name):
        if name not in list(COLOR_PALETTES.keys()):
            raise ValueError(f'Invalid color_palette name. Accepted color_palettes are {COLOR_PALETTES}')
        self.__init__(font=self.font,
                      color_palette=COLOR_PALETTES[name])


class PlannerWidgetStyle:
    def __init__(self,
                 color_palette: str = 'dark material',
                 font='light'):
        if font not in list(FONTS.keys()):
            raise ValueError(f'Invalid font name {font}. Accepted font names are {tuple(FONTS.keys())}')
        self._font = FONTS[font]
        self.font_name = font
        if color_palette not in list(COLOR_PALETTES.keys()):
            raise ValueError(
                f'Invalid font name {color_palette}. Accepted font names are {tuple(COLOR_PALETTES.keys())}')
        self._color_palette = COLOR_PALETTES[color_palette]
        self.color_palette_name = color_palette
        # Locate icon path
        self.icon_path = os.path.join(*os.path.split(__file__)[:-1])
        self.icon_path = os.path.join(self.icon_path,
                                      'styles/icons',
                                      self.color_palette_name.replace(" ", "-"))
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
                        color:%s
                    }
                    ''' % (self.color_palette['background 1'],
                           self.color_palette['border'],
                           self.font['family'],
                           self.color_palette['text']),
                'planner_tab':
                    {
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
                        'timelines_scrollarea':
                            '''
                                QWidget
                                {
                                    border:None;
                                    margin-top:0px;
                                }
                            ''',
                        'timelines_widget':
                            {
                                'main':
                                    '''
                                    QWidget
                                    {
                                        border:None;
                                    }
                                    '''
                            },
                        'month_widget':
                            {
                                'main':
                                    '''
                                    QFrame
                                    {
                                        border:3px solid %s;
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
                                    }
                                    ''' % (self.color_palette['text - light'],
                                           self.font['size - title 2']),
                            },
                        'week_widget':
                            {
                                'main':
                                    '''
                                    QWidget
                                    {
                                        border:2px solid %s;
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
                                    }
                                    ''' % (self.color_palette['text - light'],
                                           self.font['size - text']),
                            },
                        'day_widget':
                            {
                                'main':
                                    '''
                                    QWidget
                                    {
                                        border:1px solid %s;
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
                                    ''' % (self.color_palette['text - light'],
                                           self.font['size - text - small']),
                            },
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
                        'timeline':
                            {
                                'main':
                                    '''
                                    QWidget
                                    {
                                        margin-left:0px;
                                        padding:0px;
                                    }
                                    ''',
                                'label':
                                    '''
                                    QLabel
                                    {
                                        font-size:%s;
                                    }
                                    ''' % (self.font['size - text'])
                            }
                    }
            }

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, name):
        if name not in list(FONTS.keys()):
            raise ValueError(f'Invalid font name {name}. Accepted fonts are {FONTS}')
        self.__init__(color_palette=self.color_palette,
                      font=FONTS[name])

    @property
    def color_palette(self):
        return self._color_palette

    @color_palette.setter
    def color_palette(self, name):
        if name not in list(COLOR_PALETTES.keys()):
            raise ValueError(f'Invalid color_palette name. Accepted color_palettes are {COLOR_PALETTES}')
        self.__init__(font=self.font,
                      color_palette=COLOR_PALETTES[name])
