# package modules


import json as JSON
import re as Regex


import modules.core.Configuration as Configuration
import modules.core.file.Operation as Operation
import modules.core.file.Reader as Reader
import modules.core.typecheck.TypeCheck as TypeCheck
import modules.core.typecheck.Types as Types
import modules.core.Util as Util
import modules.string.Path as Path
import modules.Web as Web


__triggerCommand = "/"
__triggerYoutube = []
__triggerBrowse = []
__triggerOpenFile = []


def loadConfiguration():
    global __triggerCommand, __triggerYoutube, __triggerBrowse, __triggerOpenFile
    triggerConfig = Operation.readFile(Path.CONFIGS_TRIGGER_FILE_NAME, None, False)
    if triggerConfig is not None:
        j = JSON.loads(triggerConfig)
        __triggerCommand = j.get("trigger_command")
        __triggerYoutube = j.get("trigger_youtube")
        __triggerBrowse = j.get("trigger_browse")
        __triggerOpenFile = j.get("trigger_openfile")
    return


def checkStringHasCommand(stringIn):
    global __triggerCommand
    TypeCheck.enforce(stringIn, Types.STRING)
    forbidden = [".", "_", "/", " ", "-", "~", "\"", "'"]
    if __triggerCommand in forbidden:
        forbidden.remove(__triggerCommand)
    for f in forbidden:
        if f in stringIn:
            return False
    if len(stringIn.split(__triggerCommand)) > 2:
        return False
    return stringIn.startswith(__triggerCommand)


def checkStringHasFile(stringIn):
    global __triggerOpenFile
    TypeCheck.enforce(stringIn, Types.STRING)
    for t in __triggerOpenFile:
        if t in stringIn:
            return True
    words = stringIn.split(" ")
    for w in words:
        if w.startswith("~/"):
            return True
        elif w.startswith("/"):
            w2 = w.split("/")
            if len(w2) > 0:
                return True
            elif "." in w2[-1]:
                return True
    return False


def checkTriggers(promptIn):
    TypeCheck.enforce(promptIn, Types.STRING)

    promptOut = [promptIn]
    triggerHasRan = False

    while True:
        potentialTriggers = {}
        for key, value in __getTriggerMap().items():
            for v in value:
                if v in promptOut[0]:
                    potentialTriggers[key] = Util.getStringMatchPercentage(v, promptOut[0])
        if len(potentialTriggers) == 1:
            triggerHasRan = True
            triggerToCall = list(potentialTriggers)[0]
            Util.printDebug("Calling trigger: " + str(triggerToCall))
            result = triggerToCall(promptOut[0])
            if result is not None:
                promptOut[0] = result[0]
                for data in result[1]:
                    promptOut.append(data)
            else:
                Util.printError("No result for this trigger - stopping trigger detection.")
                break
        elif len(potentialTriggers) > 1:
            triggerHasRan = True
            triggerToCall = None
            for trigger, percentage in potentialTriggers.items():
                if triggerToCall is None:
                    triggerToCall = trigger
                elif percentage > potentialTriggers[triggerToCall]:
                    triggerToCall = trigger
            Util.printDebug(f"Calling best-matched trigger: {str(triggerToCall)}")
            result = triggerToCall(promptOut[0])
            if result is not None:
                promptOut[0] = result[0]
                for data in result[1]:
                    promptOut.append(data)
        else:
            if triggerHasRan:   Util.printDebug("No more triggers detected.")
            else:               Util.printDebug("No triggers detected.")
            break
    return promptOut  # [prompt, data1, data2, ...]


def checkForYoutube(linkIn):
    TypeCheck.enforce(linkIn, Types.STRING)
    for youtubeFormat in __getTriggerMap()[triggerYouTube]:
        if linkIn.startswith(youtubeFormat):
            videoId = linkIn.replace(youtubeFormat, "")
            return Web.getYouTubeCaptions(videoId)
    return None


def triggerYouTube(promptIn):
    TypeCheck.enforce(promptIn, Types.STRING)
    promptWithoutWebsites = promptIn
    youtubeTranscripts = []
    videoCounter = 1
    for s in promptIn.split(" "):
        youtubeResult = checkForYoutube(s)
        if youtubeResult is not None:
            promptWithoutWebsites = promptWithoutWebsites.replace(s, "")
            youtubeTranscripts.append(
                "\n``` Video " + str(videoCounter) + " (" + s + ")"
                "\n" + youtubeResult + "\n"
                "```\n"
            )
            videoCounter += 1
    return [promptWithoutWebsites, youtubeTranscripts]  # [prompt, [data1, data2, ...]]


def triggerBrowse(promptIn):
    TypeCheck.enforce(promptIn, Types.STRING)
    promptOut = promptIn
    websiteTexts = []
    for s in promptOut.split(" "):
        if "http://" in s or "https://" in s:
            promptOut = promptOut.replace(s, "")
            youtubeResult = checkForYoutube(s)
            if youtubeResult is not None:
                websiteTitle = "YouTube Video"
                websiteText = youtubeResult
            else:
                website = Web.getSourceText(s, True, 0)
                websiteTitle = website[1]
                websiteText = website[2]
                if websiteTitle is None or websiteText is None or Util.checkEmptyString(websiteText):
                    websiteTitle = "Error accessing webpage"
                    websiteText = Util.errorBlankEmptyText("website")
                websiteTexts.append(
                    "\n``` Website \"" + websiteTitle + "\" (" + s + ")"
                    "\n" + websiteText + "\n"
                    "```\n"
                )
    return [promptOut, websiteTexts]  # [prompt, [data1, data2, ...]]


def triggerOpenFile(promptIn):
    TypeCheck.enforce(promptIn, Types.STRING)
    promptWithoutFilePaths = promptIn
    filePathsInPrompt = Util.getFilePathFromPrompt(promptIn)
    fileContents = []
    detectedWebsites = []
    promptPreset = ""
    for filePath in filePathsInPrompt:
        if "/" in filePath:
            #formattedFilePath = "'" + filePath + "'"
            #if " " + formattedFilePath in promptWithoutFilePaths:
            #    promptWithoutFilePaths = promptWithoutFilePaths.replace(" " + formattedFilePath, "")
            #elif formattedFilePath + " " in promptWithoutFilePaths:
            #    promptWithoutFilePaths = promptWithoutFilePaths.replace(formattedFilePath + " ", "")
            #else:
            #    promptWithoutFilePaths = promptWithoutFilePaths.replace(formattedFilePath, "")
            promptWithoutFilePaths = promptWithoutFilePaths.replace(filePath, "")
            if not filePath.endswith(".prompt"):
                filePaths = []
                shouldUseFilePathsAsNames = False
                if Operation.folderExists(filePath):
                    pathTree = Operation.getPathTree(filePath)
                    filePaths = pathTree
                    shouldUseFilePathsAsNames = True
                    Util.printDebug(f"Opening folder: {filePath}")
                    Util.printDebug("Files in folder: ")
                    Util.printDebug(Util.formatArrayToString(pathTree, ""))
                else:
                    filePaths = [filePath]
                for f in filePaths:
                    fullFileName = f.split("/")
                    fileName = fullFileName[len(fullFileName) - 1]
                    Util.printDebug(f"Parsing file: {f}")
                    fileContent = Reader.getFileContents(f, False, promptIn=promptIn)
                    if fileContent is not None:
                        if Util.checkEmptyString(fileContent):
                            fileContent = Util.errorBlankEmptyText("file")
                        else:
                            if not Configuration.getConfig("enable_internet"):
                                Util.printDebug("Internet is disabled - skipping embedded website check.")
                            else:
                                # check for websites in file
                                words = Regex.split(' |\n|\r|\)|\]|\}|\>', fileContent)
                                for word in words:
                                    if word.startswith("http://") or word.startswith("https://"):
                                        detectedWebsites.append(word)
                                        Util.printDebug(f"Found website in file: {word}")
                        Util.printDump(f"File content: {fileContent}")
                        if shouldUseFilePathsAsNames:
                            fileContents.append(
                                "\n``` File \"" + f + "\""
                                "\n" + fileContent + "\n"
                                "```\n"
                            )
                        else:
                            fileContents.append(
                                "\n``` File \"" + fileName + "\""
                                "\n" + fileContent + "\n"
                                "```\n"
                            )
                        if len(detectedWebsites) > 0:
                            for website in detectedWebsites:
                                youtubeResult = checkForYoutube(website)
                                if youtubeResult is not None:
                                    websiteTitle = "YouTube Video"
                                    websiteText = youtubeResult
                                else:
                                    web = Web.getSourceText(website, True, 0)
                                    websiteTitle = web[1]
                                    websiteText = web[2]
                                    if not Util.checkEmptyString(websiteText):
                                        Util.printDebug(f"Retrieved text from: {website}")
                                        Util.printDump(f"Website text: {websiteText}")
                                if shouldUseFilePathsAsNames:
                                    fileContents.append(
                                        "\n``` Website in file \"" + f + "\" [" + websiteTitle + " (" + website + ")]"
                                        "\n" + websiteText + "\n"
                                        "```\n"
                                    )
                                else:
                                    fileContents.append(
                                        "\n``` Website in file \"" + fileName + "\" [" + websiteTitle + " (" + website + ")]"
                                        "\n" + websiteText + "\n"
                                        "```\n"
                                    )
                    else:
                        Util.printError("Cannot get file contents.")
                        return None
            else:
                Util.printDebug("Found a prompt file.")
                promptPreset = Reader.getFileContents(filePath, False).strip()
                Util.printDebug(f"Prompt in file: {promptPreset}")
        else:
            Util.printDebug(f"File skipped it is missing a slash: {filePath}")
    if len(promptPreset) > 0:
        return [promptPreset, fileContents]
    else:
        return [promptWithoutFilePaths, fileContents]


def __getTriggerMap():
    return {
        triggerYouTube: __triggerYoutube,
        triggerBrowse: __triggerBrowse,
        triggerOpenFile: __triggerOpenFile,
    }
