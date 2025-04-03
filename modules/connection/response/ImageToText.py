# modules.connection.response


import base64 as Base64


import modules.connection.request.ImageToText as ImageToText
import modules.file.Operation as Operation
import modules.string.Prompt as Prompt
import modules.Configuration as Configuration
import modules.Print as Print
import modules.typecheck.TypeCheck as TypeCheck
import modules.typecheck.Types as Types
import modules.Util as Util


def getImageToTextResponse(promptIn, filePathIn):
    TypeCheck.check(promptIn, Types.STRING)
    TypeCheck.check(filePathIn, Types.STRING)

    model = Configuration.getConfig("default_image_to_text_model")
    if model is None or len(model) == 0:
        Print.error("\nImage-to-Text is disabled because the Image-to-Text model is not set.\n")
        return None

    if Operation.fileExists(filePathIn):
        fileExtension = filePathIn.split(".")
        fileExtension = fileExtension[len(fileExtension) - 1]
        imageUrl = "data:image/" + fileExtension + ";base64," + Base64.b64encode(Operation.readFileBinary(filePathIn)).decode("utf-8")
        response = ImageToText.createImageToTextRequest(
            {
                "model": Configuration.getConfig("default_image_to_text_model"),
                "messages": [
                    {
                        "role": "USER",
                        "content": [
                            {
                                "type": "text",
                                "text": Prompt.getImageToTextSystemPrompt(),
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": imageUrl,
                                },
                            },
                        ]
                    },
                    {
                        "role": "USER",
                        "content": [
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
            Print.error("\nNo message from server!\n")
    else:
        Print.error("\nFile does not exist!\n")

    return None
