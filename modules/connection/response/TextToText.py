# package modules.connection.response


import copy as Copy
import json as JSON
import sys as System
import time as Time


import modules.connection.request.TextToText as TextToText
import modules.connection.response.TextToAudio as TextToAudio
import modules.connection.response.TextToImage as TextToImage
import modules.Conversation as Conversation
import modules.core.file.Operation as Operation
import modules.core.file.Reader as Reader
import modules.core.Configuration as Configuration
import modules.core.Print as Print
import modules.core.typecheck.TypeCheck as TypeCheck
import modules.core.typecheck.Types as Types
import modules.core.Util as Util
import modules.Model as Model
import modules.string.Path as Path
import modules.string.Prompt as Prompt
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


def getResponse(messagesIn, seedIn, functionIn=None, functionCallIn=None, grammarIn=None):
    model = Configuration.getConfig("default_text_to_text_model")
    if model is None or len(model) == 0:
        Util.printError("Text-to-Text is disabled because the Text-to-Text model is not set.")
        return None

    requestData = {}
    requestData["model"] = model
    requestData["messages"] = messagesIn
    requestData["seed"] = seedIn
    if grammarIn is not None:
        requestData["grammar"] = grammarIn
    if functionIn is not None:
        requestData["functions"] = functionIn
    if functionCallIn is not None:
        requestData["function_call"] = functionCallIn

    Util.setShouldInterruptCurrentOutputProcess(False)
    response = TextToText.createRequest(requestData)
    Util.setShouldInterruptCurrentOutputProcess(True)

    if response is None:
        Util.printError("Error getting response.")
    return response


def getStreamedResponse(promptIn, seedIn, dataIn, shouldWriteDataToConvo, isReprompt, isServer, proposedAnswerIn):
    TypeCheck.enforce(promptIn, Types.STRING)
    TypeCheck.enforce(seedIn, Types.INTEGER)
    TypeCheck.enforce(dataIn, Types.LIST)
    TypeCheck.enforce(shouldWriteDataToConvo, Types.BOOLEAN)
    TypeCheck.enforce(isReprompt, Types.BOOLEAN)
    TypeCheck.enforce(proposedAnswerIn, Types.STRING)

    if len(Configuration.getConfig("default_text_to_text_model")) == 0:
        if Configuration.getConfig("debug_level") >= 1:
            yield from Util.printError("Text-to-Text is disabled because the Text-to-Text model is not set.")
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
        for data in dataIn:
            promptHistory = Conversation.addToPrompt(promptHistory, "system", f"{Prompt.getRespondUsingInformationPrompt()}{data}", chatFormat)

    promptHistoryForReprompt = Copy.copy(promptHistory)

    systemPromptOverride = Model.getChatModelPromptOverride(Configuration.getConfig("default_text_to_text_model"))
    if systemPromptOverride is not None:
        if isReprompt:
            if Configuration.getConfig("debug_level") >= 3:
                yield from Util.printDebug("Using overridden system prompt with reprompt.")
            promptHistory = Conversation.addToPrompt(promptHistory, "system", f"{systemPromptOverride} {Prompt.getRepromptSystemPrompt(proposedAnswerIn)}", chatFormat)
        else:
            yield from Util.printDebug("Using overridden system prompt.")
            promptHistory = Conversation.addToPrompt(promptHistory, "system", systemPromptOverride, chatFormat)
    elif len(Configuration.getConfig("system_prompt")) > 0:
        if isReprompt:
            if Configuration.getConfig("debug_level") >= 3:
                yield from Util.printDebug("Using configuration system prompt with reprompt.")
            promptHistory = Conversation.addToPrompt(promptHistory, "system", f'{Configuration.getConfig("system_prompt")} {Prompt.getRepromptSystemPrompt(proposedAnswerIn)}', chatFormat)
        else:
            if Configuration.getConfig("debug_level") >= 3:
                yield from Util.printDebug("Using configuration system prompt.")
            promptHistory = Conversation.addToPrompt(promptHistory, "system", Configuration.getConfig("system_prompt"), chatFormat)
    elif isReprompt:
        if Configuration.getConfig("debug_level") >= 3:
            yield from Util.printDebug("Using reprompt system prompt.")
        promptHistory = Conversation.addToPrompt(promptHistory, "system", Prompt.getRepromptSystemPrompt(proposedAnswerIn), chatFormat)
    else:
        if Configuration.getConfig("debug_level") >= 2:
            yield from Util.printInfo("Not using a system prompt.")
    promptHistory = Conversation.addToPrompt(promptHistory, "user", promptIn, chatFormat)
    promptHistory = Conversation.addToPrompt(promptHistory, "assistant", "", chatFormat, isPromptEnding=True)
    Util.printPromptHistory(promptHistory)

    assistantResponse = ""
    Util.setShouldInterruptCurrentOutputProcess(False)
    completion = TextToText.createStreamedRequest(
        {
            "model": Configuration.getConfig("default_text_to_text_model"),
            "messages": promptHistory,
            "seed": seedIn,
        }
    )

    if completion is None:
        if Configuration.getConfig("debug_level") >= 1:
            yield from Util.printError("No response from server.")
        Util.setShouldInterruptCurrentOutputProcess(True)
        return None

    # pausedLetters = {}
    # stop = False
    currentLength = 0
    punctuations = Configuration.getConfig("line_break_punctuations")
    lastLetter = ""
    lineBreakThreshold = Configuration.getConfig("line_break_threshold")
    startTime = None
    prematureTermination = False
    tokens = None
    assistantResponseStringAsPrinted = ""
    inCodeBlock = False
    codeBlockCounter = 0
    try:
        for chunk in completion:  # L1
            if Util.getShouldInterruptCurrentOutputProcess():
                prematureTermination = True
                Util.printDebug("Stopped output.")
                break  # L1

            letter = chunk.choices[0].delta.content
            if letter is None:
                Util.printDebug("Letter is None - breaking loop.")
                break  # L1

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
            #             Util.printDebug("Stopword reached: \"" + pausedLetters[stopword] + "\"")
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
            #     Util.printDebug("Stopping output because stopword reached: \"" + pausedLetters[stopword] + "\"")
            #     break  # L1

            if letter == "`":
                codeBlockCounter += 1
                if codeBlockCounter == 3:
                    codeBlockCounter = 0
                    inCodeBlock = not inCodeBlock
            else:
                codeBlockCounter = 0

            skipPrint = False
            if letter != "\n":
                currentLength += 1
                if lastLetter in punctuations and currentLength >= lineBreakThreshold and not inCodeBlock:
                    skipPrint = letter == " "
                    currentLength = 0
                    yield from Print.response("\n", "")
                    assistantResponseStringAsPrinted += "\n"
            else:
                currentLength = 0

            if not skipPrint:
                yield from Print.response(letter, "")
                assistantResponseStringAsPrinted += letter
                Time.sleep(Configuration.getConfig("print_delay"))
                System.stdout.flush()
            assistantResponse += letter
            lastLetter = letter

        if chunk["usage"] is not None:
            tokens = chunk["usage"]
    except Exception as e:
        Util.printError("An error occurred during server output:" + str(e))

    Util.setShouldInterruptCurrentOutputProcess(True)
    endTime = Time.perf_counter()
    yield from Print.response("\n", "")
    __printTokenUsage(startTime, endTime, tokens)

    assistantResponseString = assistantResponse.replace("ASSISTANT: ", "").replace("SYSTEM: ", "")
    if "</think>\n" in assistantResponseString: assistantResponseString = assistantResponseString.split("</think>")[1]
    if prematureTermination:                    assistantResponseString += "... [TRUNCATED]"
    noReprompt = False
    if isReprompt and assistantResponseString == proposedAnswerIn:
        if Configuration.getConfig("debug_level") >= 2:
            yield from Util.printInfo("The currently-proposed answer is the same as the last-proposed answer - breaking reprompt loop.")
        if Configuration.getConfig("debug_level") > 0:
            yield from Print.response(assistantResponseStringAsPrinted, "\n")
        noReprompt = True
    if Configuration.getConfig("do_reprompts") and not noReprompt:
        if Configuration.getConfig("reprompt_with_history"):    repromptHistory = promptHistoryForReprompt
        else:                                                   repromptHistory = []
        shouldRepromptMessage = Conversation.addToPrompt(repromptHistory, "system", Prompt.getShouldRepromptSystemPrompt(), chatFormat)
        shouldRepromptMessage = Conversation.addToPrompt(shouldRepromptMessage, "user", promptIn, chatFormat)
        shouldRepromptMessage = Conversation.addToPrompt(shouldRepromptMessage, "assistant", assistantResponseString, chatFormat, isPromptEnding=True)

        if Configuration.getConfig("debug_level") >= 2:
            yield from Util.printInfo("Determining if answer needs to be regenerated...")
        Util.setShouldInterruptCurrentOutputProcess(False)
        shouldRepromptStartTime = Time.perf_counter()
        shouldRepromptResult = getResponse(
            shouldRepromptMessage,
            seedIn,
            grammarIn=Util.getGrammarString(["PASS", "FAIL"]),
        )
        shouldRepromptEndTime = Time.perf_counter()
        Util.setShouldInterruptCurrentOutputProcess(True)

        if shouldRepromptResult is not None:
            __printTokenUsage(shouldRepromptStartTime, shouldRepromptEndTime, shouldRepromptResult["usage"])
            Util.printDebug("Model reply: " + shouldRepromptResult["content"])
            if "pass" in shouldRepromptResult["content"].lower():
                if Configuration.getConfig("debug_level") >= 2:
                    yield from Util.printInfo("Keeping this answer.")
                if Configuration.getConfig("debug_level") > 0:
                    yield from Print.response(assistantResponseStringAsPrinted, "\n")
            else:
                if Configuration.getConfig("debug_level") >= 2:
                    yield from Util.printInfo("Regenerating answer - this may infinitely loop!")
                if isServer:
                    yieldResult = yield from getStreamedResponse(promptIn, seedIn, dataIn, shouldWriteDataToConvo, True, isServer, assistantResponseString)
                    return yieldResult
                else:
                    for _ in getStreamedResponse(promptIn, seedIn, dataIn, shouldWriteDataToConvo, True, isServer, assistantResponseString):
                        pass
        else:
            if Configuration.getConfig("debug_level") >= 1:
                yield from Util.printError("Reprompt failed - using default answer.")
            if Configuration.getConfig("debug_level") > 0:
                yield from Print.response(assistantResponseStringAsPrinted, "\n")

    if len(dataIn) > 0 and shouldWriteDataToConvo:
        for data in dataIn:
            Conversation.writeConversation(currentConversationName, "SYSTEM: " + f"{Prompt.getRespondUsingInformationPrompt()}{data}")

    Conversation.writeConversation(currentConversationName, "USER: " + promptIn)
    Conversation.writeConversation(currentConversationName, "ASSISTANT: " + assistantResponseString)

    if Configuration.getConfig("read_outputs") and not isServer:
        Util.printInfo("Generating Audio-to-Text...")
        response = TextToAudio.getResponse(assistantResponse, True)
        if response is not None:
            Util.printDebug("Playing Audio-to-Text...")
            Reader.openLocalFile(response, "aplay -q -N", False)
        else:
            Util.printError("Could not generate Audio-to-Text.")
    return assistantResponse


def function_action(actionsArray):
    return


def getTextToTextResponseFunctions(promptIn, seedIn, dataIn, isServer):
    TypeCheck.enforce(promptIn, Types.STRING)
    TypeCheck.enforce(seedIn, Types.INTEGER)
    TypeCheck.enforce(dataIn, Types.LIST)

    if len(Configuration.getConfig("default_text_to_text_model")) == 0:
        if Configuration.getConfig("debug_level") >= 1:
            yield from Util.printError("Text-to-Text is disabled because the Text-to-Text model is not set.")
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
            prompt = []
            for data in datas:
                prompt = Conversation.addToPrompt(prompt, "system", Prompt.getRespondUsingInformationPrompt() + data, chatFormat)
            prompt = Conversation.addToPrompt(prompt, "system", Prompt.getFunctionEditSystemPrompt(enums), chatFormat)
            prompt = Conversation.addToPrompt(prompt, "system", remainingActions, chatFormat)

        prompt = Conversation.addToPrompt(prompt, "user", promptIn, chatFormat)
        fullPrompt = promptHistory + prompt
        Util.printPromptHistory(fullPrompt)
        if Configuration.getConfig("debug_level") >= 2:
            yield from Util.printInfo("Determining function(s) to do for this prompt...")

        Util.setShouldInterruptCurrentOutputProcess(False)
        startTime = Time.perf_counter()
        result = getResponse(
            fullPrompt,
            seedIn,
            functionIn=function,
            functionCallIn={
                "name": "function_action",
            },
        )
        endTime = Time.perf_counter()
        Util.setShouldInterruptCurrentOutputProcess(True)

        actionsResponse = None
        if result is not None:
            __printTokenUsage(startTime, endTime, result["usage"])
            if "function_call" in result:
                functionCall = result["function_call"]
                if "arguments" in functionCall:
                    actionsResponse = JSON.loads(functionCall["arguments"])
                else:
                    if Configuration.getConfig("debug_level") >= 1:
                        yield from Util.printError("No arguments received from server.")
                    break  # L1
            else:
                if "content" in result and result["content"] is not None:
                    # Util.cleanupServerResponseTokens(result["content"])
                    resultJson = JSON.loads(result["content"])
                    if "arguments" in resultJson:
                        actionsResponse = resultJson["arguments"]
                    else:
                        if Configuration.getConfig("debug_level") >= 1:
                            yield from Util.printError("No arguments received from server.")
                        break  # L1
                else:
                    if Configuration.getConfig("debug_level") >= 1:
                        yield from Util.printError("No content received from server.")
                    break  # L1
        else:
            if Configuration.getConfig("debug_level") >= 1:
                yield from Util.printError("No response from server.")
            break  # L1

        if actionsResponse is None or actionsResponse.get("actionsArray") is None:
            if Configuration.getConfig("debug_level") >= 1:
                yield from Util.printError("No response from server - trying default chat completion.")
            if isServer:
                yieldResult = yield from getStreamedResponse(promptIn, seedIn, [], True, False, isServer, "")
                return yieldResult
            else:
                for _ in getStreamedResponse(promptIn, seedIn, [], True, False, isServer, ""):
                    pass

        actionsArray = actionsResponse.get("actionsArray")

        if Configuration.getConfig("debug_level") >= 3:
            yield from Util.printDebug("Determined actions and input data:")

        if len(actionsArray) > 0 and len(actionsArray[0]) > 0:
            for action in actionsArray:
                if Configuration.getConfig("debug_level") >= 3:
                    yield from Util.printDebug(" - " + action.get("action") + ": " + action.get("action_input_data"))
        else:
            if Configuration.getConfig("debug_level") >= 3:
                yield from Util.printDebug(" - (None)")

        if len(actionsArray) < 1:
            if Configuration.getConfig("debug_level") >= 3:
                yield from Util.printDebug("No more actions in the action plan - exiting loop.")
            break  # L1

        action = actionsArray[0]
        theAction = action.get("action").upper()
        theActionInputData = action.get("action_input_data").lower()

        if theAction is lastAction and theActionInputData is lastActionData:
            if Configuration.getConfig("debug_level") >= 3:
                yield from Util.printDebug("The action and data are the same as the last - exiting loop.")
            break  # L1

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
                    datas,
                    promptIn
                )
                if not actionResult:
                    break  # L1
                theAction, theActionInputData, searchedTerms, enums, hrefs, chatFormat, seedIn, datas = actionResult

            case "CREATE_IMAGE_WITH_DESCRIPTION":
                actionResult = __actionCreateImageWithDescription(theActionInputData, seedIn)
                if not actionResult:
                    break  # L1

            case "WRITE_FILE_TO_FILESYSTEM":
                actionResult = __actionWriteFileToFilesystem(theActionInputData)
                if not actionResult:
                    break  # L1

            case _:
                if Configuration.getConfig("debug_level") >= 1:
                    yield from Util.printError("Unrecognized action: " + action)

        if Configuration.getConfig("debug_level") >= 3:
            yield from Util.printDebug("Action \"" + theAction + ": " + theActionInputData + "\" has completed successfully.")

        if len(actionsArray) >= 1:
            lastActionsArray = actionsArray
            lastActionsArray.pop(0)
            if Configuration.getConfig("debug_level") >= 3:
                yield from Util.printDebug("Reprompting model with action plan.")
        else:
            if Configuration.getConfig("debug_level") >= 3:
                yield from Util.printDebug("This was the last action in the action plan - exiting loop.")
            break  # L1

    hasHref = len(hrefs) > 0
    if not hasHref:
        if Configuration.getConfig("debug_level") >= 2:
            yield from Util.printInfo("This is an offline response.")

    response = yield from getStreamedResponse(promptIn, seedIn, datas, True, False, isServer, "")

    if response is None:
        if Configuration.getConfig("debug_level") >= 1:
            yield from Util.printError("No response from server.")
    else:
        if hasHref:
            yield from Print.response("Sources analyzed:", "\n")
            for href in hrefs:
                yield from Print.response(" - " + href, "\n")
    return response


def getTextToTextResponseModel(promptIn, seedIn):
    TypeCheck.enforce(promptIn, Types.STRING)
    TypeCheck.enforce(seedIn, Types.INTEGER)

    if len(Configuration.getConfig("default_text_to_text_model")) == 0:
        Util.printError("Text-to-Text is disabled because the Text-to-Text model is not set.")
        return None

    if not Configuration.getConfig("enable_automatic_model_switching"):
        return Configuration.getConfig("default_text_to_text_model")
    else:
        Util.printInfo("Switching models - this may take a while...")
        Configuration.resetDefaultTextModel()

        switchableModels = Model.getSwitchableTextModels()
        if len(switchableModels) == 0:
            Util.printDebug("No switchable models - skipping model switcher.")
            return None
        elif len(switchableModels) == 1:
            nextModel = Model.getModelByNameAndType(switchableModels[0], "text_to_text", True, True, False)
            if nextModel is not None:   Util.printDebug("Only " + switchableModels[0] + " is enabled - using it and skipping model switcher.")
            else:                       Util.printError("Only " + switchableModels[0] + " is enabled, but cannot load model.")
            return nextModel
        else:
            chatFormat = Model.getChatModelFormat(Configuration.getConfig("default_text_to_text_model"))
            conversation = Conversation.getConversation(Conversation.getConversationName())
            promptHistory = Conversation.getPromptHistoryFromConversation(conversation, chatFormat)
            systemContent = Prompt.getDetermineBestAssistantPrompt() + Model.getSwitchableTextModelDescriptions()
            promptMessage = Conversation.addToPrompt(promptHistory, "system", systemContent, chatFormat)
            promptMessage = Conversation.addToPrompt(promptMessage, "user", promptIn, chatFormat)
            grammarString = Util.getGrammarString(switchableModels)

            Util.printDump("Current prompt for model response:")
            Util.printPromptHistory(promptMessage)
            Util.printDump("Choices: " + grammarString)

            Util.setShouldInterruptCurrentOutputProcess(False)
            startTime = Time.perf_counter()
            result = getResponse(
                promptMessage,
                seedIn,
                grammarIn=grammarString,
            )
            endTime = Time.perf_counter()
            Util.setShouldInterruptCurrentOutputProcess(True)

            if result is not None:
                nextModel = Model.getModelByNameAndType(result["content"], "text_to_text", True, True, False)
                if nextModel is not None:
                    Util.printDebug("Next model: " + nextModel)
                else:
                    Util.printError("Next model is determined but cannot be found: " + nextModel)
                __printTokenUsage(startTime, endTime, result["usage"])
                return nextModel
    return None


def __actionSearchInternetWithSearchTerm(theAction, theActionInputData, searchedTerms, enums, hrefs, chatFormat, seedIn, datas, promptIn):
    if not Configuration.getConfig("enable_internet"):
        Util.printDebug("Internet is disabled - skipping this action. (\"" + theAction + "\": " + theActionInputData + ")")
        return theAction, theActionInputData, searchedTerms, enums, hrefs, chatFormat, seedIn, datas
    
    if len(theActionInputData) < 1:
        Util.printError("No search term provided.")
        return theAction, theActionInputData, searchedTerms, enums, hrefs, chatFormat, seedIn, datas

    if theActionInputData in searchedTerms or theActionInputData.upper() in enums:
        Util.printError("Skipping duplicated search term: " + theActionInputData + " - exiting loop.")
        return False

    searchedTerms.append(theActionInputData)
    searchResultSources = Web.getSearchResults(theActionInputData, Configuration.getConfig("max_sources_per_search"))
    nonDuplicateHrefs = []
    for href in searchResultSources:
        if href not in hrefs:
            nonDuplicateHrefs.append(href)
        else:
            Util.printDebug("Skipped duplicate source: " + href)

    if len(nonDuplicateHrefs) < 1:
        Util.printDebug("All target links are duplicates - skipping this search.")
        return theAction, theActionInputData, searchedTerms, enums, hrefs, chatFormat, seedIn, datas

    searchResults = Web.getSearchResultsTextAsync(nonDuplicateHrefs, Configuration.getConfig("max_sentences_per_source"))
    if len(searchResults) < 1:
        Util.printError("No search results with this search term.")
        return theAction, theActionInputData, searchedTerms, enums, hrefs, chatFormat, seedIn, datas

    for key, value in searchResults.items():
        if Configuration.getConfig("enable_determine_source_relevance"):
            relevancePrompt = []
            relevancePrompt = Conversation.addToPrompt(relevancePrompt, "system", f"{Prompt.getSourceRelevanceSystemPrompt()}{value}", chatFormat)
            relevancePrompt = Conversation.addToPrompt(relevancePrompt, "user", promptIn, chatFormat)

            Util.setShouldInterruptCurrentOutputProcess(False)
            startTimeInner = Time.perf_counter()
            sourceRelevance = getResponse(
                relevancePrompt,
                seedIn,
                grammarIn=Util.getGrammarString(["YES", "NO"]),
            )
            endTimeInner = Time.perf_counter()
            Util.setShouldInterruptCurrentOutputProcess(True)
            if sourceRelevance is not None:
                __printTokenUsage(startTimeInner, endTimeInner, sourceRelevance["usage"])
                Util.printInfo(f'Source relevant to prompt: {sourceRelevance["content"]}')
                if sourceRelevance["content"].lower() == "no":
                    continue
            else:
                Util.printError("Failed to determine source relevance.")

        if Configuration.getConfig("enable_source_condensing"):
            Util.printDebug("Condensing source data: " + key)

            Util.setShouldInterruptCurrentOutputProcess(False)
            startTimeInner = Time.perf_counter()
            simplifiedData = getResponse(
                Conversation.addToPrompt([], "system", Prompt.getCondenseSourceDataPrompt() + value, chatFormat),
                seedIn,
            )
            endTimeInner = Time.perf_counter()
            Util.setShouldInterruptCurrentOutputProcess(True)

            if simplifiedData is not None:
                simplifiedDataContent = simplifiedData["content"]
                Util.printDump("Condensed source data:" + simplifiedDataContent)
                value = simplifiedDataContent
                __printTokenUsage(startTimeInner, endTimeInner, simplifiedData["usage"])
            else:
                Util.printError(f"Failed to condense source: {key} - adding as whole source.")
        hrefs.append(key)
        datas.append(value)
        Util.printDebug("Appended source data: " + key)
    return theAction, theActionInputData, searchedTerms, enums, hrefs, chatFormat, seedIn, datas


def __actionCreateImageWithDescription(theActionInputData, seedIn):
    Print.generic("The model wants to create an image with the following description: " + theActionInputData)
    next = Util.printYNQuestion("Do you want to allow this action?")
    match next:
        case 0:
            Util.setShouldInterruptCurrentOutputProcess(False)
            imageResponse = TextToImage.getResponse(Util.getRandomSeed(), theActionInputData, "", seedIn, 0, None)
            Util.setShouldInterruptCurrentOutputProcess(True)
            if imageResponse is not None:
                Print.response(imageResponse, "")
            else:
                Util.printError("Error generating image - continuing...")
        case 1:
            Print.red("Will not generate image, continuing...")
        case 2:
            Print.red("Aborting functions.")
            return False
    return True


def __actionWriteFileToFilesystem(theActionInputData):
    fileName = "file_" + Util.getDateTimeString()
    fileContents = theActionInputData
    fileContents = Util.cleanupString(fileContents)
    Print.generic("The model wants to write the following file: " + fileName + ", with the following contents:")
    Print.generic(fileContents)
    next = Util.printYNQuestion("Do you want to allow this action?")
    match next:
        case 0:
            Operation.appendFile(Path.OTHER_FILE_PATH + fileName, fileContents)
            Print.green("File has been written.")
        case 1:
            Print.red("Will not write file, continuing...")
        case 2:
            Print.red("Aborting functions.")
            return False
    return True
