"""
This module define the styles to be used by the task-related widgets.
"""
import os

from taskplanner.gui.utilities import get_screen_size
from PyQt5.Qt import QSize

COLOR_PALETTES = {
    'dark material':
        {
            'main background': '#232426',#'#1e1f22',
            'secondary background': '#3a3c3f', #'#2b2d30',
            'text': 'white',#'#bcbec4',
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

ICON_SIZES = {'regular': QSize(40, 40),
              'small': QSize(25, 25)}


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
                                      'icons',
                                      self.color_palette_name.replace(" ", "-"))
        # Get screen size
        screen_size = get_screen_size()
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
                                        ''' % (self.color_palette['main background'],
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
                    ''' % (self.color_palette['main background'],
                           self.color_palette['border'],
                           self.color_palette['main background'],
                           self.color_palette['border'],
                           self.color_palette['main background'],
                           self.color_palette['border'],
                           self.color_palette['main background'],
                           self.color_palette['border'],
                           self.color_palette['main background'],
                           self.color_palette['border'],
                           self.color_palette['main background'],
                           self.color_palette['border'],
                           self.color_palette['main background'],
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
                            ''' % (self.color_palette['secondary background'],
                                   self.color_palette['text'],
                                   self.font['size - title 1'])
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
                                }
                                ''' % (self.color_palette['border'],
                                       self.color_palette['text'],
                                       self.font['size - text - small']),
                        },
                    'category_widget':
                        {
                            'icon_pushbutton':
                                '''
                                                QPushButton
                                                {
                                                    border: 0px;
                                                    /* border-radius:%s; */
                                                }
                                                ''' % (int(screen_size.width / 220)),
                            'combobox':
                                '''
                                                QComboBox
                                                {
                                                    font-size:%s;
                                                    border:2px solid %s;
                                                    border-radius:%spx;
                                                }
                                                ''' % (self.font['size - text'],
                                                       self.color_palette['border'],
                                                       int(screen_size.width / 220)),
                            'add_pushbutton':
                                '''
                                                QPushButton
                                                {
                                                    border-radius:%spx;
                                                    border:2px solid %s;
                                                }
                                                QPushButton:hover
                                                {
                                                    background-color:%s;
                                                }
                                                ''' % (int(screen_size.width / 220),
                                                       self.color_palette['border'],
                                                       self.color_palette['border']),
                        },
                    'priority_widget':
                        {
                            'icon_pushbutton':
                                '''
                                                QPushButton
                                                {
                                                    border: 0px;
                                                    /* border-radius:%s; */
                                                }
                                                ''' % (int(screen_size.width / 220)),
                            'combobox':
                                '''
                                                QComboBox
                                                {
                                                    font-size:%s;
                                                    border-radius:%s;
                                                }
                                                ''' % (self.font['size - text'],
                                                       int(screen_size.width / 220))
                        },
                    'assignee_widget':
                        {
                            'icon_pushbutton':
                                '''
                                            QPushButton
                                            {
                                                border: 0px;
                                                /* border-radius:%s; */
                                            }
                                            ''' % (int(screen_size.width / 220)),
                        },

                    'description_textedit':
                        '''
                                        QTextEdit
                                        {
                                            font-size:%s;
                                            border:2px solid %s;
                                            border-radius:%s;
                                        }
                                        ''' % (self.font['size - text'],
                                               self.color_palette['border'],
                                               int(screen_size.width / 220))
                },
            'simple view':
                {

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
