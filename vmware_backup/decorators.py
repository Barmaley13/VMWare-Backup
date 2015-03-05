"""
Collection of decorators to make our life a little easier
Based on a recipe from here:
https://wiki.python.org/moin/PythonDecoratorLibrary
"""

__author__ = 'Kirill V. Belyayev'

__copyright__ = "Copyright 2014, CIMA Systems"
__license__ = "GPL"


### INCLUDES ###
import time

from default_settings import ATTEMPT_NUMBER, ATTEMPT_TIMEOUT


### FUNCTIONS ###
def simple_decorator(decorator):
    """
    This decorator can be used to turn simple functions
    into well-behaved decorators, so long as the decorators
    are fairly simple. If a decorator expects a function and
    returns a function (no descriptors), and if it doesn't
    modify function attributes or docstring, then it is
    eligible to use this. Simply apply @simple_decorator to
    your decorator and it will automatically preserve the
    docstring and function attributes of functions to which
    it is applied.
    """
    def new_decorator(f):
        g = decorator(f)
        g.__name__ = f.__name__
        g.__doc__ = f.__doc__
        g.__dict__.update(f.__dict__)
        return g
    # Now a few lines needed to make simple_decorator itself
    # be a well-behaved decorator.
    new_decorator.__name__ = decorator.__name__
    new_decorator.__doc__ = decorator.__doc__
    new_decorator.__dict__.update(decorator.__dict__)
    return new_decorator


@simple_decorator
def multiple_attempts(func):
    """ Decorator to perform multiple attempts """
    def _multiple_attempts(*args, **kwargs):

        total_attempts = 0
        success = False
        output = None

        while not success and total_attempts < ATTEMPT_NUMBER:
            total_attempts += 1
            kwargs['total_attempts'] = total_attempts

            success, output = func(*args, **kwargs)

            if success or total_attempts >= ATTEMPT_NUMBER:
                break
            else:
                time.sleep(ATTEMPT_TIMEOUT)

        return output

    return _multiple_attempts


if __name__ == '__main__':
    """ Test Unit """
    import random

    from file_system import create_time_stamp
    from default_settings import LOG_TS_FORMAT

    @multiple_attempts
    def test_function(**kwargs):
        """
        Little function that tests above decorator
        Also, gives an example how to use above decorator
        """
        success = False

        print create_time_stamp(LOG_TS_FORMAT), 'Attempt # ' + str(kwargs['total_attempts'])

        random_number = random.random()
        success_margin = 0.75
        if random_number >= success_margin:
            success = True

        print 'Random number: ' + str(random_number)
        print 'Success Margin: ' + str(success_margin)

        return success, random_number

    test_results = test_function()
    print "Test Results: ", str(test_results)