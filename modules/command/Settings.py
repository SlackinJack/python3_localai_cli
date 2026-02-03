# package modules.command


import modules.Conversation as Conversation
import modules.core.Configuration as Configuration
import modules.core.Print as Print
import modules.core.Util as Util
import modules.Model as Model


def command():
    for _ in serverSettings():
        pass
    return


def serverSettings():
    yield from Print.generic("Configuration File:")
    yield from Print.generic(Configuration.getConfigurationFileName(), tabs=1)

    yield from Print.generic("Settings:")
    yield from Print.setting(Configuration.getConfig("enable_functions"), "Functions", tabs=1)
    yield from Print.setting(Configuration.getConfig("enable_internet"), "Internet", tabs=1)
    yield from Print.setting(Configuration.getConfig("enable_automatic_model_switching"), "Model Switcher", tabs=1)
    yield from Print.setting(Configuration.getConfig("do_reprompts"), "Chat Reprompting", tabs=1)
    yield from Print.setting(Configuration.getConfig("enable_chat_history_consideration"), "Consider Chat History", tabs=1)

    yield from Print.generic("Models:")
    for modelType, modelName in Model.getModelTypes().items():
        modelNameDisplay = Util.padStringToLength(modelName + ":", 16)
        yield from Print.generic(modelNameDisplay + str(Configuration.getConfig("default_" + modelType + "_model")), tabs=1)

    yield from Print.generic("Conversation file:")
    yield from Print.generic(Conversation.getConversationName() + ".convo", tabs=1)

    yield from Print.generic("System prompt:")
    yield from Util.printCurrentSystemPrompt(Print.generic, "", tabs=1)
