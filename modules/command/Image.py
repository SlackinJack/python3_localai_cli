# modules.command


import threading as Threading
import time as Time


import modules.connection.response.ImageToImage as ImageToImage
import modules.connection.response.ImageToText as ImageToText
import modules.connection.response.ImageToVideo as ImageToVideo
import modules.connection.response.TextToImage as TextToImage
import modules.file.Operation as Operation
import modules.file.Reader as Reader
import modules.Configuration as Configuration
import modules.Model as Model
import modules.Print as Print
import modules.Util as Util


def commandImage():
    choices = [
        "Single Image",
        "Endless Images",
        "Image-to-Text",
        "Image-to-Image",
        "Image-to-Video",
        "Settings"
    ]

    def menu():
        selection = Util.printMenu("Image menu", "", choices)
        if selection is None:
            return
        elif selection == "Single Image":
            submenuImageSingle()
        elif selection == "Endless Images":
            submenuImageEndless()
        elif selection == "Image-to-Text":
            submenuImageToText()
        elif selection == "Image-to-Image":
            submenuImageToImage()
        elif selection == "Image-to-Video":
            submenuImageToVideo()
        elif selection == "Settings":
            submenuImageSettings()
        else:
            Print.error("\nInvalid selection.\n")
        menu()
        return
    menu()
    Print.generic("\nReturning to main menu.\n")
    return


def getPositivePrompt():
    positivePrompt = Util.printInput("Enter positive image prompt, or the path to a prompt (required)")
    if Util.checkStringHasFile(positivePrompt):
        theFilePath = Util.getFilePathFromPrompt(positivePrompt)
        positivePrompt = ""
        for filePath in theFilePath:
            prompt = __cleanupPromptFileString(Reader.getFileContents(filePath, False))
            if not Util.checkEmptyString(prompt):
                if len(positivePrompt) > 0:
                    positivePrompt += ", " + prompt
                else:
                    positivePrompt += prompt
            else:
                Print.error("\nPrompt file was empty and was skipped: " + filePath)
    return positivePrompt


def getNegativePrompt():
    negativePrompt = Util.printInput("Enter negative image prompt, or the path to a prompt (or leave empty to skip)")
    if Util.checkStringHasFile(negativePrompt):
        theFilePath = Util.getFilePathFromPrompt(negativePrompt)
        negativePrompt = ""
        for filePath in theFilePath:
            prompt = __cleanupPromptFileString(Reader.getFileContents(filePath, False))
            if not Util.checkEmptyString(prompt):
                if len(negativePrompt) > 0:
                    negativePrompt += ", " + prompt
                else:
                    negativePrompt += prompt
            else:
                Print.error("\nPrompt file was empty and was skipped: " + filePath)
        if Util.checkEmptyString(negativePrompt):
            Util.printInfo("\nNegative prompt path was provided, but the file was empty.\nNot using a negative prompt.")
    return negativePrompt


def submenuImageSingle():
    positivePrompt = getPositivePrompt()
    if not Util.checkEmptyString(positivePrompt):
        negativePrompt = getNegativePrompt()

        def menu():
            seed = Util.setOrPresetValue(
                "Enter an image seed (eg. 1234567890)",
                Util.getRandomSeed(),
                Util.intVerifier,
                "random",
                "Using a random seed",
                "The seed you entered is invalid - using a random seed!"
            )

            Util.startTimer(0)
            imageResponse = TextToImage.getTextToImageResponse(positivePrompt, negativePrompt, seed, False, "")
            if imageResponse is not None:
                Print.response("\n" + imageResponse, "\n")
            else:
                Print.error("\nError generating image.\n")
            Util.endTimer(0)

            if not Util.printYNQuestion("Do you want to regenerate the image with the same prompt?") == 0:
                Print.generic("\nReturning to menu.\n")
                return
            Print.generic("\nUsing same prompt.\n")
            menu()
            return
        menu()
    else:
        Print.error("\nImage prompt was empty - returning to image menu.\n")
    return


def submenuImageEndless():
    positivePrompt = getPositivePrompt()
    if not Util.checkEmptyString(positivePrompt):
        negativePrompt = getNegativePrompt()
        maxImages = Util.printInput("Enter number of images to do (or leave empty for infinite)")
        if len(maxImages) > 0 and Util.intVerifier(maxImages)[1]:
            maxImages = Util.intVerifier(maxImages)[0]
        else:
            Print.error("\nInvalid number - using infinite\n")
            maxImages = 0
        imagesQueued = 0
        imagesCompleted = 0

        Util.clearWindowIfAllowed()
        Print.generic(
            "\n(Press [" + Util.getKeybindStopName() + "] at any time to stop image generation.)\n"
            "\n"
            "\nPositive prompt:\n" + positivePrompt + "\n"
        )

        if len(negativePrompt) > 0:
            Print.generic("Negative prompt:\n" + negativePrompt + "\n")

        Print.generic(
            "Image Settings:\n"
            "Dimensions (WxH): " + Configuration.getConfig("image_size") + "\n"
            "Step: " + str(Configuration.getConfig("image_step")) + "\n"
            "Clip Skip: " + str(Configuration.getConfig("image_clipskip")) + "\n"
            "Images to Generate: " + (str(maxImages) if maxImages > 0 else "Infinite") + "\n"
        )

        Util.setShouldInterruptCurrentOutputProcess(False)
        endlessImageFailed = False
        stopAllWorkersGracefully = False
        threads = {}

        def canStartWorker():
            nonlocal endlessImageFailed, imagesQueued, maxImages
            if not endlessImageFailed and \
               not stopAllWorkersGracefully and \
               not Util.getShouldInterruptCurrentOutputProcess() and \
               (imagesQueued < maxImages or maxImages == 0):
                return True
            return False

        def worker(threadIdIn):
            nonlocal endlessImageFailed, imagesQueued, imagesCompleted, maxImages, stopAllWorkersGracefully, threads
            if canStartWorker():
                imagesQueued += 1
                isMultiWorker = (threadIdIn != "single_worker")

                threads[threadIdIn] = True
                imageSeed = Util.getRandomSeed()
                threadTic = Time.perf_counter()
                if isMultiWorker:
                    Util.printDebug("\n[" + str(threadIdIn) + "]: Worker started at: " + Util.getTimeString())
                    workerId = threadIdIn
                else:
                    Util.printDebug("\nWorker started at: " + Util.getTimeString())
                    workerId = ""
                imageResponse = TextToImage.getTextToImageResponse(positivePrompt, negativePrompt, imageSeed, True, workerId)
                if imageResponse is not None:
                    imagesCompleted += 1
                    if isMultiWorker:
                        Print.response("\n[" + threadIdIn + "]: Image created: " + imageResponse + "\n", "\n")
                    else:
                        Print.response("\nImage created: " + imageResponse + "\n", "\n")
                    if maxImages > 0:
                        Util.printInfo("\nCompleted image: " + str(imagesCompleted) + "/" + str(maxImages) + "\n")
                else:
                    Print.error("\nError generating image - stopping workers.\n")
                    endlessImageFailed = True

                threadToc = Time.perf_counter()
                Util.printDebug(f"\n{threadToc - threadTic:0.3f} seconds (Completed at: " + Util.getTimeString() + ")")
                Print.separator()
                threads[threadIdIn] = False
                if canStartWorker():
                    worker(threadIdIn)
                else:
                    stopAllWorkersGracefully = True
                    Print.generic("\nWorker stopped: " + threadIdIn)
            return

        def checkForRunningThread():
            for isRunning in threads.values():
                if isRunning:
                    return True
            return False

        Print.generic("")

        matchedServerModels = Model.getServerHasImageModels(Configuration.getConfig("default_text_to_image_model"))
        if matchedServerModels is not None and len(matchedServerModels) > 0:
            for model in matchedServerModels:
                theModel = model.split(Configuration.getConfig("default_text_to_image_model") + "-")
                if len(theModel) > 1:
                    threads[theModel[1]] = False

        if len(threads) > 1:
            Print.generic("\nAvailable Workers:")
            for t in threads.keys():
                Print.generic(t)
            Print.generic("\n")
            Print.separator()
        else:
            if len(threads) == 0:
                threads["single_worker"] = False
            Util.printDebug("\nUsing single worker.")

        for threadId, isRunning in threads.items():
            if not isRunning:
                Threading.Thread(target=worker, args=(threadId,)).start()

        while True:
            if endlessImageFailed:
                if not checkForRunningThread():
                    Print.error("\nA worker has failed to generate an image - returning to image menu.\n")
                    break
            elif Util.getShouldInterruptCurrentOutputProcess():
                if not checkForRunningThread():
                    Print.generic("\nExiting continuous image generation - returning to image menu.\n")
                    break
            elif stopAllWorkersGracefully:
                if not checkForRunningThread():
                    Print.generic("\nExiting continuous image generation - returning to image menu.\n")
                    break
            Time.sleep(0.5)
    else:
        Print.error("\nImage prompt was empty - returning to image menu.\n")
    Util.setShouldInterruptCurrentOutputProcess(True)
    return


def submenuImageToImage():
    positivePrompt = Util.printInput("Enter prompt (or leave blank to skip)")
    negativePrompt = Util.printInput("Enter negative prompt (or leave blank to skip)")
    filePath = Util.printInput("Enter file path")
    if len(filePath) > 0:
        seed = Util.setOrPresetValue(
            "Enter an image seed (eg. 1234567890)",
            Util.getRandomSeed(),
            Util.intVerifier,
            "random",
            "Using a random seed",
            "The seed you entered is invalid - using a random seed!"
        )
        Print.generic("\nGetting response...\n")
        result = ImageToImage.getImageToImageResponse(positivePrompt, negativePrompt, filePath, seed)

        if result is not None:
            Print.response("\nImage created: " + result + "\n", "\n")
        else:
            Print.error("\nError generating image.\n")
    else:
        Print.error("\nFile path was empty - returning to image menu.\n")
    return


def submenuImageToText():
    # TODO: leave prompt blank for basic image transcription
    prompt = Util.printInput("Enter prompt")
    if len(prompt) > 0:
        filePath = Util.printInput("Enter file path")
        if len(filePath) > 0:
            filePath = Util.getFilePathFromPrompt(filePath)
            if len(filePath) == 1:
                filePath = filePath[0]
                if Operation.fileExists(filePath):
                    Print.generic("\nGetting response...\n")
                    result = ImageToText.getImageToTextResponse(prompt, filePath)
                    if result is not None:
                        Print.response("\n" + result + "\n", "\n")
                    else:
                        Print.error("\nNo result from server.\n")
                else:
                    Print.error("\nFile cannot be found - exiting.\n")
            else:
                Print.error("\nMultiple files were given - exiting.\n")
        else:
            Print.error("\nFile path cannot be empty - exiting.\n")
    else:
        Print.error("\nPrompt cannot be empty - exiting.\n")
    return


def submenuImageToVideo():
    prompt = "<None>"
    filePath = Util.printInput("Enter file path")
    if len(filePath) > 0:
        seed = Util.setOrPresetValue(
            "Enter an image seed (eg. 1234567890)",
            Util.getRandomSeed(),
            Util.intVerifier,
            "random",
            "Using a random seed",
            "The seed you entered is invalid - using a random seed!"
        )
        Print.generic("\nGetting response...\n")
        result = ImageToVideo.getImageToVideoResponse(prompt, filePath, seed)

        if result is not None:
            Print.response("\nVideo created: " + result + "\n", "\n")
        else:
            Print.error("\nError generating video.\n")
    else:
        Print.error("\nFile path was empty - returning to image menu.\n")
    return


def submenuImageSettings():
    def menu():
        choices = [
            "Clip Skip",
            "Size",
            "Step",
        ]

        desc = (
            "Clip Skip:  " + str(Configuration.getConfig("image_clipskip")) + "\n"
            "Size (WxH): " + Configuration.getConfig("image_size") + "\n"
            "Step:       " + str(Configuration.getConfig("image_step")) + "\n"
        )

        selection = Util.printMenu("Image Settings", desc, choices)

        if selection is None:
            return
        elif selection == "Clip Skip":
            submenuImageSettingsClipSkip()
        elif selection == "Size":
            submenuImageSettingsSize()
        elif selection == "Step":
            submenuImageSettingsStep()
        else:
            Print.error("\nInvalid selection.\n")
        menu()
        return
    menu()
    Print.generic("\nReturning to image menu.\n")
    return


def submenuImageSettingsClipSkip():
    Print.generic(
        "\nClip skip is how much the model can deviate "
        "from the original prompt.\n"

        "Higher clip skip will deviate more from the prompt.\n"
        "Lower clip skip will stay with the original prompt.\n"
    )

    Configuration.setConfig(
        "image_clipskip",
        Util.setOrDefault(
            "Enter image clip skip value",
            Configuration.getConfig("image_clipskip"),
            Util.intVerifier,
            "Keeping current image clip skip value",
            "Image clip skip value set to",
            "Invalid integer value - keeping current image clip skip value"
        )
    )
    return


def submenuImageSettingsSize():
    Print.generic(
        "\nSet the output image resolution, in [width]x[height].\n"
        "Large images will take more time.\n"
        "Note: Values must be an integer and be divisible by 8.\n"
    )

    Configuration.setConfig(
        "image_size",
        Util.setOrDefault(
            "Enter the new image size",
            Configuration.getConfig("image_size"),
            Util.imageSizeVerifier,
            "Keeping current image size",
            "Image size set to",
            "Resolution is not in the correct format, or is not divisible by 8\nKeeping current image size"
        )
    )
    return


def submenuImageSettingsStep():
    Print.generic(
        "\nSteps is the number of refinement "
        "iterations to do on a given image.\n"

        "More steps usually result in better images, "
        "but with gradual diminishing returns.\n"

        "Higher values will negatively affect "
        "processing time with large images.\n"
    )

    Configuration.setConfig(
        "image_step",
        Util.setOrDefault(
            "Enter image step value",
            Configuration.getConfig("image_step"),
            Util.intVerifier,
            "Keeping current image step value",
            "Image step value set to",
            "Invalid integer value - keeping current image step value"
        )
    )
    return


def __cleanupPromptFileString(stringIn):
    if stringIn is None:
        return None
    else:
        while "\n\n" in stringIn:
            stringIn = stringIn.replace("\n\n", "\n")
        while "  " in stringIn:
            stringIn = stringIn.replace("  ", " ")
        stringIn = stringIn.replace(" \n", " ")
        stringIn = stringIn.replace("\n", " ")
        return stringIn.strip()
