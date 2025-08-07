# modules.connection.response


import json as JSON
import sys as System
import time as Time


import modules.connection.request.TextToText as TextToText
import modules.connection.response.TextToAudio as TextToAudio
import modules.connection.response.TextToImage as TextToImage
import modules.file.Operation as Operation
import modules.file.Reader as Reader
import modules.string.Path as Path
import modules.string.Prompt as Prompt
import modules.Configuration as Configuration
import modules.Conversation as Conversation
import modules.Model as Model
import modules.Print as Print
import modules.typecheck.TypeCheck as TypeCheck
import modules.typecheck.Types as Types
import modules.Util as Util
import modules.Web as Web


# Add custom stopwords here as necessary
# __stopwords = ["\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"] + Util.getServerResponseTokens()


def __printTokenUsage(startTimeIn, endTimeIn, tokensIn):
    if startTimeIn is not None and endTimeIn is not None and tokensIn is not None and tokensIn["prompt_tokens"] > 0:
        totalTime = endTimeIn - startTimeIn
        compTokens = tokensIn["completion_tokens"]
        compTokenTime = compTokens / totalTime
        promptTokens = tokensIn["prompt_tokens"]
        totalTokens = tokensIn["total_tokens"]
        totalTokenTime = totalTokens / totalTime
        Util.printDebug(f"""
Stats:
Prompt Tokens: {promptTokens}
Completion/Total Time: {compTokenTime:0.3f}t/s ({compTokens}t/{totalTime:0.3f}s)
All/Total Time: {totalTokenTime:0.3f}t/s ({totalTokens}t/{totalTime:0.3f}s)""")
    return


# Uses OpenAI API
def getTextToTextResponseStreamed(promptIn, seedIn, dataIn, shouldWriteDataToConvo, isReprompt, proposedAnswerIn):
    TypeCheck.check(promptIn, Types.STRING)
    TypeCheck.check(seedIn, Types.INTEGER)
    TypeCheck.check(dataIn, Types.LIST)
    TypeCheck.check(shouldWriteDataToConvo, Types.BOOLEAN)

    if len(Configuration.getConfig("default_text_to_text_model")) == 0:
        Print.error("\nText-to-Text is disabled because the Text-to-Text model is not set.\n")
        return None

    currentConversationName = Conversation.getConversationName()

    nextModel = getTextToTextResponseModel(promptIn, seedIn)
    if nextModel is not None and nextModel is not Configuration.getConfig("default_text_to_text_model"):
        Configuration.setConfig("default_text_to_text_model", nextModel)

    chatFormat = Model.getChatModelFormat(Configuration.getConfig("default_text_to_text_model"))

    promptHistory = []
    if Configuration.getConfig("enable_chat_history_consideration"):
        conversation = Conversation.getConversation(currentConversationName)
        promptHistory = Conversation.getPromptHistoryFromConversation(conversation, chatFormat)

    if len(dataIn) > 0:
        # systemContent = Prompt.getRespondUsingInformationPrompt() + Util.formatArrayToString(dataIn, "\n\n")
        # promptHistory = Conversation.addToPrompt(promptHistory, "system", systemContent, chatFormat)
        for data in dataIn:
            promptHistory = Conversation.addToPrompt(promptHistory, "system", Prompt.getRespondUsingInformationPrompt() + data, chatFormat)

    systemPromptOverride = Model.getChatModelPromptOverride(Configuration.getConfig("default_text_to_text_model"))
    if systemPromptOverride is not None:
        if isReprompt:
            Util.printDebug("\nUsing overridden system prompt with reprompt.")
            promptHistory = Conversation.addToPrompt(promptHistory, "system", systemPromptOverride + Prompt.getRepromptSystemPrompt(proposedAnswerIn), chatFormat)
        else:
            Util.printDebug("\nUsing overridden system prompt.")
            promptHistory = Conversation.addToPrompt(promptHistory, "system", systemPromptOverride, chatFormat)
    elif len(Configuration.getConfig("system_prompt")) > 0:
        if isReprompt:
            Util.printDebug("\nUsing configuration system prompt with reprompt.")
            promptHistory = Conversation.addToPrompt(promptHistory, "system", Configuration.getConfig("system_prompt") + Prompt.getRepromptSystemPrompt(proposedAnswerIn), chatFormat)
        else:
            Util.printDebug("\nUsing configuration system prompt.")
            promptHistory = Conversation.addToPrompt(promptHistory, "system", Configuration.getConfig("system_prompt"), chatFormat)
    elif isReprompt:
        Util.printDebug("\nUsing reprompt system prompt.")
        promptHistory = Conversation.addToPrompt(promptHistory, "system", Prompt.getRepromptSystemPrompt(proposedAnswerIn), chatFormat)
    else:
        Util.printInfo("\nNot using a system prompt.")
    promptHistory = Conversation.addToPrompt(promptHistory, "user", promptIn, chatFormat)
    promptHistory = Conversation.addToPrompt(promptHistory, "assistant", "", chatFormat, isPromptEnding=True)
    Util.printPromptHistory(promptHistory)

    assistantResponse = ""
    completion = TextToText.createOpenAITextToTextRequest(
        {
            "model": Configuration.getConfig("default_text_to_text_model"),
            "messages": promptHistory,
            "seed": seedIn,
        }
    )
    if completion is not None:
        # pausedLetters = {}
        # stop = False
        startTime = None
        prematureTermination = False
        Util.setShouldInterruptCurrentOutputProcess(False)
        tokens = None
        try:
            Print.response("", "\n")
            for chunk in completion:  # L1
                if not Util.getShouldInterruptCurrentOutputProcess():
                    letter = chunk.choices[0].delta.content
                    if letter is not None:
                        if startTime is None:
                            startTime = Time.perf_counter()
                        # pause = False
                        # for stopword in __stopwords:
                        #     if len(letter) >= 1 and stopword.startswith(letter):
                        #         if pausedLetters.get(stopword) is None:
                        #             pausedLetters[stopword] = ""
                        # for stopword in list(pausedLetters.keys()):  # L2
                        #     index = len(pausedLetters[stopword])
                        #     if stopword[index] == letter:
                        #         pause = True
                        #         pausedLetters[stopword] += letter
                        #         if stopword in pausedLetters[stopword]:
                        #             Util.printDebug("\nStopword reached: \"" + pausedLetters[stopword] + "\"\n")
                        #             stop = True
                        #             break  # L2
                        # if len(pausedLetters) == 0:
                        #     pause = False
                        # if not stop and not pause:
                        #     if len(pausedLetters) > 0:
                        #         longestPause = ""
                        #         for paused in list(pausedLetters.keys()):
                        #             pausedPhrase = pausedLetters[paused]
                        #             if len(longestPause) <= len(pausedPhrase):
                        #                 longestPause = pausedPhrase
                        #             del pausedLetters[paused]
                        #         Print.response(longestPause, "")
                        #         assistantResponse += longestPause
                        #     Print.response(letter, "")
                        #     Time.sleep(Configuration.getConfig("print_delay"))
                        #     System.stdout.flush()
                        #     assistantResponse += letter
                        # elif stop:
                        #     Util.printDebug("\nStopping output because stopword reached: \"" + pausedLetters[stopword] + "\"\n")
                        #     break  # L1
                        Print.response(letter, "")
                        Time.sleep(Configuration.getConfig("print_delay"))
                        System.stdout.flush()
                        assistantResponse += letter
                    else:
                        Util.printDebug("\nLetter is None - breaking loop.\n")
                        break  # L1
                else:
                    prematureTermination = True
                    Util.printDebug("\nStopped output.\n")
                    break  # L1
            if chunk["usage"] is not None:
                tokens = chunk["usage"]
        except Exception as e:
            Print.error("\nAn error occurred during server output:\n" + str(e))
        Util.setShouldInterruptCurrentOutputProcess(True)
        endTime = Time.perf_counter()
        Print.response("", "\n")
        __printTokenUsage(startTime, endTime, tokens)

        assistantResponseString = assistantResponse.replace("ASSISTANT: ", "").replace("SYSTEM: ", "")
        if prematureTermination:
            assistantResponseString += "... [TRUNCATED]"
        noReprompt = False
        if isReprompt and assistantResponseString == proposedAnswerIn:
            Util.printInfo("\nThe currently-proposed answer is the same as the last-proposed answer - breaking reprompt loop.")
            noReprompt = True
        if Configuration.getConfig("do_reprompts") and not noReprompt:
            repromptHistory = []
            shouldRepromptMessage = Conversation.addToPrompt(repromptHistory, "system", Prompt.getShouldRepromptSystemPrompt(), chatFormat)
            shouldRepromptMessage = Conversation.addToPrompt(shouldRepromptMessage, "user", promptIn, chatFormat)
            shouldRepromptMessage = Conversation.addToPrompt(shouldRepromptMessage, "assistant", assistantResponseString, chatFormat)

            shouldRepromptStartTime = Time.perf_counter()
            shouldRepromptResult = TextToText.createTextToTextRequest(
                {
                    "model": Configuration.getConfig("default_text_to_text_model"),
                    "messages": shouldRepromptMessage,
                    "seed": seedIn,
                    "grammar": Util.getGrammarString(["yes", "no"]),
                }
            )
            shouldRepromptEndTime = Time.perf_counter()
            if shouldRepromptResult is not None:
                __printTokenUsage(shouldRepromptStartTime, shouldRepromptEndTime, shouldRepromptResult["usage"])
                if "n" in shouldRepromptResult["content"]:
                    Util.printInfo("\nRegenerating answer - this may infinitely loop!")
                    return getTextToTextResponseStreamed(promptIn, seedIn, dataIn, shouldWriteDataToConvo, True, assistantResponseString)
                else:
                    Util.printInfo("\nKeeping this answer.")
            else:
                Print.error("\nReprompt failed - using default answer.")

        if len(dataIn) > 0 and shouldWriteDataToConvo:
            # systemContent = "SYSTEM: " + Prompt.getRespondUsingInformationPrompt() + Util.formatArrayToString(dataIn, "\n\n")
            # Conversation.writeConversation(currentConversationName, systemContent)
            for data in dataIn:
                Conversation.writeConversation(currentConversationName, "SYSTEM: " + Prompt.getRespondUsingInformationPrompt() + data)

        Conversation.writeConversation(currentConversationName, "USER: " + promptIn)
        Conversation.writeConversation(currentConversationName, "ASSISTANT: " + assistantResponseString)

        if Configuration.getConfig("read_outputs"):
            Util.printInfo("\nGenerating Audio-to-Text...\n")
            response = TextToAudio.getTextToAudioResponse(assistantResponse, True)
            if response is not None:
                Util.printDebug("\nPlaying Audio-to-Text...\n")
                Reader.openLocalFile(response, "aplay -q -N", False)
            else:
                Print.error("\nCould not generate Audio-to-Text.\n")
        return assistantResponse
    else:
        Print.error("\nNo response from server.")

    return None


def function_action(actionsArray):
    return


def getTextToTextResponseFunctions(promptIn, seedIn, dataIn):
    TypeCheck.check(promptIn, Types.STRING)
    TypeCheck.check(seedIn, Types.INTEGER)
    TypeCheck.check(dataIn, Types.LIST)

    if len(Configuration.getConfig("default_text_to_text_model")) == 0:
        Print.error("\nText-to-Text is disabled because the Text-to-Text model is not set.\n")
        return None

    enums = [
        "SEARCH_INTERNET_WITH_SEARCH_TERM",
        "CREATE_IMAGE_WITH_DESCRIPTION",
        "WRITE_FILE_TO_FILESYSTEM"
    ]

    function = [
        {
            "name": "function_action",
            "parameters": {
                "type": "object",
                "properties": {
                    "actionsArray": {
                        "type": "array",
                        "description": Prompt.getFunctionActionsArrayDescription(enums),
                        "items": {
                            "type": "object",
                            "properties": {
                                "action": {
                                    "type": "string",
                                    "description": Prompt.getFunctionActionDescription(),
                                    "enum": enums,
                                },
                                "action_input_data": {
                                    "type": "string",
                                    "description":
                                        Prompt.getFunctionActionInputDataDescription(),
                                }
                            }
                        }
                    }
                }
            }
        }
    ]

    if Configuration.getConfig("enable_automatic_model_switching"):
        Configuration.resetDefaultTextModel()

    hrefs = []
    searchedTerms = []
    datas = dataIn
    promptHistory = []
    lastActionsArray = []
    firstRun = True
    lastAction = ""
    lastActionData = ""
    chatFormat = Model.getChatModelFormat(Configuration.getConfig("default_text_to_text_model"))

    # L1
    while True:
        if Configuration.getConfig("enable_chat_history_consideration"):
            conversation = Conversation.getConversation(Conversation.getConversationName())
            promptHistory = Conversation.getPromptHistoryFromConversation(conversation, chatFormat)

        if firstRun:
            firstRun = False
            prompt = Conversation.addToPrompt([], "system", Prompt.getFunctionSystemPrompt(enums), chatFormat)
        else:
            remainingActions = ""
            if len(lastActionsArray) > 0:
                formattedLastActionsArray = []
                for a in lastActionsArray:
                    formattedLastActionsArray.append(a["action"] + ": " + a["action_input_data"])
                remainingActions = Prompt.getRemainingActionsPrompt(formattedLastActionsArray)
            else:
                remainingActions = Prompt.getNoMoreActionsPrompt()
            # systemContent = Prompt.getRespondUsingInformationPrompt() + Util.formatArrayToString(datas, " ")
            # prompt = Conversation.addToPrompt([], "system", systemContent, chatFormat)
            prompt = []
            for data in datas:
                prompt = Conversation.addToPrompt(prompt, "system", Prompt.getRespondUsingInformationPrompt() + data, chatFormat)
            prompt = Conversation.addToPrompt(prompt, "system", Prompt.getFunctionEditSystemPrompt(enums), chatFormat)
            prompt = Conversation.addToPrompt(prompt, "system", remainingActions, chatFormat)

        prompt = Conversation.addToPrompt(prompt, "user", promptIn, chatFormat)
        fullPrompt = promptHistory + prompt
        Util.printPromptHistory(fullPrompt)
        Util.printDebug("\nDetermining function(s) to do for this prompt...")

        startTime = Time.perf_counter()
        result = TextToText.createTextToTextRequest(
            {
                "model": Configuration.getConfig("default_text_to_text_model"),
                "messages": fullPrompt,
                "seed": seedIn,
                "functions": function,
                "function_call": {
                    "name": "function_action",
                },
            }
        )
        endTime = Time.perf_counter()

        actionsResponse = None
        if result is not None:
            __printTokenUsage(startTime, endTime, result["usage"])
            if "function_call" in result:
                functionCall = result["function_call"]
                if "arguments" in functionCall:
                    actionsResponse = JSON.loads(functionCall["arguments"])
                else:
                    Print.error("\nNo arguments received from server.\n")
                    break  # L1
            else:
                if "content" in result and result["content"] is not None:
                    # Util.cleanupServerResponseTokens(result["content"])
                    resultJson = JSON.loads(result["content"])
                    if "arguments" in resultJson:
                        actionsResponse = resultJson["arguments"]
                    else:
                        Print.error("\nNo arguments received from server.\n")
                        break  # L1
                else:
                    Print.error("\nNo content received from server.\n")
                    break  # L1
        else:
            Print.error("\nNo response from server.")
            break  # L1

        if actionsResponse is not None and actionsResponse.get("actionsArray") is not None:
            actionsArray = actionsResponse.get("actionsArray")

            Util.printDebug("\nDetermined actions and input data:")

            if len(actionsArray) > 0 and len(actionsArray[0]) > 0:
                for action in actionsArray:
                    Util.printDebug(" - " + action.get("action") + ": " + action.get("action_input_data"))
            else:
                Util.printDebug("(None)")

            if len(actionsArray) > 0:
                action = actionsArray[0]
                theAction = action.get("action").upper()
                theActionInputData = action.get("action_input_data").lower()
                if theAction is not lastAction or theActionInputData is not lastActionData:
                    lastAction = theAction
                    lastActionData = theActionInputData
                    match theAction:

                        case "SEARCH_INTERNET_WITH_SEARCH_TERM":
                            actionResult = __actionSearchInternetWithSearchTerm(
                                theAction,
                                theActionInputData,
                                searchedTerms,
                                enums,
                                hrefs,
                                chatFormat,
                                seedIn,
                                datas
                            )
                            if not actionResult:
                                break #  L1
                            theAction, theActionInputData, searchedTerms, enums, hrefs, chatFormat, seedIn, datas = actionResult

                        case "CREATE_IMAGE_WITH_DESCRIPTION":
                            actionResult = __actionCreateImageWithDescription(theActionInputData, seedIn)
                            if not actionResult:
                                break #  L1

                        case "WRITE_FILE_TO_FILESYSTEM":
                            actionResult = __actionWriteFileToFilesystem(theActionInputData)
                            if not actionResult:
                                break #  L1

                        case _:
                            Print.error("\nUnrecognized action: " + action)

                    Util.printDebug("\nAction \"" + theAction + ": " + theActionInputData + "\" has completed successfully.")
                else:
                    Util.printDebug("\nThe action and data are the same as the last - exiting loop.\n")
                    break  # L1

                if len(actionsArray) >= 1:
                    lastActionsArray = actionsArray
                    lastActionsArray.pop(0)
                    Util.printDebug("\nReprompting model with action plan.")
                else:
                    Util.printDebug("\nThis was the last action in the action plan - exiting loop.")
                    break  # L1
            else:
                Util.printDebug("\nNo more actions in the action plan - exiting loop.")
                break  # L1
        else:
            Print.error("\nNo response from server - trying default chat completion.")
            return getTextToTextResponseStreamed(promptIn, seedIn, [], True, False, "")

    hasHref = len(hrefs) > 0
    if not hasHref:
        Util.printInfo("\nThis is an offline response!")

    response = getTextToTextResponseStreamed(promptIn, seedIn, datas, True, False, "")

    if response is not None:
        if hasHref:
            Print.response("\nSources analyzed:", "\n")
            for href in hrefs:
                Print.response(" - " + href, "\n")
    else:
        Print.error("\nNo response from server.")
    return response


def getTextToTextResponseModel(promptIn, seedIn):
    TypeCheck.check(promptIn, Types.STRING)
    TypeCheck.check(seedIn, Types.INTEGER)

    if len(Configuration.getConfig("default_text_to_text_model")) == 0:
        Print.error("\nText-to-Text is disabled because the Text-to-Text model is not set.\n")
        return None

    if not Configuration.getConfig("enable_automatic_model_switching"):
        return Configuration.getConfig("default_text_to_text_model")
    else:
        Util.printInfo("\nSwitching models - this may take a few seconds...")
        Configuration.resetDefaultTextModel()

        switchableModels = Model.getSwitchableTextModels()
        if len(switchableModels) == 0:
            Util.printDebug("\nNo switchable models - skipping model switcher.")
            return None
        elif len(switchableModels) == 1:
            nextModel = Model.getModelByNameAndType(switchableModels[0], "text_to_text", True, True, False)
            if nextModel is not None:
                Util.printDebug("\nOnly " + switchableModels[0] + " is enabled - using it and skipping model switcher.")
            else:
                Print.error("\nOnly " + switchableModels[0] + " is enabled, but cannot load model.")
            return nextModel
        else:
            chatFormat = Model.getChatModelFormat(Configuration.getConfig("default_text_to_text_model"))
            conversation = Conversation.getConversation(Conversation.getConversationName())
            promptHistory = Conversation.getPromptHistoryFromConversation(conversation, chatFormat)
            systemContent = Prompt.getDetermineBestAssistantPrompt() + Model.getSwitchableTextModelDescriptions()
            promptMessage = Conversation.addToPrompt(promptHistory, "system", systemContent, chatFormat)
            promptMessage = Conversation.addToPrompt(promptMessage, "user", promptIn, chatFormat)
            grammarString = Util.getGrammarString(switchableModels)

            Util.printDump("\nCurrent prompt for model response:")
            Util.printPromptHistory(promptMessage)
            Util.printDump("\nChoices: " + grammarString)

            startTime = Time.perf_counter()
            result = TextToText.createTextToTextRequest(
                {
                    "model": Configuration.getConfig("default_text_to_text_model"),
                    "messages": promptMessage,
                    "seed": seedIn,
                    "grammar": grammarString,
                }
            )
            endTime = Time.perf_counter()

            if result is not None:
                nextModel = Model.getModelByNameAndType(result["content"], "text_to_text", True, True, False)
                if nextModel is not None:
                    Util.printDebug("\nNext model: " + nextModel)
                else:
                    Print.error("\nNext model is determined but cannot be found: " + nextModel)
                __printTokenUsage(startTime, endTime, result["usage"])
                return nextModel
    return None


def __actionSearchInternetWithSearchTerm(theAction, theActionInputData, searchedTerms, enums, hrefs, chatFormat, seedIn, datas):
    if Configuration.getConfig("enable_internet"):
        if len(theActionInputData) > 0:
            if theActionInputData not in searchedTerms and theActionInputData.upper() not in enums:
                searchedTerms.append(theActionInputData)
                searchResultSources = Web.getSearchResults(theActionInputData, Configuration.getConfig("max_sources_per_search"))
                nonDuplicateHrefs = []
                for href in searchResultSources:
                    if href not in hrefs:
                        nonDuplicateHrefs.append(href)
                    else:
                        Util.printDebug("\nSkipped duplicate source: " + href)
                if len(nonDuplicateHrefs) > 0:
                    searchResults = Web.getSearchResultsTextAsync(nonDuplicateHrefs, Configuration.getConfig("max_sentences_per_source"))
                    if len(searchResults) > 0:
                        for key, value in searchResults.items():
                            if Configuration.getConfig("enable_source_condensing"):
                                Util.printDebug("\nCondensing source data: " + key)

                                startTimeInner = Time.perf_counter()
                                simplifiedData = TextToText.createTextToTextRequest(
                                    {
                                        "model": Configuration.getConfig("default_text_to_text_model"),
                                        "messages": Conversation.addToPrompt([], "system", Prompt.getCondenseSourceDataPrompt() + value, chatFormat),
                                        "seed": seedIn,
                                    }
                                )
                                endTimeInner = Time.perf_counter()
                                if simplifiedData is not None:
                                    simplifiedDataContent = simplifiedData["content"]
                                    Util.printDump("\nCondensed source data:\n" + simplifiedDataContent)
                                    hrefs.append(key)
                                    datas.append(simplifiedDataContent)
                                    Util.printDebug("\nAppended source data: " + key)
                                    __printTokenUsage(startTimeInner, endTimeInner, simplifiedData["usage"])
                                else:
                                    Util.printError("\nFailed to condense source: " + key)
                            else:
                                hrefs.append(key)
                                datas.append(value)
                                Util.printDebug("\nAppended source data: " + key)
                    else:
                        Print.error("\nNo search results with this search term.")
                else:
                    Util.printDebug("\nAll target links are duplicates - skipping this search.")
            else:
                Print.error("\nSkipping duplicated search term: " + theActionInputData)
                Print.error("\nExiting loop.")
                return False
        else:
            Print.error("\nNo search term provided.")
    else:
        Util.printDebug("\nInternet is disabled - skipping this action. (\"" + theAction + "\": " + theActionInputData + ")")
    return theAction, theActionInputData, searchedTerms, enums, hrefs, chatFormat, seedIn, datas


def __actionCreateImageWithDescription(theActionInputData, seedIn):
    Print.generic("\nThe model wants to create an image with the following description: " + theActionInputData + "\n")
    next = Util.printYNQuestion("Do you want to allow this action?")
    match next:
        case 0:
            imageResponse = TextToImage.getTextToImageResponse(Util.getRandomSeed(), theActionInputData, "", seedIn, False, "")
            if imageResponse is not None:
                Print.response(imageResponse, "\n")
            else:
                Print.error("\nError generating image - continuing...")
        case 1:
            Print.red("\nWill not generate image, continuing...")
        case 2:
            Print.red("\nAborting functions.\n")
            return False
    return True


def __actionWriteFileToFilesystem(theActionInputData):
    fileName = "file_" + Util.getDateTimeString()
    fileContents = theActionInputData
    Print.generic("\nThe model wants to write the following file: " + fileName + ", with the following contents:\n")
    Print.generic(fileContents + "\n")
    next = Util.printYNQuestion("Do you want to allow this action?")
    match next:
        case 0:
            Operation.appendFile(Path.OTHER_FILE_PATH + fileName, fileContents + "\n")
            Print.green("\nFile has been written.")
        case 1:
            Print.red("\nWill not write file, continuing...")
        case 2:
            Print.red("\nAborting functions.\n")
            return False
    return True
