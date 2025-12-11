from flask import Flask as Flask
from flask import request as FlaskRequest
from flask import Response as FlaskResponse
from flask import jsonify as FlaskJSONify
from flask import stream_with_context as FlaskStreamWithContext


import modules.core.Configuration as Configuration
import modules.core.Print as Print
import modules.connection.response.TextToText as TextToText


app = Flask(__name__)


def startServer():
    Print.setIsServer(True)
    app.run(host=Configuration.getConfig("server_address"), port=Configuration.getConfig("server_port"))
    return


@app.route("/<command>", methods=["POST"])
def handleCommand(command):
    match command:
        case "convo":
            return handleConversationRequest()
        case "t2t":
            return handleTextToTextRequest()
        case "t2ts":
            return handleTextToTextStreamedRequest()
        case "t2i":
            return handleTextToImageRequest()
        case "i2t":
            return handleImageToTextRequest()
    return


def handleConversationRequest():
    data = FlaskRequest.json
    conversationName = data.get("name")
    # set the conversation name
    return FlaskResponse(status=200)


def handleTextToTextRequest():
    data = FlaskRequest.json
    prompt = data.get("prompt")
    # do something with prompt
    result = "output"
    return FlaskJSONify({"output": result})


def handleTextToTextStreamedRequest():
    data = FlaskRequest.json
    prompt = data.get("prompt")
    seed = data.get("seed", 1)
    result = TextToText.getTextToTextResponseFunctions(prompt, seed, [], True)
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
