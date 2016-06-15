from sample_0020_basic import greeting  # greeting is included in top-level container
from sample_0020_basic import display_color as _color  # display_color is not included in top-level container

class my_favorites:
    color = _color
    greeting = greeting
