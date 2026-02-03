# package modules.string


import json as JSON


import modules.core.Configuration as Configuration
import modules.core.file.Operation as Operation
import modules.core.typecheck.TypeCheck as TypeCheck
import modules.core.typecheck.Types as Types
import modules.core.Util as Util
import modules.string.Path as Path


__imageToTextSystemPrompt = ""
__imageToTextDefaultUserPrompt = ""
__textToTextFunctionsSystemPromptBody = ""
__textToTextFunctionsSystemPrompt = ""
__textToTextFunctionsEditSystemPrompt = ""
__textToTextFunctionsActionsArrayDescription = ""
__textToTextFunctionsActionsDescriptions = ""
__textToTextFunctionsActionsInputsDescriptions = ""
__textToTextRespondUsingData = ""
__textToTextDetermineNextAssistant = ""
__textToTextSummarizeText = ""
__textToTextFunctionsActionsNoneLeft = ""
__textToTextFunctionsActionsRemaining = ""
__textToTextShouldRepromptSystemPrompt = ""
__textToTextRepromptSystemPrompt = ""
__textToTextSourceRelevanceSystemPrompt = ""


def loadConfiguration():
    promptConfig = Operation.readFile(Path.CONFIGS_PROMPT_FILE_NAME, None, False)
    if promptConfig is not None:
        j = JSON.loads(promptConfig)

        global __imageToTextSystemPrompt
        __imageToTextSystemPrompt = j.get("image_to_text_system_prompt")

        global __imageToTextDefaultUserPrompt
        __imageToTextDefaultUserPrompt = j.get("image_to_text_default_user_prompt")

        global __textToTextFunctionsSystemPromptBody
        __textToTextFunctionsSystemPromptBody = j.get("text_to_text_functions_system_prompt_body")

        global __textToTextFunctionsSystemPrompt
        __textToTextFunctionsSystemPrompt = j.get("text_to_text_functions_system_prompt")

        global __textToTextFunctionsEditSystemPrompt
        __textToTextFunctionsEditSystemPrompt = j.get("text_to_text_functions_edit_system_prompt")

        global __textToTextFunctionsActionsArrayDescription
        __textToTextFunctionsActionsArrayDescription = j.get("text_to_text_functions_actions_array_description")

        global __textToTextFunctionsActionsDescriptions
        __textToTextFunctionsActionsDescriptions = j.get("text_to_text_functions_actions_descriptions")

        global __textToTextFunctionsActionsInputsDescriptions
        __textToTextFunctionsActionsInputsDescriptions = j.get("text_to_text_functions_actions_inputs_descriptions")

        global __textToTextRespondUsingData
        __textToTextRespondUsingData = j.get("text_to_text_respond_using_data")

        global __textToTextDetermineNextAssistant
        __textToTextDetermineNextAssistant = j.get("text_to_text_determine_next_assistant")

        global __textToTextSummarizeText
        __textToTextSummarizeText = j.get("text_to_text_summarize_text")

        global __textToTextFunctionsActionsNoneLeft
        __textToTextFunctionsActionsNoneLeft = j.get("text_to_text_functions_actions_none_left")

        global __textToTextFunctionsActionsRemaining
        __textToTextFunctionsActionsRemaining = j.get("text_to_text_functions_actions_remaining")

        global __textToTextShouldRepromptSystemPrompt
        __textToTextShouldRepromptSystemPrompt = j.get("text_to_text_should_reprompt_system_prompt")

        global __textToTextRepromptSystemPrompt
        __textToTextRepromptSystemPrompt = j.get("text_to_text_reprompt_system_prompt")

        global __textToTextSourceRelevanceSystemPrompt
        __textToTextSourceRelevanceSystemPrompt = j.get("text_to_text_source_relevance_system_prompt")

    return


def getImageToTextSystemPrompt():
    global __imageToTextSystemPrompt
    return __imageToTextSystemPrompt


def getImageToTextDefaultUserPrompt():
    global __imageToTextDefaultUserPrompt
    return __imageToTextDefaultUserPrompt


def getFunctionSystemPromptBody(actionEnumsIn):
    TypeCheck.enforce(actionEnumsIn, Types.LIST)
    global __textToTextFunctionsSystemPromptBody
    out = __textToTextFunctionsSystemPromptBody
    out = out.replace("$LOCATION$", Configuration.getConfig("location"))
    out = out.replace("$TIME_DATE_READABLE$", Util.getReadableDateTimeString())
    out = out.replace("$ACTION_ENUMS$", Util.formatArrayToString(actionEnumsIn, "; "))
    return out


def getFunctionSystemPrompt(actionEnumsIn):
    TypeCheck.enforce(actionEnumsIn, Types.LIST)
    global __textToTextFunctionsSystemPrompt
    out = __textToTextFunctionsSystemPrompt
    out = out.replace("$FUNCTIONS_SYSTEM_PROMPT_BODY$", getFunctionSystemPromptBody(actionEnumsIn))
    return out


def getFunctionEditSystemPrompt(actionEnumsIn):
    TypeCheck.enforce(actionEnumsIn, Types.LIST)
    global __textToTextFunctionsEditSystemPrompt
    out = __textToTextFunctionsEditSystemPrompt
    out = out.replace("$FUNCTIONS_SYSTEM_PROMPT_BODY$", getFunctionSystemPromptBody(actionEnumsIn))
    return out


def getFunctionActionsArrayDescription(actionEnumsIn):
    TypeCheck.enforce(actionEnumsIn, Types.LIST)
    global __textToTextFunctionsActionsArrayDescription
    out = __textToTextFunctionsActionsArrayDescription
    out = out.replace("$ACTION_ENUMS$", Util.formatArrayToString(actionEnumsIn, "; "))
    return out


def getFunctionActionDescription():
    global __textToTextFunctionsActionsDescriptions
    return __textToTextFunctionsActionsDescriptions


def getFunctionActionInputDataDescription():
    global __textToTextFunctionsActionsInputsDescriptions
    return __textToTextFunctionsActionsInputsDescriptions


def getRespondUsingInformationPrompt():
    global __textToTextRespondUsingData
    return __textToTextRespondUsingData


def getDetermineBestAssistantPrompt():
    global __textToTextDetermineNextAssistant
    return __textToTextDetermineNextAssistant


def getCondenseSourceDataPrompt():
    global __textToTextSummarizeText
    return __textToTextSummarizeText


def getNoMoreActionsPrompt():
    global __textToTextFunctionsActionsNoneLeft
    return __textToTextFunctionsActionsNoneLeft


def getRemainingActionsPrompt(actionsIn):
    global __textToTextFunctionsActionsRemaining
    out = __textToTextFunctionsActionsRemaining
    out = out.replace("$ACTION_ENUMS$", Util.formatArrayToString(actionsIn, "; "))
    return out


def getShouldRepromptSystemPrompt():
    global __textToTextShouldRepromptSystemPrompt
    return __textToTextShouldRepromptSystemPrompt


def getRepromptSystemPrompt(proposedAnswerIn):
    global __textToTextRepromptSystemPrompt
    TypeCheck.enforce(proposedAnswerIn, Types.STRING)
    out = __textToTextRepromptSystemPrompt
    out = out.replace("$PREVIOUS_ANSWER$", proposedAnswerIn)
    return out


def getSourceRelevanceSystemPrompt():
    global __textToTextSourceRelevanceSystemPrompt
    return __textToTextSourceRelevanceSystemPrompt
