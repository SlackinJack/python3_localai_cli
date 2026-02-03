from flask import Flask as Flask
from flask import request as FlaskRequest
from flask import Response as FlaskResponse
from flask import jsonify as FlaskJSONify


import modules.core.Configuration as Configuration
import modules.core.Print as Print
import modules.command.Conversation as Conversation
import modules.command.Messages as Messages
import modules.command.Settings as Settings
import modules.command.toggle.Function as Function
import modules.command.toggle.History as History
import modules.command.toggle.Internet as Internet
import modules.command.toggle.Reprompt as Reprompt
import modules.command.toggle.Switcher as Switcher
import modules.connection.response.TextToText as TextToText


app = Flask(__name__)


def startServer():
    Print.setIsServer(True)
    app.run(host=Configuration.getConfig("server_address"), port=Configuration.getConfig("server_port"))
    return


@app.route("/<command>", methods=["POST"])
def handleCommand(command):
    match command:
        # commands
        case "convo":
            return handleConversationRequest()
        case "messages":
            return handleMessagesRequest()
        case "settings":
            return handleSettingsRequest()
        # toggles
        case "functions":
            return handleFunctionsRequest()
        case "history":
            return handleHistoryRequest()
        case "internet":
            return handleInternetRequest()
        case "reprompt":
            return handleRepromptRequest()
        case "switcher":
            return handleSwitcherRequest()
        # endpoints
        case "t2t":
            return handleTextToTextRequest()
        case "t2ts":
            return handleTextToTextStreamedRequest()
        case "t2i":
            return handleTextToImageRequest()
        case "i2t":
            return handleImageToTextRequest()
    return


# commands


def handleConversationRequest():
    data = FlaskRequest.json
    conversationName = data.get("name")
    Conversation.changeConversation(conversationName)
    return FlaskResponse(status=200)


def handleMessagesRequest():
    result = Messages.messagesServer()
    return FlaskResponse(result, mimetype="text/plain")


def handleSettingsRequest():
    result = Settings.serverSettings()
    return FlaskResponse(result, mimetype="text/plain")


# toggles


def handleFunctionsRequest():
    yield from Function.toggle()
    return FlaskResponse(status=200)


def handleHistoryRequest():
    yield from History.toggle()
    return FlaskResponse(status=200)


def handleInternetRequest():
    yield from Internet.toggle()
    return FlaskResponse(status=200)


def handleRepromptRequest():
    yield from Reprompt.toggle()
    return FlaskResponse(status=200)


def handleSwitcherRequest():
    yield from Switcher.toggle()
    return FlaskResponse(status=200)


# endpoints


def handleTextToTextRequest():
    data = FlaskRequest.json
    prompt = data.get("prompt")
    seed = data.get("seed", 1)
    result = TextToText.getTextToTextResponse(prompt, seed)
    return FlaskResponse(result, mimetype="text/plain")


def handleTextToTextStreamedRequest():
    data = FlaskRequest.json
    prompt = data.get("prompt")
    seed = data.get("seed", 1)
    if Configuration.getConfig("enable_functions"):
        result = TextToText.getTextToTextResponseFunctions(prompt, seed, [], True)
    else:
        result = TextToText.getStreamedResponse(prompt, seed, [], True, False, True, "")
    return FlaskResponse(result, mimetype="text/plain")
    

def handleTextToImageRequest():
    data = FlaskRequest.json
    positive = data.get("positive")
    negative = data.get("negative")
    # ...
    result = None # base64 response
    return FlaskJSONify({"output": result})


def handleImageToTextRequest():
    data = FlaskRequest.json
    prompt = data.get("prompt")
    image = data.get("image")
    # do something with prompt and image
    result = "output"
    return FlaskJSONify({"output": result})
