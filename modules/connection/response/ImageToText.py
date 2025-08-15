# package modules.connection.response


import base64 as Base64


import modules.connection.request.ImageToText as ImageToText
import modules.core.file.Operation as Operation
import modules.core.Configuration as Configuration
import modules.core.typecheck.TypeCheck as TypeCheck
import modules.core.typecheck.Types as Types
import modules.core.Util as Util
import modules.string.Prompt as Prompt


def getImageToTextResponse(promptIn, filePathIn):
    TypeCheck.check(promptIn, Types.STRING)
    TypeCheck.check(filePathIn, Types.STRING)

    model = Configuration.getConfig("default_image_to_text_model")
    if model is None or len(model) == 0:
        Util.printError("\nImage-to-Text is disabled because the Image-to-Text model is not set.\n")
        return None

    encodedFile = ""
    if ";base64," in filePathIn:
        encodedFile = filePathIn
    elif Operation.fileExists(filePathIn):
        fileExtension = filePathIn.split(".")
        fileExtension = fileExtension[len(fileExtension) - 1]
        encodedFile = "data:image/" + fileExtension + ";base64," + Base64.b64encode(Operation.readFileBinary(filePathIn)).decode("utf-8")
    else:
        Util.printError("\nFile does not exist!\n")
    if len(encodedFile) > 0:
        response = ImageToText.createImageToTextRequest(
            {
                "model": Configuration.getConfig("default_image_to_text_model"),
                "messages": [
                    {
                        "role": "SYSTEM",
                        "content": [
                            {
                                "type": "text",
                                "text": Prompt.getImageToTextSystemPrompt(),
                            },
                        ]
                    },
                    {
                        "role": "USER",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": encodedFile,
                                },
                            },
                            {
                                "type": "text",
                                "text": promptIn,
                            },
                        ]
                    },
                ]
            }
        )
        if response is not None:
            response = Util.cleanupString(response)
            response = Util.cleanupServerResponseTokens(response)
            return response
        else:
            Util.printError("\nNo message from server!\n")
    return None
