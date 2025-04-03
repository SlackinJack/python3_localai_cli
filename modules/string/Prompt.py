# modules.string


import modules.Configuration as Configuration
import modules.typecheck.TypeCheck as TypeCheck
import modules.typecheck.Types as Types
import modules.Util as Util


def getImageToTextSystemPrompt():
    return (
        "You are a helpful ASSISTANT. "
        "Use the provided image to answer USER's inquiry."
    )


def getFunctionSystemPromptBody(actionEnumsIn):
    TypeCheck.check(actionEnumsIn, Types.LIST)
    return (
        "You are encouraged to search the internet for information that will "
        "help you respond to the USER's inquiry.\n"

        "Files and images should not be created, unless explicitly "
        "requested in the inquiry.\n"

        "If the given inquiry requires the use of the current location, "
        "then use the following: " + Configuration.getConfig("location") + ".\n"

        "If the given inquiry requires the use of the current time and date, "
        "then use the following: " + Util.getReadableDateTimeString() + ".\n"

        "If you decide that additional actions must be used, then create an "
        "action plan of tasks in the form of an array. Otherwise, create an "
        "blank array.\n"

        "Available actions are: "
        "\"" + Util.formatArrayToString(actionEnumsIn, "\"; \"") + "\"."
    )


def getFunctionSystemPrompt(actionEnumsIn):
    TypeCheck.check(actionEnumsIn, Types.LIST)
    return (
        "If necessary, create an action plan to fulfill "
        "the tasks given by, and/or to provide an accurate response to, "
        "the USER's most recent inquiry."
        "\n" + getFunctionSystemPromptBody(actionEnumsIn)
    )


def getFunctionEditSystemPrompt(actionEnumsIn):
    TypeCheck.check(actionEnumsIn, Types.LIST)
    return (
        "If necessary, revise the current action plan which will fulfill the "
        "tasks given by, and/or to provide an accurate response to, the "
        "USER's most recent inquiry, using the newly provided information.\n"

        "Remove any irrelevant, redundant or unnecessary actions from the "
        "action plan that are not required by the USER's most recent "
        "inquiry.\n" + getFunctionSystemPromptBody(actionEnumsIn)
    )


def getFunctionActionsArrayDescription(actionEnumsIn):
    TypeCheck.check(actionEnumsIn, Types.LIST)
    return (
        "An order-sensitive action plan that will be completed in order to "
        "complete the given tasks, and/or accurately answer the inquiry.\n"

        "Each item in the action plan consists of a single action, and its "
        "corresponding input data for the action.\n"

        "Duplicate actions are permitted, only when the input data is "
        "different between each action.\n"

        "If additional actions should be used, then create an action "
        "plan in the form of an array.\n"

        "Otherwise, create an blank array.\n"
        "Available actions are: "
        "\"" + Util.formatArrayToString(actionEnumsIn, "\"; \"") + "\"."
    )


def getFunctionActionDescription():
    return (
        "The action to be completed at this step of the action plan.\n"

        "Use the action \"SEARCH_INTERNET_WITH_SEARCH_TERM\" to search the "
        "internet for current and updated information, or information on a "
        "specific subject regarding the inquiry.\n"

        "Use the action \"CREATE_IMAGE_WITH_DESCRIPTION\" "
        "to create an artificial image.\n"

        "Use the action \"WRITE_FILE_TO_FILESYSTEM\" to create a new "
        "raw text file on the filesystem."
    )


def getFunctionActionInputDataDescription():
    return (
        "The input data that corresponds to this specific action.\n"

        "If the action is \"SEARCH_INTERNET_WITH_SEARCH_TERM\", "
        "provide the search terms that will be used to search "
        "for information on the internet.\n"

        "If the action is \"CREATE_IMAGE_WITH_DESCRIPTION\", "
        "provide a comprehensive description of the image to be created, "
        "using keywords and specific details.\n"

        "If the action is \"WRITE_FILE_TO_FILESYSTEM\", "
        "provide the contents of the file."
    )


def getRespondUsingInformationPrompt():
    return ("For your next response, use the following data:\n\n")


def getDetermineBestAssistantPrompt():
    return (
        "Use the following descriptions available assistants to determine "
        "which assistant possesses the most relevant skills related to the "
        "task and/or inquiry given by USER: "
    )


def getCondenseSourceDataPrompt():
    return (
        "Summarize the key points from the "
        "following text using an unordered list: "
    )


def getNoMoreActionsPrompt():
    return (
        "There are currently no remaining actions "
        "in the action plan. If you continue without "
        "additional actions, then you will reply to USER."
    )


def getRemainingActionsPrompt(actionsIn):
    return (
        "Current remaining actions in the action plan: "
        "\"" + Util.formatArrayToString(actionsIn, "\"; \"") + "\"."
    )