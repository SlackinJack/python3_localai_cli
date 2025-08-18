# package modules.connection.response


import base64 as Base64
import json as JSON


import modules.connection.request.ImageToImage as ImageToImage
import modules.core.file.Operation as Operation
import modules.core.Configuration as Configuration
import modules.core.typecheck.TypeCheck as TypeCheck
import modules.core.typecheck.Types as Types
import modules.core.Util as Util


def getImageToImageResponse(positivePromptIn, negativePromptIn, filePathIn, seedIn):
    TypeCheck.enforce(positivePromptIn, Types.STRING)
    TypeCheck.enforce(negativePromptIn, Types.STRING)
    TypeCheck.enforce(filePathIn, Types.STRING)
    TypeCheck.enforce(seedIn, Types.INTEGER)

    model = Configuration.getConfig("default_image_to_image_model")
    if model is None or len(model) == 0:
        Util.printError("\nImage-to-Image is disabled because the Image-to-Image model is not set.\n")
        return None

    filePathIn = Util.removeApostrophesFromFileInput(filePathIn)
    if Operation.fileExists(filePathIn):
        requestParameters = {
            "model": Configuration.getConfig("default_image_to_image_model"),
            "prompt": positivePromptIn if len(negativePromptIn) == 0 else positivePromptIn + "|" + negativePromptIn,
            "file": Base64.b64encode(Operation.readFileBinary(filePathIn)).decode("utf-8"),
            "seed": seedIn,
            "size": Configuration.getConfig("image_size"),
            "step": Configuration.getConfig("image_step"),
            "clip_skip": Configuration.getConfig("image_clipskip"),
        }
        Util.setShouldInterruptCurrentOutputProcess(False)
        response = ImageToImage.createImageToImageRequest(requestParameters)
        Util.setShouldInterruptCurrentOutputProcess(True)

        if response is not None:
            if Configuration.getConfig("write_output_params"):
                Operation.appendFile(response + ".params", JSON.dumps(requestParameters, indent=4))
            return "Your image is available at: " + response
        else:
            Util.printError("\nImage-to-Image generation failed!")
    else:
        Util.printError("\nFile does not exist!\n")

    return None
