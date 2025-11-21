# package modules.connection.response


import base64 as Base64
import json as JSON


import modules.connection.request.ImageToVideo as ImageToVideo
import modules.core.file.Operation as Operation
import modules.core.Configuration as Configuration
import modules.core.typecheck.TypeCheck as TypeCheck
import modules.core.typecheck.Types as Types
import modules.core.Util as Util


def getResponse(promptIn, filePathIn, seedIn):
    TypeCheck.enforce(promptIn, Types.STRING)
    TypeCheck.enforce(filePathIn, Types.STRING)
    TypeCheck.enforce(seedIn, Types.INTEGER)

    model = Configuration.getConfig("default_image_to_video_model")
    if model is None or len(model) == 0:
        Util.printError("\nImage-to-Video is disabled because the Image-to-Video model is not set.\n")
        return None

    filePathIn = Util.removeApostrophesFromFileInput(filePathIn)
    if Operation.fileExists(filePathIn):
        requestParameters = {
            "prompt": promptIn,
            "model": Configuration.getConfig("default_image_to_video_model"),
            "file": Base64.b64encode(Operation.readFileBinary(filePathIn)).decode("utf-8"),
            "seed": seedIn,
            "size": Configuration.getConfig("image_size"),
            "step": Configuration.getConfig("image_step"),
        }
        Util.setShouldInterruptCurrentOutputProcess(False)
        response = ImageToVideo.createRequest(requestParameters)
        Util.setShouldInterruptCurrentOutputProcess(True)
        if response is not None:
            if Configuration.getConfig("write_output_params"):
                Operation.appendFile(response + ".params", JSON.dumps(requestParameters, indent=4))
            return "Your video is available at: " + response
        else:
            Util.printError("\nImage-to-Video generation failed!")
    else:
        Util.printError("\nFile does not exist!\n")

    return None
