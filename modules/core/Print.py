# package modules.core


import os as OS
import termcolor as TermColor


import modules.core.typecheck.TypeCheck as TypeCheck
import modules.core.typecheck.Types as Types


def generic(stringIn, repeats=0):
    TypeCheck.enforce(stringIn, Types.STRING)
    TypeCheck.enforce(repeats, Types.INTEGER)
    if repeats == 0:
        print(stringIn)
    else:
        print(stringIn * repeats)
    return


def green(stringIn):
    TypeCheck.enforce(stringIn, Types.STRING)
    print(TermColor.colored(stringIn, "light_green"))
    return


def red(stringIn):
    TypeCheck.enforce(stringIn, Types.STRING)
    print(TermColor.colored(stringIn, "light_red"))
    return


def response(stringIn, endIn):
    TypeCheck.enforce(stringIn, Types.STRING)
    TypeCheck.enforce(endIn, Types.STRING)
    print(TermColor.colored(stringIn, "green"), end=endIn)
    return


def setting(enabledIn, descriptionIn):
    TypeCheck.enforce(enabledIn, Types.BOOLEAN)
    TypeCheck.enforce(descriptionIn, Types.STRING)
    generic(("  [ON]  " if enabledIn else "  [OFF] ") + descriptionIn)
    return


def separator():
    generic("-", 64)
    return


def clear():
    OS.system("clear")
    generic("\n", 128)
    return
