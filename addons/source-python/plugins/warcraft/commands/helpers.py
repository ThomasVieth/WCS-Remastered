"""

"""

## python imports

from operator import add, mul, sub, truediv

## all declaration

__all__ = ("operator_options", "retrieve_extra_args", )

## declare available operators

operator_options = {
    "+": add,
    "-": sub,
    "/": truediv,
    "*": mul,
    "=": lambda x, y: y
}

## args generator

def retrieve_extra_args(command, player_index_in_list):
    variable_count = len(command)
    args = []
    for i in range(player_index_in_list + 1, variable_count):
        args.append(command[i])
    return args