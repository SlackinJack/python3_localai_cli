# modules.connection.response


import base64 as Base64
import json as JSON


import modules.connection.request.ImageToVideo as ImageToVideo
import modules.file.Operation as Operation
import modules.Configuration as Configuration
import modules.Print as Print
import modules.typecheck.TypeCheck as TypeCheck
import modules.typecheck.Types as Types
import modules.Util as Util


def getImageToVideoResponse(promptIn, filePathIn, seedIn):
    TypeCheck.check(promptIn, Types.STRING)
    TypeCheck.check(filePathIn, Types.STRING)
    TypeCheck.check(seedIn, Types.INTEGER)

    model = Configuration.getConfig("default_image_to_video_model")
    if model is None or len(model) == 0:
        Print.error("\nImage-to-Video is disabled because the Image-to-Video model is not set.\n")
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
        response = ImageToVideo.createImageToVideoRequest(requestParameters)
        if response is not None:
            if Configuration.getConfig("write_output_params"):
                Operation.appendFile(response + ".params", JSON.dumps(requestParameters, indent=4))
            return "Your video is available at: " + response
        else:
            Print.error("\nImage-to-Video generation failed!")
    else:
        Print.error("\nFile does not exist!\n")

    return None
