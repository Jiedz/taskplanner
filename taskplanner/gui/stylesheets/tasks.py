'''
This module define the stylesheets to be used by the task-related widgets.
'''
import setuptools

COLOR_PALETTES = {'light earth':
    {
        'main background': 'white',
        'secondary background': '#FCF5ED',
        'urgent': '#CE5A67',
        'text': '#45474B',
        'highlight': '#F4BF96',
        'completed': '#A7D397'
    }
}

FONTS = {'light':
    {
        'family': 'Sans Serif',
        'size - title 1': 20,
        'size - title 2': 16,
        'size - text': 14
    },
    'elegant light':
        {
            'family': 'Liberation Serif',#'Oregano',
            'size - title 1': 20,
            'size - title 2': 16,
            'size - text': 14
        }
}


class TaskWidgetStyle:
    def __init__(self,
                 color_palette: dict = COLOR_PALETTES['light earth'],
                 font=FONTS['light']):
        self._font, self._color_palette = font, color_palette
        self.stylesheets = {
                            'standard view':
                                {
                                    'main':
                                        '''
                                        QWidget
                                        {
                                            background-color:%s;
                                            border:2px solid %s;
                                            border-radius:5px;
                                            font-family:%s;
                                            color:%s
                                        }
                                        '''%(self.color_palette['main background'],
                                             self.color_palette['highlight'],
                                             self.font['family'],
                                             self.color_palette['text']),
                                    'scroll_area':
                                        '''
                                        QWidget
                                        {
                                            background-color:%s;
                                            border:2px solid %s;
                                            border-radius:5px;
                                            font-family:%s;
                                            color:%s
                                        }
                                        ''' % (
                                        self.color_palette['main background'],
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
                                                    border-radius:5px;
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
                                                    border-radius:5px;
                                                    font-size:%s;
                                                    background-color:%s
                                                }   
                                                '''%(self.color_palette['highlight'],
                                                     self.font['size - text'],
                                                     self.color_palette['secondary background']),
                                            'completed_pushbutton':
                                                '''
                                                QPushButton:hover
                                                {
                                                    background-color:%s;
                                                    color:white;
                                                }
                                                QPushButton:checked
                                                {
                                                    background-color:%s;
                                                    color:white;
                                                }
                                                '''%(self.color_palette['completed'],
                                                     self.color_palette['completed']),
                                            'close_pushbutton':
                                                '''
                                                QPushButton:hover
                                                {
                                                    background-color:%s;
                                                    color:white;
                                                }
                                                QPushButton:checked
                                                {
                                                    background-color:%s;
                                                    color:white;
                                                }
                                                ''' % (self.color_palette['urgent'],
                                                       self.color_palette['urgent']),


                                        },
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
