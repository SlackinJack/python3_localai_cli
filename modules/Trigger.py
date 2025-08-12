# modules.util


import json as JSON
import re as Regex


import modules.Configuration as Configuration
import modules.file.Operation as Operation
import modules.file.Reader as Reader
import modules.Print as Print
import modules.string.Path as Path
import modules.typecheck.TypeCheck as TypeCheck
import modules.typecheck.Types as Types
import modules.Util as Util
import modules.Web as Web


__triggerYoutube = []
__triggerBrowse = []
__triggerOpenFile = []


def __getTriggerConfiguration():
    global __triggerYoutube, __triggerBrowse, __triggerOpenFile
    triggerConfig = Operation.readFile(Path.CONFIGS_TRIGGER_FILE_NAME, None, False)
    if triggerConfig is not None:
        j = JSON.loads(triggerConfig)
        __triggerYoutube = j.get("trigger_youtube")
        __triggerBrowse = j.get("trigger_browse")
        __triggerOpenFile = j.get("trigger_openfile")
    return


__getTriggerConfiguration()


def checkTriggers(promptIn):
    TypeCheck.check(promptIn, Types.STRING)

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
            Util.printDebug("\nCalling trigger: " + str(triggerToCall))
            result = triggerToCall(promptOut[0])
            if result is not None:
                promptOut[0] = result[0]
                for data in result[1]:
                    promptOut.append(data)
            else:
                Util.printError("\nNo result for this trigger - stopping trigger detection.\n")
                break
        elif len(potentialTriggers) > 1:
            triggerHasRan = True
            triggerToCall = None
            for trigger, percentage in potentialTriggers.items():
                if triggerToCall is None:
                    triggerToCall = trigger
                elif percentage > potentialTriggers[triggerToCall]:
                    triggerToCall = trigger
            Util.printDebug("\nCalling best-matched trigger: " + str(triggerToCall))
            result = triggerToCall(promptOut[0])
            if result is not None:
                promptOut[0] = result[0]
                for data in result[1]:
                    promptOut.append(data)
        else:
            if triggerHasRan:
                Util.printDebug("\nNo more triggers detected.")
            else:
                Util.printDebug("\nNo triggers detected.")
            break
    return promptOut  # [prompt, data1, data2, ...]


def checkForYoutube(linkIn):
    TypeCheck.check(linkIn, Types.STRING)
    for youtubeFormat in __getTriggerMap()[triggerYouTube]:
        if linkIn.startswith(youtubeFormat):
            videoId = linkIn.replace(youtubeFormat, "")
            return Web.getYouTubeCaptions(videoId)
    return None


def triggerYouTube(promptIn):
    TypeCheck.check(promptIn, Types.STRING)
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
    TypeCheck.check(promptIn, Types.STRING)
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
    TypeCheck.check(promptIn, Types.STRING)
    promptWithoutFilePaths = promptIn
    filePathsInPrompt = Util.getFilePathFromPrompt(promptIn)
    fileContents = []
    detectedWebsites = []
    promptPreset = ""
    for filePath in filePathsInPrompt:
        if "/" in filePath:
            formattedFilePath = "'" + filePath + "'"
            if " " + formattedFilePath in promptWithoutFilePaths:
                promptWithoutFilePaths = promptWithoutFilePaths.replace(" " + formattedFilePath, "")
            elif formattedFilePath + " " in promptWithoutFilePaths:
                promptWithoutFilePaths = promptWithoutFilePaths.replace(formattedFilePath + " ", "")
            else:
                promptWithoutFilePaths = promptWithoutFilePaths.replace(formattedFilePath, "")
            if not filePath.endswith(".prompt"):
                filePaths = []
                shouldUseFilePathsAsNames = False
                if Operation.folderExists(filePath):
                    pathTree = Operation.getPathTree(filePath)
                    filePaths = pathTree
                    shouldUseFilePathsAsNames = True
                    Util.printDebug("\nOpening folder: " + filePath)
                    Util.printDebug("\nFiles in folder:")
                    Util.printDebug(Util.formatArrayToString(pathTree, "\n"))
                else:
                    filePaths = [filePath]
                for f in filePaths:
                    fullFileName = f.split("/")
                    fileName = fullFileName[len(fullFileName) - 1]
                    Util.printDebug("\nParsing file: " + fileName)
                    fileContent = Reader.getFileContents(f, False)
                    if fileContent is not None:
                        if Util.checkEmptyString(fileContent):
                            fileContent = Util.errorBlankEmptyText("file")
                        else:
                            if not Configuration.getConfig("enable_internet"):
                                Util.printDebug("\nInternet is disabled - skipping embedded website check.")
                            else:
                                # check for websites in file
                                words = Regex.split(" |\n|\r|)|]|}|>", fileContent)
                                for word in words:
                                    if word.startswith("http://") or word.startswith("https://"):
                                        detectedWebsites.append(word)
                                        Util.printDebug("\nFound website in file: " + word + "\n")
                        Util.printDump("\nFile content: " + fileContent + "\n")
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
                                        Util.printDebug("\nRetrieved text from " + website)
                                        Util.printDump("\nWebsite text: " + websiteText + "\n")
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
                        Util.printError("\nCannot get file contents.\n")
                        return None
            else:
                Util.printDebug("\nFound a prompt file.")
                promptPreset = Reader.getFileContents(filePath, False).strip()
                Util.printDebug("\nPrompt: " + promptPreset)
        else:
            Util.printDebug("\nSkipped \"" + filePath + "\" because it did not contain \"/\" - assuming invalid file path.")
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
