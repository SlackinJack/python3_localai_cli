# modules.util


import termcolor as TermColor


import modules.typecheck.TypeCheck as TypeCheck
import modules.typecheck.Types as Types


def generic(stringIn, repeats=0):
    TypeCheck.check(stringIn, Types.STRING)
    TypeCheck.check(repeats, Types.INTEGER)
    if repeats == 0:    print(stringIn)
    else:               print(stringIn * repeats)
    return


def green(stringIn):
    TypeCheck.check(stringIn, Types.STRING)
    print(TermColor.colored(stringIn, "light_green"))
    return


def red(stringIn):
    TypeCheck.check(stringIn, Types.STRING)
    print(TermColor.colored(stringIn, "light_red"))
    return


def response(stringIn, endIn):
    TypeCheck.check(stringIn, Types.STRING)
    TypeCheck.check(endIn, Types.STRING)
    print(TermColor.colored(stringIn, "green"), end=endIn)
    return


def setting(enabledIn, descriptionIn):
    TypeCheck.check(enabledIn, Types.BOOLEAN)
    TypeCheck.check(descriptionIn, Types.STRING)
    generic(("  [ON]  " if enabledIn else "  [OFF] ") + descriptionIn)
    return


def separator():
    generic("-", 64)
    return


def clear():
    generic("\n", 64)
    return
