# modules.util


import datetime as DateTime
import difflib as DiffLib
import json as JSON
import pynput as Pynput
import random as Random
import re as Regex
import readline as ReadLine  # unused, but fixes keyboard arrow keys for inputs
import termcolor as TermColor
import time as Time


import modules.Configuration as Configuration
import modules.Print as Print
import modules.typecheck.TypeCheck as TypeCheck
import modules.typecheck.Types as Types



# TODO: Move this (to configuration?):
# Remap keybind here if necessary
__keybindStop = Pynput.keyboard.Key.f12


# __serverResponseTokens = [
#     "</s>",
#     "<|end_of_sentence|>",
#     "<|endoftext|>",
#     "<|im_end|>",
#     "<0x0A>"
# ]


# def getServerResponseTokens():
#     return __serverResponseTokens


__keybindStopName = str(__keybindStop).upper().split(".")[1]


def getKeybindStopName():
    return __keybindStopName


####################
""" BEGIN PRINTS """
####################


def printInput(titleIn):
    TypeCheck.check(titleIn, Types.STRING)
    Print.separator()
    result = input(titleIn + ": ")
    Print.separator()
    clearWindowIfAllowed()
    return result


def printInfo(stringIn):
    TypeCheck.check(stringIn, Types.STRING)
    if Configuration.getConfig("debug_level") >= 1:
        print(TermColor.colored(stringIn, "yellow"))
    return


def printDebug(stringIn):
    TypeCheck.check(stringIn, Types.STRING)
    if Configuration.getConfig("debug_level") >= 2:
        print(TermColor.colored(stringIn, Configuration.getConfig("debug_text_color")))
    return


def printDump(stringIn):
    TypeCheck.check(stringIn, Types.STRING)
    if Configuration.getConfig("debug_level") >= 3:
        print(TermColor.colored(stringIn, Configuration.getConfig("dump_text_color")))
    return


def printPromptHistory(promptHistoryIn):
    TypeCheck.check(promptHistoryIn, Types.LIST)
    printDump("\nCurrent conversation:")
    for item in promptHistoryIn:
        printDump("\n" + item["content"])
    return


def clearWindowIfAllowed():
    if Configuration.getConfig("clear_window_before_every_prompt"):
        Print.clear()
    return


def printYNQuestion(messageIn):
    TypeCheck.check(messageIn, Types.STRING)
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
                Print.generic("\nInvalid option - assuming \"No\".\n")
                return 1
    return None


def printMenu(titleIn, descriptionIn, choicesIn):
    TypeCheck.check(titleIn, Types.STRING)
    TypeCheck.check(descriptionIn, Types.STRING)
    TypeCheck.check(choicesIn, Types.LIST)
    Print.generic("\n" + titleIn + ":\n")
    if len(descriptionIn) > 0:
        Print.generic(descriptionIn + "\n")
    i = 0
    for c in choicesIn:
        Print.generic("  (" + str(i + 1) + ") " + c)
        i += 1
    # printGeneric("(Tip: Use quotes to insert literal numbers (e.g. '123' or \"123\")).\n")
    Print.generic("\n  (0) Exit\n")
    selection = printInput("Select item")
    escaped = False
    if "\"" in selection or "'" in selection:
        escaped = True
        selection = selection.replace("\"", "")
        selection = selection.replace("'", "")
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
        Print.generic("\nQuotes in input - escaped from numerical options.\n")
    return selection


def printCurrentSystemPrompt(printerIn, spaceIn):
    TypeCheck.check(printerIn, Types.FUNCTION)
    TypeCheck.check(spaceIn, Types.STRING)
    if printerIn is not None:
        systemPrompt = Configuration.getConfig("system_prompt")
        if len(systemPrompt) > 0:
            printerIn("  " + systemPrompt + spaceIn)
        else:
            printerIn("  (Empty)" + spaceIn)
    return


########################
""" BEGIN STRING OPS """
########################


blankCharacters = ["\f", "\n", "\r", "\t", "\v"]


def checkEmptyString(strIn):
    TypeCheck.checkList(strIn, [Types.STRING, Types.NONE])
    if strIn is None:
        return True
    else:
        blanks = blankCharacters + [" "]
        for s in strIn:
            if s not in blanks:
                return False
        return True


def checkStringHasCommand(strIn):
    TypeCheck.check(strIn, Types.STRING)
    return strIn.startswith("/")


def checkStringHasFile(strIn):
    TypeCheck.check(strIn, Types.STRING)
    return "'/" in strIn


def cleanupString(stringIn):
    TypeCheck.check(stringIn, Types.STRING)
    for char in blankCharacters: out = stringIn.replace(char, " ")  # remove all spaces
    out = " ".join(out.split())                                     # remove all redundant spaces
    # out = (out.encode("ascii", errors="ignore")).decode()           # drop all non-ascii chars
    return out


def cleanupServerResponseTokens(stringIn):
    TypeCheck.check(stringIn, Types.STRING)
    stringOut = stringIn
    # for s in __serverResponseTokens:
    #     stringOut = stringOut.replace(s, "")
    return stringOut


def trimTextBySentenceLength(textIn, maxLength):
    TypeCheck.check(textIn, Types.STRING)
    TypeCheck.check(maxLength, Types.INTEGER)
    i = 0               # char position
    j = 0               # sentences
    k = 0               # chars since last sentence
    flag = False        # deleted a "short" sentence this run
    m = 24              # "short" sentence chars threshold
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
    TypeCheck.check(arrayIn, Types.LIST)
    TypeCheck.check(separator, Types.STRING)
    return separator.join(str(s) for s in arrayIn)


def formatJSONToString(dictionaryIn):
    TypeCheck.check(dictionaryIn, Types.DICTIONARY)
    return JSON.dumps(dictionaryIn, indent=4)


def getGrammarString(listIn):
    TypeCheck.check(listIn, Types.LIST)
    grammarStringBuilder = "root ::= ("     # length is 10
    for item in listIn:
        if len(grammarStringBuilder) > 10:  # length from above
            grammarStringBuilder += " | "
        grammarStringBuilder += "\"" + item + "\""
    grammarStringBuilder += ")"
    return grammarStringBuilder


def errorBlankEmptyText(sourceIn):
    TypeCheck.check(sourceIn, Types.STRING)
    Print.error("The " + sourceIn + " is empty/blank!")
    return "The text received from the " + sourceIn + " is blank and/or empty."


def getRandomSeed():
    return Random.randrange(1, (2 ** 32) - 1)


def removeApostrophesFromFileInput(stringIn):
    TypeCheck.check(stringIn, Types.STRING)
    stringOut = stringIn.replace("' ", "")
    stringOut = stringIn.replace("'", "")
    return stringOut


def getStringMatchPercentage(sourceStringIn, targetStringIn):
    TypeCheck.check(sourceStringIn, Types.STRING)
    TypeCheck.check(targetStringIn, Types.STRING)
    return DiffLib.SequenceMatcher(None, sourceStringIn, targetStringIn).ratio() * 100


def getFilePathFromPrompt(stringIn):
    TypeCheck.check(stringIn, Types.STRING)
    return (Regex.findall(r"'(.*?)'", stringIn, Regex.DOTALL))


def replaceLast(stringIn, replaceTextIn, replacementTextIn):
    TypeCheck.check(stringIn, Types.STRING)
    TypeCheck.check(replaceTextIn, Types.STRING)
    TypeCheck.check(replacementTextIn, Types.STRING)
    stringOut = stringIn[::-1].replace(replaceTextIn[::-1], replacementTextIn[::-1], 1)[::-1]
    return stringOut


# Unused, maybe useful in the future
def padStringsToSameLength(stringListIn):
    TypeCheck.check(stringListIn, Types.LIST)
    longestStringLength = 0
    for s in stringListIn:
        if len(s) > longestStringLength:
            longestStringLength = len(s)
    for s in stringListIn:
        s = padStringToLength(s, longestStringLength)
    return stringListIn


def padStringToLength(stringIn, lengthIn):
    TypeCheck.check(stringIn, Types.STRING)
    TypeCheck.check(lengthIn, Types.INTEGER)
    while len(stringIn) < lengthIn:
        stringIn += " "
    return stringIn


########################
""" BEGIN MISC UTILS """
########################


def setOrDefault(promptIn, defaultValueIn, verifierFuncIn, keepDefaultValueStringIn, setValueStringIn, verifierErrorStringIn):
    TypeCheck.check(promptIn, Types.STRING)
    TypeCheck.check(verifierFuncIn, Types.FUNCTION)
    TypeCheck.check(keepDefaultValueStringIn, Types.STRING)
    TypeCheck.check(setValueStringIn, Types.STRING)
    TypeCheck.check(verifierErrorStringIn, Types.STRING)

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
    TypeCheck.check(promptIn, Types.STRING)
    TypeCheck.check(verifierFuncIn, Types.FUNCTION)
    TypeCheck.check(presetTypeStringIn, Types.STRING)
    TypeCheck.check(presetValueStringIn, Types.STRING)
    TypeCheck.check(verifierErrorStringIn, Types.STRING)

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
    TypeCheck.check(promptIn, Types.STRING)
    TypeCheck.check(verifierFuncIn, Types.FUNCTION)
    TypeCheck.check(presetTypeStringIn, Types.STRING)
    TypeCheck.check(presetValueStringIn, Types.STRING)
    TypeCheck.check(verifiedResultStringIn, Types.STRING)
    TypeCheck.check(verifierErrorStringIn, Types.STRING)

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
    TypeCheck.check(promptIn, Types.STRING)
    TypeCheck.check(leaveEmptyMessageIn, Types.STRING)
    TypeCheck.check(verifierFuncIn, Types.FUNCTION)
    TypeCheck.check(noResultMessageIn, Types.STRING)
    TypeCheck.check(verifiedResultMessageIn, Types.STRING)
    TypeCheck.check(verifierErrorMessageIn, Types.STRING)

    if promptIn is not None and leaveEmptyMessageIn is not None and valueIn is not None and verifierFuncIn is not None and noResultMessageIn is not None and verifiedResultMessageIn is not None and verifierErrorMessageIn is not None:
        result = printInput(promptIn + " (" + leaveEmptyMessageIn + " \"" + str(valueIn) + "\")")
        if len(result) == 0:
            Print.red("\n" + noResultMessageIn + ": " + str(valueIn) + "\n")
            return valueIn
        else:
            verifiedResult = verifierFuncIn(result)
            if verifiedResult[1]:
                if len(verifiedResultMessageIn) > 0:
                    Print.green("\n" + verifiedResultMessageIn + ": " + str(verifiedResult[0]) + "\n")
                return verifiedResult[0]
            else:
                Print.error("\n" + verifierErrorMessageIn + ": " + str(valueIn) + "\n")
                return valueIn
    return None


def toggleSetting(settingIn, disableStringIn, enableStringIn):
    TypeCheck.check(settingIn, Types.BOOLEAN)
    TypeCheck.check(disableStringIn, Types.STRING)
    TypeCheck.check(enableStringIn, Types.STRING)
    if settingIn:
        Print.red("\n" + disableStringIn + "\n")
    else:
        Print.green("\n" + enableStringIn + "\n")
    return not settingIn


def intVerifier(stringIn):
    TypeCheck.check(stringIn, Types.STRING)
    try:
        return [int(stringIn), True]
    except:
        return [stringIn, False]


def floatVerifier(stringIn):
    TypeCheck.check(stringIn, Types.STRING)
    try:
        return [float(stringIn), True]
    except:
        return [stringIn, False]


def imageSizeVerifier(stringIn):
    TypeCheck.check(stringIn, Types.STRING)
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
    TypeCheck.check(timerNumber, Types.INTEGER)
    match timerNumber:
        case 0:  # foreground process timer
            global tic
            tic = Time.perf_counter()
        case 1:  # tests timer
            global tick
            tick = Time.perf_counter()
        case _:
            Print.error("\nUnknown start timer: " + str(timerNumber))
    return


def endTimer(timerNumber):
    TypeCheck.check(timerNumber, Types.INTEGER)
    toc = Time.perf_counter()
    stringFormat = "\n"
    match timerNumber:
        case 0:
            stringFormat += f"Prompt processing time: {toc - tic:0.3f}"
        case 1:
            stringFormat += f"Test time: {toc - tick:0.3f}"
        case _:
            Print.error("\nUnknown end timer: " + str(timerNumber))
            return
    stringFormat += " seconds"
    printDebug(stringFormat)
    return


def keyListener(key):
    global __shouldInterruptCurrentOutputProcess

    if key == __keybindStop:
        if not __shouldInterruptCurrentOutputProcess:
            __shouldInterruptCurrentOutputProcess = True
            Print.generic("")
            Print.separator()
            Print.red("[" + __keybindStopName + "] pressed - waiting for process to complete then exiting...")
            Print.separator()
            Print.generic("")
    return


__shouldInterruptCurrentOutputProcess = True


def setShouldInterruptCurrentOutputProcess(shouldInterrupt):
    TypeCheck.check(shouldInterrupt, Types.BOOLEAN)
    global __shouldInterruptCurrentOutputProcess
    __shouldInterruptCurrentOutputProcess = shouldInterrupt
    return


def getShouldInterruptCurrentOutputProcess():
    return __shouldInterruptCurrentOutputProcess
