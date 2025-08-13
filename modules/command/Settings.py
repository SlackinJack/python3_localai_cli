# package modules.command


import modules.Conversation as Conversation
import modules.core.Configuration as Configuration
import modules.core.Print as Print
import modules.core.Util as Util
import modules.Model as Model


def commandSettings():
    Print.generic("\nConfiguration File:\n  " + Configuration.getConfigurationFileName())

    Print.generic("\nSettings:")
    Print.setting(Configuration.getConfig("enable_functions"),                  "Functions")
    Print.setting(Configuration.getConfig("enable_internet"),                   "Internet")
    Print.setting(Configuration.getConfig("enable_automatic_model_switching"),  "Model Switcher")
    Print.setting(Configuration.getConfig("do_reprompts"),                      "Chat Reprompting")
    Print.setting(Configuration.getConfig("enable_chat_history_consideration"), "Consider Chat History")

    Print.generic("\nModels:")
    for modelType, modelName in Model.getModelTypes().items():
        modelNameDisplay = Util.padStringToLength(modelName + ":", 16)
        Print.generic("  " + modelNameDisplay + str(Configuration.getConfig("default_" + modelType + "_model")))

    Print.generic("\nConversation file:\n  " + Conversation.getConversationName() + ".convo")

    Print.generic("\nSystem prompt:")
    Util.printCurrentSystemPrompt(Print.generic, "")

    Print.generic("")
    return
