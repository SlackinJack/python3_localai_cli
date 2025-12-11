# package modules.core


import datetime as DateTime
import difflib as DiffLib
import json as JSON
import random as Random
import re as Regex
import readline as ReadLine  # unused, but fixes keyboard arrow keys for inputs
import termcolor as TermColor
import time as Time


import modules.core.Configuration as Configuration
import modules.core.Print as Print
import modules.core.typecheck.TypeCheck as TypeCheck
import modules.core.typecheck.Types as Types


__keybindStop = None
__keybindStopName = ""
__shouldInterruptCurrentOutputProcess = True


def getKeybindStopName():
    # NOTE: Remap keybind here if necessary

    # NOTE: if keybinds dont work, and you are using wayland,
    # then you need to enable x11 support
    import pynput as Pynput
    global __keybindStop, __keybindStopName
    __keybindStop = Pynput.keyboard.Key.f12
    __keybindStopName = str(__keybindStop).upper().split(".")[1]
    return __keybindStopName


def keyListener(key):
    global __shouldInterruptCurrentOutputProcess, __keybindStop
    if key == __keybindStop:
        if not __shouldInterruptCurrentOutputProcess:
            __shouldInterruptCurrentOutputProcess = True
            Print.generic("")
            Print.separator()
            Print.red(f"[{__keybindStopName}] pressed - waiting for process to complete then exiting...")
            Print.separator()
            Print.generic("")
    return


def setShouldInterruptCurrentOutputProcess(shouldInterrupt):
    TypeCheck.enforce(shouldInterrupt, Types.BOOLEAN)
    global __shouldInterruptCurrentOutputProcess
    __shouldInterruptCurrentOutputProcess = shouldInterrupt
    return


def getShouldInterruptCurrentOutputProcess():
    return __shouldInterruptCurrentOutputProcess


def printInput(titleIn):
    TypeCheck.enforce(titleIn, Types.STRING)
    Print.separator()
    result = input(titleIn + ": ")
    Print.separator()
    clearWindowIfAllowed()
    return result


def printError(stringIn):
    TypeCheck.enforce(stringIn, Types.STRING)
    if Configuration.getConfig("debug_level") >= 1:
        if Print.getIsServer():
            return yieldError(stringIn)
        else:
            print(TermColor.colored(stringIn, "red"))
    return stringIn


def yieldError(stringIn):
    yield f"[ERR]: {stringIn}\n"


def printInfo(stringIn):
    TypeCheck.enforce(stringIn, Types.STRING)
    if Configuration.getConfig("debug_level") >= 2:
        if Print.getIsServer():
            return yieldInfo(stringIn)
        else:
            print(TermColor.colored(stringIn, "yellow"))
    return stringIn


def yieldInfo(stringIn):
    yield f"[INF]: {stringIn}\n"


def printDebug(stringIn):
    TypeCheck.enforce(stringIn, Types.STRING)
    if Configuration.getConfig("debug_level") >= 3:
        if Print.getIsServer():
            return yieldDebug(stringIn)
        else:
            print(TermColor.colored(stringIn, Configuration.getConfig("debug_text_color")))
    return stringIn


def yieldDebug(stringIn):
    yield f"[DBG]: {stringIn}\n"


def printDump(stringIn):
    TypeCheck.enforce(stringIn, Types.STRING)
    if Configuration.getConfig("debug_level") >= 4:
        if Print.getIsServer():
            return yieldDump(stringIn)
        else:
            print(TermColor.colored(stringIn, Configuration.getConfig("dump_text_color")))
    return stringIn


def yieldDump(stringIn):
    yield f"[DMP]: {stringIn}\n"


def printPromptHistory(promptHistoryIn):
    TypeCheck.enforce(promptHistoryIn, Types.LIST)
    printDump("Current conversation:")
    for item in promptHistoryIn:
        printDump("" + item["content"])
    return


def clearWindowIfAllowed():
    if Configuration.getConfig("clear_window_before_every_prompt"):
        Print.clear()
    return


def printYNQuestion(messageIn):
    TypeCheck.enforce(messageIn, Types.STRING)
    if len(messageIn) > 0:
        if Configuration.getConfig("always_yes_to_yn"):
            return 0
        else:
            result = printInput(messageIn + " ([Y]es/[N]o/[E]xit)")
            result = result.lower()
            if result.lower().startswith("y"):
                return 0
            elif result.lower().startswith("e"):
                return 2
            else:
                Print.generic("Invalid option - assuming \"No\".")
                return 1
    return None


def printMenu(titleIn, descriptionIn, choicesIn):
    TypeCheck.enforce(titleIn, Types.STRING)
    TypeCheck.enforce(descriptionIn, Types.STRING)
    TypeCheck.enforce(choicesIn, Types.LIST)
    Print.generic(titleIn + ":")
    Print.generic("(Tip: Use quotes to insert literal numbers (e.g. '123' or \"123\")).")
    if len(descriptionIn) > 0:
        Print.generic(descriptionIn)
    i = 0
    for c in choicesIn:
        Print.generic("  (" + str(i + 1) + ") " + c)
        i += 1
    Print.generic("  (0) Exit")
    selection = printInput("Select item")
    escaped = False
    if "\"" in selection or '"' in selection:
        escaped = True
        selection = selection.replace("\"", "").replace("'", "")
    else:
        if selection == "0":
            selection = None
        else:
            result = intVerifier(selection)
            if result[1]:
                theResult = result[0] - 1
                if theResult <= len(choicesIn) - 1:
                    selection = choicesIn[theResult]
                else:
                    selection = ""
    if escaped:
        Print.generic("Quotes in input - escaped from numerical options.")
    return selection


def printCurrentSystemPrompt(printerIn, spaceIn):
    TypeCheck.enforce(printerIn, Types.FUNCTION)
    TypeCheck.enforce(spaceIn, Types.STRING)
    if printerIn is not None:
        systemPrompt = Configuration.getConfig("system_prompt")
        if len(systemPrompt) > 0:
            printerIn("  " + systemPrompt + spaceIn)
        else:
            printerIn("  (Empty)" + spaceIn)
    return


blankCharacters = ["\f", "\n", "\r", "\t", "\v"]


def checkEmptyString(strIn):
    TypeCheck.enforceList(strIn, [Types.STRING, Types.NONE])
    if strIn is None:
        return True
    else:
        blanks = blankCharacters + [" "]
        for s in strIn:
            if s not in blanks:
                return False
        return True


def cleanupString(stringIn):
    TypeCheck.enforce(stringIn, Types.STRING)
    for char in blankCharacters: out = stringIn.replace(char, " ")  # remove all spaces
    out = " ".join(out.split())                                     # remove all redundant spaces
    if Configuration.getConfig("unicode_only"):
        out = (out.encode("ascii", errors="ignore")).decode()       # drop all non-ascii chars
    return out


def cleanupServerResponseTokens(stringIn):
    TypeCheck.enforce(stringIn, Types.STRING)
    stringOut = stringIn
    # for s in __serverResponseTokens:
    #     stringOut = stringOut.replace(s, "")
    return stringOut


def trimTextBySentenceLength(textIn, maxLength):
    TypeCheck.enforce(textIn, Types.STRING)
    TypeCheck.enforce(maxLength, Types.INTEGER)
    i = 0               # char position
    j = 0               # sentences
    k = 0               # chars since last sentence
    flag = False        # deleted a "short" sentence this run
    m = 36              # "short" sentence chars threshold
    for char in textIn:
        i += 1
        k += 1
        parse = False
        if "!" == char:
            parse = True
        elif "?" == char:
            parse = True
        elif "." == char:
            charBefore = textIn[i - 1]
            if not charBefore.isnumeric():
                parse = True
            if not parse:
                charAfter = None
                if i + 1 < len(textIn):
                    charAfter = textIn[i + 1]
                if charAfter is not None and not charAfter.isnumeric():
                    parse = True
        if parse:
            j += 1
            if k < m and not flag:
                j -= 1
                flag = True
            if j == maxLength:
                return textIn[0:i]
            k = 0
            flag = False
    return textIn


def formatArrayToString(arrayIn, separator):
    TypeCheck.enforce(arrayIn, Types.LIST)
    TypeCheck.enforce(separator, Types.STRING)
    return separator.join(str(s) for s in arrayIn)


def formatJSONToString(dictionaryIn):
    TypeCheck.enforce(dictionaryIn, Types.DICTIONARY)
    return JSON.dumps(dictionaryIn, indent=4)


def getGrammarString(listIn):
    TypeCheck.enforce(listIn, Types.LIST)
    grammarStringBuilder = "root ::= ("     # length is 10
    for item in listIn:
        if len(grammarStringBuilder) > 10:  # length from above
            grammarStringBuilder += " | "
        grammarStringBuilder += "\"" + item + "\""
    grammarStringBuilder += ")"
    return grammarStringBuilder


def errorBlankEmptyText(sourceIn):
    TypeCheck.enforce(sourceIn, Types.STRING)
    printError("The " + sourceIn + " is empty/blank!")
    return "The text received from the " + sourceIn + " is blank and/or empty."


def getRandomSeed():
    return Random.randrange(1, (2 ** 32) - 1)


def removeApostrophesFromFileInput(stringIn):
    TypeCheck.enforce(stringIn, Types.STRING)
    stringOut = stringIn.replace("' ", "").replace("'", "")
    return stringOut


def getStringMatchPercentage(sourceStringIn, targetStringIn):
    TypeCheck.enforce(sourceStringIn, Types.STRING)
    TypeCheck.enforce(targetStringIn, Types.STRING)
    return DiffLib.SequenceMatcher(None, sourceStringIn, targetStringIn).ratio() * 100


def getFilePathFromPrompt(stringIn):
    TypeCheck.enforce(stringIn, Types.STRING)
    result = Regex.findall(r"""(?:~?\/{1})(?:(?:[a-zA-Z0-9 ._\-\!\@\$\%\^\&\*\(\)\[\]\<\>]*)(?:[a-zA-Z0-9._\-\!\@\$\%\^\&\*\(\)\[\]\<\>]+)(?:[\/]?))*""", stringIn, Regex.DOTALL)
    out = []
    for r in result:
        r2 = r
        if r2.endswith(" "): r2 = replaceLast(r2, " ", "")
        out.append(r2)
    return out


def replaceLast(stringIn, replaceTextIn, replacementTextIn):
    TypeCheck.enforce(stringIn, Types.STRING)
    TypeCheck.enforce(replaceTextIn, Types.STRING)
    TypeCheck.enforce(replacementTextIn, Types.STRING)
    stringOut = stringIn[::-1].replace(replaceTextIn[::-1], replacementTextIn[::-1], 1)[::-1]
    return stringOut


# Unused, maybe useful in the future
def padStringsToSameLength(stringListIn):
    TypeCheck.enforce(stringListIn, Types.LIST)
    longestStringLength = 0
    for s in stringListIn:
        if len(s) > longestStringLength:
            longestStringLength = len(s)
    for s in stringListIn:
        s = padStringToLength(s, longestStringLength)
    return stringListIn


def padStringToLength(stringIn, lengthIn):
    TypeCheck.enforce(stringIn, Types.STRING)
    TypeCheck.enforce(lengthIn, Types.INTEGER)
    while len(stringIn) < lengthIn:
        stringIn += " "
    return stringIn


def setOrDefault(promptIn, defaultValueIn, verifierFuncIn, keepDefaultValueStringIn, setValueStringIn, verifierErrorStringIn):
    TypeCheck.enforce(promptIn, Types.STRING)
    TypeCheck.enforce(verifierFuncIn, Types.FUNCTION)
    TypeCheck.enforce(keepDefaultValueStringIn, Types.STRING)
    TypeCheck.enforce(setValueStringIn, Types.STRING)
    TypeCheck.enforce(verifierErrorStringIn, Types.STRING)

    return setOr(
        promptIn,
        "leave empty for current",
        defaultValueIn,
        verifierFuncIn,
        keepDefaultValueStringIn,
        setValueStringIn,
        verifierErrorStringIn,
    )


def setOrPresetValue(promptIn, presetValueIn, verifierFuncIn, presetTypeStringIn, presetValueStringIn, verifierErrorStringIn):
    TypeCheck.enforce(promptIn, Types.STRING)
    TypeCheck.enforce(verifierFuncIn, Types.FUNCTION)
    TypeCheck.enforce(presetTypeStringIn, Types.STRING)
    TypeCheck.enforce(presetValueStringIn, Types.STRING)
    TypeCheck.enforce(verifierErrorStringIn, Types.STRING)

    return setOrPresetValueWithResult(
        promptIn,
        presetValueIn,
        verifierFuncIn,
        presetTypeStringIn,
        presetValueStringIn,
        "",
        verifierErrorStringIn,
    )


def setOrPresetValueWithResult(promptIn, presetValueIn, verifierFuncIn, presetTypeStringIn, presetValueStringIn, verifiedResultStringIn, verifierErrorStringIn):
    TypeCheck.enforce(promptIn, Types.STRING)
    TypeCheck.enforce(verifierFuncIn, Types.FUNCTION)
    TypeCheck.enforce(presetTypeStringIn, Types.STRING)
    TypeCheck.enforce(presetValueStringIn, Types.STRING)
    TypeCheck.enforce(verifiedResultStringIn, Types.STRING)
    TypeCheck.enforce(verifierErrorStringIn, Types.STRING)

    return setOr(
        promptIn,
        "leave empty for " + presetTypeStringIn,
        presetValueIn,
        verifierFuncIn,
        presetValueStringIn,
        verifiedResultStringIn,
        verifierErrorStringIn,
    )


def setOr(promptIn, leaveEmptyMessageIn, valueIn, verifierFuncIn, noResultMessageIn, verifiedResultMessageIn, verifierErrorMessageIn):
    TypeCheck.enforce(promptIn, Types.STRING)
    TypeCheck.enforce(leaveEmptyMessageIn, Types.STRING)
    TypeCheck.enforce(verifierFuncIn, Types.FUNCTION)
    TypeCheck.enforce(noResultMessageIn, Types.STRING)
    TypeCheck.enforce(verifiedResultMessageIn, Types.STRING)
    TypeCheck.enforce(verifierErrorMessageIn, Types.STRING)

    if promptIn is not None and leaveEmptyMessageIn is not None and valueIn is not None and verifierFuncIn is not None and noResultMessageIn is not None and verifiedResultMessageIn is not None and verifierErrorMessageIn is not None:
        result = printInput(promptIn + " (" + leaveEmptyMessageIn + " \"" + str(valueIn) + "\")")
        if len(result) == 0:
            Print.red(noResultMessageIn + ": " + str(valueIn))
            return valueIn
        else:
            verifiedResult = verifierFuncIn(result)
            if verifiedResult[1]:
                if len(verifiedResultMessageIn) > 0:
                    Print.green(verifiedResultMessageIn + ": " + str(verifiedResult[0]))
                return verifiedResult[0]
            else:
                printError(verifierErrorMessageIn + ": " + str(valueIn))
                return valueIn
    return None


def toggleSetting(settingIn, disableStringIn, enableStringIn):
    TypeCheck.enforce(settingIn, Types.BOOLEAN)
    TypeCheck.enforce(disableStringIn, Types.STRING)
    TypeCheck.enforce(enableStringIn, Types.STRING)
    if settingIn:
        Print.red(disableStringIn)
    else:
        Print.green(enableStringIn)
    return not settingIn


def intVerifier(stringIn):
    TypeCheck.enforce(stringIn, Types.STRING)
    try:
        return [int(stringIn), True]
    except:
        return [stringIn, False]


def floatVerifier(stringIn):
    TypeCheck.enforce(stringIn, Types.STRING)
    try:
        return [float(stringIn), True]
    except:
        return [stringIn, False]


def imageSizeVerifier(stringIn):
    TypeCheck.enforce(stringIn, Types.STRING)
    sizes = stringIn.split("x")
    if len(sizes) == 2:
        width = sizes[0]
        height = sizes[1]
        if intVerifier(width)[1] and intVerifier(height)[1]:
            if int(width) % 8 == 0 and int(height) % 8 == 0:
                return [stringIn, True]
    return [stringIn, False]


def getDateTimeString():
    return DateTime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def getReadableDateTimeString():
    return DateTime.datetime.now().strftime("%A, %B %d, %Y - %H:%M:%S")


def getTimeString():
    return DateTime.datetime.now().strftime("%H:%M:%S")


__tic = Time.perf_counter()
__tick = Time.perf_counter()


def startTimer(timerNumber):
    global __tic, __tick
    TypeCheck.enforce(timerNumber, Types.INTEGER)
    match timerNumber:
        case 0: __tic = Time.perf_counter()     # foreground process timer
        case 1: __tick = Time.perf_counter()    # tests timer
        case _: printError("Unknown start timer: " + str(timerNumber))
    return


def endTimer(timerNumber):
    global __tic, __tick
    TypeCheck.enforce(timerNumber, Types.INTEGER)
    toc = Time.perf_counter()
    stringFormat = ""
    match timerNumber:
        case 0: stringFormat += f"Prompt processing time: {toc - __tic:0.3f}"
        case 1: stringFormat += f"Test time: {toc - __tick:0.3f}"
        case _:
            printError("Unknown end timer: " + str(timerNumber))
            return
    stringFormat += " seconds"
    printDebug(stringFormat)
    return
