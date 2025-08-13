# package modules.connection.response


import json as JSON


import modules.connection.request.TextToImage as TextToImage
import modules.core.file.Operation as Operation
import modules.core.file.Reader as Reader
import modules.core.Configuration as Configuration
import modules.core.typecheck.TypeCheck as TypeCheck
import modules.core.typecheck.Types as Types
import modules.core.Util as Util


def getTextToImageResponse(requestIdIn, positivePromptIn, negativePromptIn, seedIn, silent, workerId):
    TypeCheck.check(requestIdIn, Types.INTEGER)
    TypeCheck.check(positivePromptIn, Types.STRING)
    TypeCheck.check(negativePromptIn, Types.STRING)
    TypeCheck.checkList(seedIn, [Types.INTEGER, Types.NONE])
    TypeCheck.check(silent, Types.BOOLEAN)
    TypeCheck.check(workerId, Types.STRING)

    model = Configuration.getConfig("default_text_to_image_model")
    if model is None or len(model) == 0:
        Util.printError("\nText-to-Image is disabled because the Text-to-Image model is not set.\n")
        return None

    seedIn = Util.getRandomSeed() if seedIn is None else int(seedIn)

    if not silent:
        Util.printInfo("\nGenerating image...")
        Util.printDebug("\nPositive prompt:\n" + positivePromptIn + "\n")

        if len(negativePromptIn) > 0:
            Util.printDebug("Negative prompt:\n" + negativePromptIn + "\n")

        Util.printDebug("Image Settings:")
        Util.printDebug("Seed: " + str(seedIn))
        Util.printDebug("Dimensions (WxH): " + Configuration.getConfig("image_size"))
        Util.printDebug("Step: " + str(Configuration.getConfig("image_step")))
        Util.printDebug("Clip Skip: " + str(Configuration.getConfig("image_clipskip")))

    imageModel = Configuration.getConfig("default_text_to_image_model")

    if workerId is not None and len(workerId) > 0:
        imageModel += "-" + workerId

    requestParameters = {
        "model": imageModel,
        "seed": seedIn,
        "prompt": positivePromptIn if len(negativePromptIn) == 0 else positivePromptIn + "|" + negativePromptIn,
        "size": Configuration.getConfig("image_size"),
        "step": Configuration.getConfig("image_step"),
        "clip_skip": Configuration.getConfig("image_clipskip"),
    }
    response = TextToImage.createTextToImageRequest(requestIdIn, requestParameters)

    if response is not None:
        if Configuration.getConfig("write_output_params"):
            Operation.appendFile(response + ".params", JSON.dumps(requestParameters, indent=4))
        if silent:
            return response + "\n(Seed: " + str(seedIn) + ")"
        else:
            if Configuration.getConfig("automatically_open_files"):
                Reader.openLocalFile(response, None, True)
            return "Your image is available at: " + response
    else:
        Util.printError("\nText-to-Image creation failed!")

    return None
