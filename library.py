from typing import Set, Any, Dict

## function object

# Tree of functions, that can be called
class function:
    def __init__(self, f_type='NONE', *args):
        self.type = f_type
        self.args = args  # list of functions

        self.debug = True

    def __call__(self, args=[]):
        # TODO what is the semantics of being able to pass args dynamically at evaluation time?
        # should I just keep the args at construction/definition/compilation time?
        if len(args) > 0:
            self.args = args

        if self.debug:
            print(f"calling {self.type} with args {fmt_args(self.args)}")  # TODO how to indent this based on call depth?

        return call_table[self.type](self.args)

    def __str__(self):
        str_args = fmt_args(self.args)
        return f"{self.type}({str_args})"

    def __repr__(self):
        return self.__str__()


def fmt_args(args):
    if len(args) == 0:
        return ''
    elif len(args) == 1:
        return f'{args[0]}'
    else:
        return f'{args}'


## Helpers

def assert_size_args(args, size, f_type):
    assert len(args) == size, f"{f_type} requires {size} arguments"


def assert_func_args(args):
    for a in args:
        assert isinstance(a, function), f"argument {a} is not a <function>. All arguments must be."


def assert_is_primitive(value, msg):
    t = type(value)
    assert t is int or t is float, f"Assertion for numeric primitive. {msg}"


## environment

env: Dict[str, function] = dict()
looked_up_symbols: Set[str] = set()  # cache symbols at each variable resolution to avoid circular dependencies


def clear_global_env():
    global env
    env = dict()


## call contents

def call_none(args):
    raise Exception("NONE function can't be called/evaluated")


def call_const(args):
    assert_size_args(args, 1, 'CONST')
    const_value = args[0]
    assert_is_primitive(const_value, 'CONST')
    return const_value


def call_var(args):
    # Evaluating a variable, think of "x" in a mathematical expression like "x + 2",
    # This is NOT an assignment, but it may be part of an assignment (evaluation
    # of a function that binds a name to a constant or to a variable in the 
    # environment)
    assert_size_args(args, 1, 'VAR')
    symbol_name = args[0]
    assert isinstance(symbol_name, str), f"evaluating variable. symbol name: {symbol_name} must be a string."
    if symbol_name in env:
        if symbol_name not in looked_up_symbols:
            looked_up_symbols.add(symbol_name)
            result = env[symbol_name]()
            # TODO implement caching of evaluated value, if e.g. you need to evaluate same variable multime times in same expression
            looked_up_symbols.clear()
            return result
        else:
            message = f"""Circular dependency found! Variable {symbol_name} depends on variables 
that ultimately depend on itself. Looked up variables: {looked_up_symbols}"""
            looked_up_symbols.clear()  # TODO needed? just clearing up for sake of cleaning
            raise Exception(message)
    else:
        return 'UNBOUND'


def call_bind(args):
    # Assignment. The '=' in mathematical expressions like 'x = 3'
    # which here would be 'bind(var('x'), const(3))'
    assert_size_args(args, 2, 'BIND')
    assert_func_args(args)
    variable, value = args
    assert variable.type == 'VAR', f"error while binding. {variable} should be a VAR function"
    symbol_name = variable.args[0]
    env[symbol_name] = value
    return variable # TODO think: is it the best thing to return the variable itself? should I return the bind node?


def call_neg(args):
    assert_size_args(args, 1, 'NEG')
    operand = args[0]()
    if 'UNBOUND' == operand:
        return 'UNBOUND'
    else:
        return - operand


def call_sum(args):
    assert_size_args(args, 2, 'SUM')
    left_operand = args[0]()
    right_operand = args[1]()
    # TODO do early stopping, returning UNBOUND as soon as you find one unbound, or evaluating both to do syntax checking?
    if 'UNBOUND' in [left_operand, right_operand]:
        return 'UNBOUND'
    else:
        return args[0]() + args[1]()


def call_mul(args):
    assert_size_args(args, 2, 'SUM')
    left_operand = args[0]()
    right_operand = args[1]()
    if 'UNBOUND' in [left_operand, right_operand]:
        return 'UNBOUND'
    else:
        return args[0]() * args[1]()


def call_der(args):
    """
    derivative operator
    IN: function, symbol with respect to which derivate
    OUT: function (if you want the value of the outputted function, evaluate again!)
    e.g. D(x -> x^2) = x -> 2*x
    i.e. DER(MUL(VAR(X),VAR(X)) -eval-> MUL(DER(VAR(X)),VAR(X)) + MUL(VAR(X),DER(VAR(X)))
    """
    assert_size_args(args, 2, 'DER')
    f, x = args
    if f.type == 'CONST':
        return function('CONST', 0)
    elif f.type == 'VAR':
        symbol_name = f.args[0]
        if symbol_name == 'x':
            # df(x)/dx
            return function('CONST', 1)
        else:
            # df(y)/dx : derivating w.r.t. another variable!
            return function('CONST', 0)
    elif f.type == 'SUM':
        a, b = f.args
        return function('SUM',
                        function('DER', a, x).__call__(),
                        function('DER', b, x).__call__()
                        )
    elif f.type == 'MUL':
        a, b = f.args
        return function('SUM',
                        function('MUL',
                                 function('DER', a, x).__call__(),
                                 b),
                        function('MUL',
                                 a,
                                 function('DER', b, x).__call__())
                        )
    else:
        raise NotImplementedError

call_table = dict(
    NONE=call_none,
    CONST=call_const,
    SUM=call_sum,
    MUL=call_mul,
    DER=call_der,
    BIND=call_bind,
    VAR=call_var, # TODO probably "SYM(BOL)" is a more suited term than "VAR(IABLE)"
    NEG=call_neg,
)

