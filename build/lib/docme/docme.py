from .decorators import *


def auto_doc(dict_functions, app_name, options={}):
    to_decorate_functions = ["before_all", "after_all", "before_feature",
                             "after_feature", "before_scenario", "after_scenario",
                             "before_step", "after_step"]
    for func in to_decorate_functions:
        decorator = eval(decorator_for_function(func))
        if func in dict_functions:
            dict_functions[func] = decorator(dict_functions[func], options, app_name)
        else:
            fake_function = lambda *args: None
            fake_function.__globals__["__file__"] = dict_functions["__file__"]
            dict_functions[func] = decorator(fake_function, options, app_name)


def decorator_for_function(function_name):
    words = function_name.split('_')
    return "".join([w.capitalize() for w in words]) + 'Decorator'


