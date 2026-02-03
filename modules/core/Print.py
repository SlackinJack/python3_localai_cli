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


def generic(stringIn, repeats=0, tabs=0):
    TypeCheck.enforce(stringIn, Types.STRING)
    TypeCheck.enforce(repeats, Types.INTEGER)
    TypeCheck.enforce(tabs, Types.INTEGER)
    if tabs > 0:
        stringIn = (tabs * "    ") + stringIn
    if getIsServer():
        return __generic_yield(stringIn, repeats=repeats, tabs=tabs)
    else:
        if repeats == 0:    print(stringIn)
        else:               print(stringIn * repeats)
    return stringIn


def __generic_yield(stringIn, repeats=0, tabs=0):
    if repeats == 0:
        yield stringIn + "\n"
    else:
        yield stringIn * repeats
        yield "\n"


def green(stringIn, tabs=0):
    TypeCheck.enforce(stringIn, Types.STRING)
    TypeCheck.enforce(tabs, Types.INTEGER)
    if tabs > 0:
        stringIn = (tabs * "    ") + stringIn
    if getIsServer():
        return __green_yield(stringIn)
    else:
        print(TermColor.colored(stringIn, "light_green"))
    return stringIn


def __green_yield(stringIn):
    yield stringIn + "\n"


def red(stringIn, tabs=0):
    TypeCheck.enforce(stringIn, Types.STRING)
    TypeCheck.enforce(tabs, Types.INTEGER)
    if tabs > 0:
        stringIn = (tabs * "    ") + stringIn
    if getIsServer():
        return __red_yield(stringIn)
    else:
        print(TermColor.colored(stringIn, "light_red"))
    return stringIn


def __red_yield(stringIn):
    yield stringIn + "\n"


def response(stringIn, endIn, tabs=0):
    TypeCheck.enforce(stringIn, Types.STRING)
    TypeCheck.enforce(endIn, Types.STRING)
    TypeCheck.enforce(tabs, Types.INTEGER)
    if tabs > 0:
        stringIn = (tabs * "    ") + stringIn
    if getIsServer():
        return __response_yield(stringIn, endIn)
    else:
        print(TermColor.colored(stringIn, "green"), end=endIn)
    return stringIn + endIn


def __response_yield(stringIn, endIn):
    yield stringIn + endIn


def setting(enabledIn, descriptionIn, tabs=0):
    TypeCheck.enforce(enabledIn, Types.BOOLEAN)
    TypeCheck.enforce(descriptionIn, Types.STRING)
    TypeCheck.enforce(tabs, Types.INTEGER)
    s = "[ON]  " if enabledIn else "[OFF] "
    if tabs > 0:
        s = (tabs * "    ") + s
    s += descriptionIn
    if getIsServer():
        return __setting_yield(s)
    else:
        generic(s)
    return s


def __setting_yield(descriptionIn):
    yield from generic(descriptionIn)


def separator():
    generic("-", 64)
    return


def clear():
    OS.system("clear")
    generic("\n", 128)
    return
