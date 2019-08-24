from library import function, clear_global_env

class tcolors:
    """
    colored output terminal
    """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


## testing "library"

test_suite = dict()

def test(expected=True):  # decorator factory. argument: whether you expect the to-be-tested function to return or raise exceptions
    assert isinstance(expected, bool), "test decorator needs to be called, like: `test()`. \
(The parameter is optional, but it's boolean.)"
    def decorator(func):
        # wrap function to be tested with logging
        def wrapped(*args, **kwargs):
            print(f"\n> Test {func.__name__.replace('_',' ')}")
            try:
                func(*args, **kwargs)
                run_smoothly = True
            except Exception as e:
                print(f"{tcolors.WARNING}EXCEPTION{tcolors.ENDC}: {e}")
                run_smoothly = False
            if run_smoothly == expected:
                print(f"{tcolors.OKGREEN}OK{tcolors.ENDC}")
            else:
                print(f"{tcolors.FAIL}FAIL{tcolors.ENDC}")
        # register test function in test suite
        test_suite[func.__name__] = wrapped
        # return wrapped
        return test_suite[func.__name__]
    return decorator


def sterilize():
    clear_global_env()


def run_all_tests():
    print("Starting testing...")
    for k, v in test_suite.items():
        sterilize()
        v()
    print("\n...end tests")


## Helpers

def mkc(value):
    """
    make constant
    :param value:
    :return:
    """
    return function('CONST', value)


def mkv(name):
    """
    make variable
    :param name: name as string
    :return:
    """
    return function('VAR', name)


def bind(var, to):
    """
    bind variable node to another function node
    :param var: variable to bind
    :param to: target function for binding
    :return: returns the bind node, if needed
    """
    assignment = function('BIND', var, to)
    assignment()
    return assignment  # if needed

## functions to be tested

@test(False)
def null_function():
    null = function()
    null()

@test()
def constant_from_value():
    const_3 = function('CONST', 3)
    print(const_3())

# constant from constant
@test(False)
def constant_from_constant():
    const_3bis = function('CONST', mkc(3))
    print(const_3bis())

@test()
def constant_from_constant():
    sum_c = function('SUM',
                     mkc(3),
                     mkc(4))
    # note: c represents a function, not its value. Its value is c(), obtained when evaluated
    print(sum_c())

@test(False)
def sum_from_raw_constants():
    sum_raw = function('SUM', 1, 2)
    print(sum_raw())

@test()
def sum_sums():
    sum_1_2_1_3 = function('SUM',
                        function('SUM', mkc(1), mkc(2)),
                        function('SUM', mkc(1), mkc(3)))
    print(sum_1_2_1_3())  # should be 7 + 10 = 17

@test()
def multiply_constants():
    mul_6 = function('MUL', mkc(2), mkc(3))
    print(mul_6())

@test()
def change_args():
    const_1 = function('CONST', 1)
    const_2 = function('CONST', 2)
    sum_1_2 = function('SUM', const_1, const_2)
    print(sum_1_2())
    sum_2_2 = sum_1_2
    sum_2_2.args = [const_2, const_2]
    print(sum_2_2())

@test()
def create_and_evaluating_unbound_variable():
    x = function('VAR', 'x')
    print(x())

@test()
def bind_to_constant():
    var_x = function('VAR', 'x')
    bind_x = function('BIND', var_x, mkc(1))
    bind_x()
    print(var_x())

@test(False)
def bind_to_raw_value():
    bind_x = function('BIND', function('VAR', 'x'), 2)
    bind_x()

@test(False)
def bind_with_literal_name():
    bind_x = function('BIND', 'x', mkc(2))
    bind_x()

@test()
def bind_variable_to_variable_to_constant():
    # x = y = 2; eval y, x
    x = mkv('x')
    y = mkv('y')
    c2 = mkc(2)
    bind_y_to_2 = function('BIND', y, c2)
    bind_y_to_2()
    bind_x_to_y = function('BIND', x, y)
    bind_x_to_y()
    print(f"y is {y()}, x is {x()}")

@test()
def bind_to_unbound_then_bound():
    x = mkv('x')
    y = mkv('y')
    bound = bind(x, to=y)
    print(f"y is {y()}, x is {x()}")
    c2 = mkc(2)
    bound = bind(y, to=c2)
    print(f"y is {y()}, x is {x()}")

@test(False)
def circular_binding():
    x = mkv('x')
    y = mkv('y')
    bound = bind(x, to=y)
    bound = bind(y, to=x)
    # ok until we evaluate one of those
    print(x())

@test()
def sum_of_variables():
   x = mkv('x')
   y = mkv('y')
   c1 = mkc(1)
   bound = bind(x, c1)
   x_plus_y = function('SUM', x, y)
   print(f"x = 1; x + y is: {x_plus_y()}")
   bound = bind(y, c1)
   print(f"y = 1; x + y is now: {x_plus_y()}")

@test()
def mul_of_variables():
    x = mkv('x')
    y = mkv('y')
    c1 = mkc(1)
    c2 = mkc(2)
    bound = bind(x, c1)
    bound = bind(y, c2)
    x_times_y = function('MUL', x, y)
    x_times_y2 = function('MUL', x_times_y, y)
    print(f"x times y^2: {x_times_y2()}")

@test()
def negative_constant():
    one = mkc(1)
    minus_one = function('NEG', one)
    print(minus_one())

@test(False)
def derivate_raw_primitive():
    derivative_expr = function('DER', 2, mkv('x'))
    derivated_func = derivative_expr()
    print(derivated_func())

@test()
def derivate_constant():
    derivative_expr = function('DER', mkc(5), mkv('x'))
    derivated_func = derivative_expr()
    print(derivated_func())

@test()
def derivate_symbol():
    f = mkv('x')
    df_dx = function('DER', f, mkv('x'))
    f_prime = df_dx()
    print(f"dx/dx is: {f_prime()}")

@test()
def derivative_polynomial():
    x = mkv('x')
    # +(+(1, x), *(x, x))
    c1_plus_x_plus_x2 = function('SUM',
                            function('SUM',
                                mkc(1),
                                x),
                            function('MUL',
                                x,
                                x)
                            )
    derivative_expr = function('DER', c1_plus_x_plus_x2, x)
    c0_plus_c1_plus_x = derivative_expr()
    print(f"D[1+x+x^2, x] = {c0_plus_c1_plus_x}")
    print(f"D[1+x+x^2, x] -evaluated-> {c0_plus_c1_plus_x()}: still UNBOUND")
    bound = bind(x, to=mkc(3))
    print(f"x = 3; D[1+x+x^2, x] -evaluated-> = {c0_plus_c1_plus_x()}: (1 + 2x)|_(x=3) == 7")


## Run tests

run_all_tests()

# to run single tests:
# test_suite['constant_from_value']()
