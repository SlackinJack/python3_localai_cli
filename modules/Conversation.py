# package modules


import modules.core.file.Operation as Operation
import modules.core.typecheck.TypeCheck as TypeCheck
import modules.core.typecheck.Types as Types
import modules.core.Util as Util
import modules.string.Path as Path


def getRandomConversationName():
    return Util.getDateTimeString()


__strConvoTimestamp = getRandomConversationName()
__strConvoName = __strConvoTimestamp


def writeConversation(convoNameIn, strIn):
    TypeCheck.check(convoNameIn, Types.STRING)
    TypeCheck.check(strIn, Types.STRING)
    content = Util.cleanupString(strIn)
    Operation.appendFile(Path.CONVERSATIONS_FILE_PATH + convoNameIn + ".convo", content + "\n")
    return


def getConversation(convoNameIn):
    TypeCheck.check(convoNameIn, Types.STRING)
    out = Operation.readFile(Path.CONVERSATIONS_FILE_PATH + convoNameIn + ".convo", "\n", True)
    out = Util.cleanupString(out)
    return out


def setConversation(fileNameIn):
    TypeCheck.check(fileNameIn, Types.STRING)
    global __strConvoName
    fileName = Path.CONVERSATIONS_FILE_PATH + fileNameIn + ".convo"
    Operation.writeFile(fileName)
    __strConvoName = fileNameIn
    return


def getConversationName():
    return __strConvoName


def getRoleAndContentFromString(stringIn):
    TypeCheck.check(stringIn, Types.STRING)
    if len(stringIn) > 0:
        i = 0
        for s in stringIn:
            if ":" in s:
                return [stringIn[0:i], stringIn[i + 2:len(stringIn)]]
            else:
                i += 1
    if len(stringIn) > 0:
        Util.printDebug("\nThe following string is not in a valid role:content form: \"" + stringIn + "\"\n")
    return None


def addToPrompt(promptListIn, roleIn, contentIn, chatFormatIn, isPromptEnding=False):
    TypeCheck.check(promptListIn, Types.LIST)
    TypeCheck.check(roleIn, Types.STRING)
    TypeCheck.check(contentIn, Types.STRING)
    TypeCheck.check(chatFormatIn, Types.STRING)
    TypeCheck.check(isPromptEnding, Types.BOOLEAN)

    line = ""
    match chatFormatIn:
        case "alpaca":
            line += roleIn.upper() + ": " + contentIn
        case "chatml":
            line += "<|im_start|>" + roleIn + "\n" + contentIn
            if not isPromptEnding:
                line += "<|im_end|>"
        case "deepseek":
            if (len(promptListIn) == 0 and roleIn != "user") or (len(promptListIn) == 0 and not isPromptEnding and roleIn == "user"):
                line += "<｜begin▁of▁sentence｜>"
            elif isPromptEnding:
                promptListLength = len(promptListIn)
                if promptListLength - 2 > -1:
                    secondLastIndex = len(promptListIn) - 2
                    promptListIn[secondLastIndex]["content"] += "<｜end▁of▁sentence｜>"
            modifiedRole = roleIn[0].upper() + roleIn[1:len(roleIn)]
            line += "<｜" + modifiedRole + "｜>" + contentIn
        case _:
            line += contentIn

    promptListIn.append({ "role": roleIn, "content": line })
    return promptListIn


def getPromptHistoryFromConversation(conversationIn, chatFormat):
    TypeCheck.check(conversationIn, Types.LIST)
    TypeCheck.check(chatFormat, Types.STRING)
    promptHistory = []
    stringBuilder = ""
    for line in conversationIn:
        if line.startswith("SYSTEM: ") or line.startswith("USER: ") or line.startswith("ASSISTANT: "):
            if len(stringBuilder) == 0:
                stringBuilder += line
            else:
                s = getRoleAndContentFromString(stringBuilder)
                if s is not None:
                    promptHistory = addToPrompt(promptHistory, s[0].lower(), s[1], chatFormat)
                stringBuilder = line
        else:
            stringBuilder += line
    s = getRoleAndContentFromString(stringBuilder)
    if s is not None:
        promptHistory = addToPrompt(promptHistory, s[0].lower(), s[1], chatFormat)
    return promptHistory
