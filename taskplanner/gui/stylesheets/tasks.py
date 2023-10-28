'''
This module define the stylesheets to be used by the task-related widgets.
'''
import setuptools, inspect, os, sys
from taskplanner.gui.utilities import get_screen_size

COLOR_PALETTES = {'light earth':
    {
        'main background': 'white',
        'secondary background': '#FCF5ED',
        'urgent': '#CE5A67',
        'text': '#45474B',
        'text - light':'gray',
        'highlight': '#F4BF96',
        'completed': '#A7D397'
    },
    'deep purple':
    {
        'main background': '#35155D',
        'secondary background': '#512B81',
        'urgent': '#9D44C0',
        'text': '#F0F0F0',
        'text - light':'#F0F0F0',
        'highlight': '#4477CE',
        'completed': '#8CABFF'
    }
}

FONTS = {'light':
    {
        'family': 'Sans Serif',
        'size - title 1': '22pt',
        'size - title 2': '16pt',
        'size - text': '12pt'
    },
    'elegant light':
        {
            'family': 'Liberation Serif',#'Oregano',
            'size - title 1': '22pt',
            'size - title 2': '16pt',
            'size - text': '12pt'
        }
}


class TaskWidgetStyle:
    def __init__(self,
                 color_palette: str = 'light earth',
                 font='light'):
        if font not in list(FONTS.keys()):
            raise ValueError(f'Invalid font name {font}. Accepted font names are {tuple(FONTS.keys())}')
        self._font = FONTS[font]
        self.font_name = font
        if color_palette not in list(COLOR_PALETTES.keys()):
            raise ValueError(f'Invalid font name {color_palette}. Accepted font names are {tuple(COLOR_PALETTES.keys())}')
        self._color_palette = COLOR_PALETTES[color_palette]
        self.color_palette_name = color_palette
        # Locate icon path
        self.icon_path = '/'.join(__file__.split('/')[:-1])
        self.icon_path = os.path.join(self.icon_path, f'Icons/{self.color_palette_name.replace(" ", "-")}')
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
                                        '''%(self.color_palette['main background'],
                                             self.color_palette['highlight'],
                                             self.font['family'],
                                             self.color_palette['text']),
                                    'toolbar':
                                        {
                                            'main':
                                                '''
                                                QWidget
                                                {
                                                    background-color:%s;
                                                    border:2px solid %s;
                                                    border-radius:10px;
                                                    font-size:%s;
                                                }
                                                ''' % (
                                                        self.color_palette['secondary background'],
                                                        self.color_palette['highlight'],
                                                        self.font['size - title 1'])
                                                +
                                                '''
                                                QPushButton
                                                {
                                                    border:2px solid %s;
                                                    border-radius:10px;
                                                    font-size:%s;
                                                    background-color:%s
                                                }   
                                                '''%(self.color_palette['highlight'],
                                                     self.font['size - text'],
                                                     self.color_palette['secondary background']),

                                            'completed_pushbutton':
                                                '''
                                                QPushButton
                                                {
                                                    /* background-color */
                                                    border-radius:%spx;
                                                }
                                                QPushButton:hover
                                                {
                                                    background-color:%s;
                                                    color:white;
                                                    
                                                }
                                                '''%(int(screen_size.width/120),
                                                    self.color_palette['completed']),

                                            'path_label':
                                                '''
                                                QLabel
                                                {
                                                    font-size:%s;
                                                    color:%s;
                                                    border:None;
                                                }
                                                '''%(self.font['size - text'],
                                                     self.color_palette['text - light']),
                                            'category_widget':
                                                {
                                                    'categories_combobox':
                                                        '''
                                                        QComboBox
                                                        {
                                                            font-size:%s;
                                                            border:2px solid %s;
                                                            border-radius:10px;
                                                        }
                                                        '''%(self.font['size - text'],
                                                             self.color_palette['highlight'],
                                                             ),
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
                                                        '''%(int(screen_size.width/180),
                                                            self.color_palette['highlight'],
                                                             self.color_palette['highlight']),
                                                }
                                        },

                                    'name_linedit':
                                        '''
                                        QLineEdit
                                        {
                                            font-size:%s;
                                            border:2px solid %s
                                        }
                                        '''%(self.font['size - title 1'],
                                             self.color_palette['highlight']),

                                    'description_textedit':
                                        '''
                                        QTextEdit
                                        {
                                            font-size:%s;
                                            border:2px solid %s
                                        }
                                        ''' % (self.font['size - text'],
                                               self.color_palette['highlight'])
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
