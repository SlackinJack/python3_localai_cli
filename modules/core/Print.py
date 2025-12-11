# package modules.core


import os as OS
import termcolor as TermColor


import modules.core.typecheck.TypeCheck as TypeCheck
import modules.core.typecheck.Types as Types


__isServer = False


def getIsServer():
    global __isServer
    return __isServer


def setIsServer(isServerIn):
    global __isServer
    __isServer = isServerIn


def generic(stringIn, repeats=0):
    TypeCheck.enforce(stringIn, Types.STRING)
    TypeCheck.enforce(repeats, Types.INTEGER)
    if getIsServer():
        return generic_yield(stringIn, repeats=0)
    else:
        if repeats == 0:    print(stringIn)
        else:               print(stringIn * repeats)
    return stringIn


def generic_yield(stringIn, repeats=0):
    if repeats == 0:
        yield stringIn + "\n"
    else:
        yield stringIn * repeats
        yield "\n"


def green(stringIn):
    TypeCheck.enforce(stringIn, Types.STRING)
    if getIsServer():
        return green_yield(stringIn)
    else:
        print(TermColor.colored(stringIn, "light_green"))
    return stringIn


def green_yield(stringIn):
    yield stringIn + "\n"


def red(stringIn):
    TypeCheck.enforce(stringIn, Types.STRING)
    if getIsServer():
        return red_yield(stringIn)
    else:
        print(TermColor.colored(stringIn, "light_red"))
    return stringIn


def red_yield(stringIn):
    yield stringIn + "\n"


def response(stringIn, endIn):
    TypeCheck.enforce(stringIn, Types.STRING)
    TypeCheck.enforce(endIn, Types.STRING)
    if getIsServer():
        return response_yield(stringIn, endIn)
    else:
        print(TermColor.colored(stringIn, "green"), end=endIn)
    return stringIn + endIn


def response_yield(stringIn, endIn):
    yield stringIn + endIn


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
