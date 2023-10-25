def set_style(widget, stylesheets):
    """
    Recursively set style sheets to a widget and all its sub-widgets.
    :param widget: :py:class:'QWidget'
        The widget to which the style is set.
    :param stylesheets: dict or str
        A single style sheet or a dictionary of them. Each key can either contain a single style sheet or another dictionary
        of style sheets. Each key must be equal to the attribute name of a sub-widget, internal to 'widget'.
    :return:
    """
    if type(stylesheets) is str: # widget is an 'elementary' QWidget
        widget.setStyleSheet(stylesheets)
    else: # widget is a custom QWidget
        for widget_name in tuple(stylesheets):
            try:
                if widget_name == 'main':
                    widget.setStyleSheet(stylesheets['main'])
                else:
                    set_style(widget=getattr(widget, widget_name),
                              stylesheets=stylesheets[widget_name])
            except Exception as e:
                print(e)