# encoding: utf-8

import operator


__all__ = ('math', 'MyClass')


def math(arg1, arg2, arith_operator='+'):
    """Performs an arithmetic operation.

    This function accepts to numbers and performs an arithmetic operation
    with them. The arithmetic operation can be passed as a string. By default,
    the addition operator is assumed.

    Parameters:
        arg1,arg2 (float):
            The numbers that we will sub/subtract/multiply/divide.
        arith_operator ({'+', '-', '*', '/'}):
            A string indicating the arithmetic operation to perform.

    Returns:
        result (float):
            The result of the arithmetic operation.

    Example:
      >>> math(2, 2, arith_operator='*')
      >>> 4

    """

    str_to_operator = {'+': operator.add,
                       '-': operator.sub,
                       '*': operator.mul,
                       '/': operator.truediv}

    return str_to_operator[arith_operator](arg1, arg2)


class MyClass(object):
    """A description of the class.

    The top docstring in a class describes the class in general, and the
    parameters to be passed to the class ``__init__``.

    Parameters:
        arg1 (float):
            The first argument.
        arg2 (int):
            The second argument.
        kwarg1 (str):
            A keyword argument.

    Attributes:
        name (str): A description of what names gives access to.

    """

    def __init__(self, arg1, arg2, kwarg1='a'):

        self.name = arg1

    def do_something(self):
        """A description of what this method does."""

        pass

    def do_something_else(self, param):
        """A description of what this method does.

        If the class only has one or two arguments, you can describe them
        inline. ``param`` is the parameter that we use to do something else.

        """

        pass
