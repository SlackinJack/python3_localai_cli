# package modules.command


import threading as Threading
import time as Time


import modules.connection.response.ImageToImage as ImageToImage
import modules.connection.response.ImageToText as ImageToText
import modules.connection.response.ImageToVideo as ImageToVideo
import modules.connection.response.TextToImage as TextToImage
import modules.core.file.Operation as Operation
import modules.core.file.Reader as Reader
import modules.core.Configuration as Configuration
import modules.core.Print as Print
import modules.core.typecheck.TypeCheck as TypeCheck
import modules.core.typecheck.Types as Types
import modules.core.Util as Util
import modules.Model as Model
import modules.Trigger as Trigger


def command():
    choices = [
        "Single Image",
        "Endless Images",
        "Image-to-Text",
        "Image-to-Image",
        "Image-to-Video",
        "Settings"
    ]

    def __menu():
        selection = Util.printMenu("Image menu", "", choices)
        if selection is None:               return
        elif selection == "Single Image":   submenuImageSingle()
        elif selection == "Endless Images": submenuImageEndless()
        elif selection == "Image-to-Text":  submenuImageToText()
        elif selection == "Image-to-Image": submenuImageToImage()
        elif selection == "Image-to-Video": submenuImageToVideo()
        elif selection == "Settings":       submenuImageSettings()
        else:                               Util.printError("Invalid selection.")
        __menu()
        return
    __menu()
    Print.generic("Returning to main menu.")
    return


def getPositivePrompt():
    positivePrompt = Util.printInput("Enter positive image prompt, or the path to a prompt (required)")
    if Trigger.checkStringHasFile(positivePrompt):
        theFilePath = Util.getFilePathFromPrompt(positivePrompt)
        positivePrompt = ""
        for filePath in theFilePath:
            contents = Reader.getFileContents(filePath, False)
            if contents is not None:
                prompt = __cleanupPromptFileString(contents)
                if not Util.checkEmptyString(prompt):
                    if len(positivePrompt) > 0:
                        positivePrompt += ", " + prompt
                    else:
                        positivePrompt += prompt
                else:
                    Util.printError("Prompt file was empty and was skipped: " + filePath)
            else:
                Util.printError("Prompt file does not exist and was skipped: " + filePath)
    return positivePrompt


def getNegativePrompt():
    if Configuration.getConfig("no_negative_prompts"):
        Util.printDebug("Skipping negative prompt.")
        return ""

    negativePrompt = Util.printInput("Enter negative image prompt, or the path to a prompt (or leave empty to skip)")
    if Trigger.checkStringHasFile(negativePrompt):
        theFilePath = Util.getFilePathFromPrompt(negativePrompt)
        negativePrompt = ""
        for filePath in theFilePath:
            contents = Reader.getFileContents(filePath, False)
            if contents is not None:
                prompt = __cleanupPromptFileString(contents)
                if not Util.checkEmptyString(prompt):
                    if len(negativePrompt) > 0:
                        negativePrompt += ", " + prompt
                    else:
                        negativePrompt += prompt
                else:
                    Util.printError("Prompt file was empty and was skipped: " + filePath)
            else:
                Util.printError("Prompt file does not exist and was skipped: " + filePath)
        if Util.checkEmptyString(negativePrompt):
            Util.printInfo("Negative prompt path was provided, but the file was empty.")
            Util.printInfo("Not using a negative prompt.")
    return negativePrompt


def submenuImageSingle():
    positivePrompt = getPositivePrompt()
    if not Util.checkEmptyString(positivePrompt):
        negativePrompt = getNegativePrompt()

        def __menu():
            seed = Util.setOrPresetValue(
                "Enter an image seed (eg. 1234567890)",
                Util.getRandomSeed(),
                Util.intVerifier,
                "random",
                "Using a random seed",
                "The seed you entered is invalid - using a random seed!"
            )

            Util.setShouldInterruptCurrentOutputProcess(False)
            Util.startTimer(0)
            imageResponse = TextToImage.getResponse(Util.getRandomSeed(), positivePrompt, negativePrompt, seed, 0, None)
            Util.endTimer(0)
            Util.setShouldInterruptCurrentOutputProcess(True)
            if imageResponse is not None:
                Print.response("" + imageResponse, "\n")
            else:
                Util.printError("Error generating image.")

            if not Util.printYNQuestion("Do you want to regenerate the image with the same prompt?") == 0:
                Print.generic("Returning to menu.")
                return
            Print.generic("Using same prompt.")
            __menu()
            return
        __menu()
    else:
        Util.printError("Image prompt was empty - returning to image menu.")
    return


def submenuImageEndless():
    positivePrompt = getPositivePrompt()
    if not Util.checkEmptyString(positivePrompt):
        negativePrompt = getNegativePrompt()
        maxImages = Util.printInput("Enter number of images to do (or leave empty for infinite)")
        if len(maxImages) > 0 and Util.intVerifier(maxImages)[1]:
            maxImages = Util.intVerifier(maxImages)[0]
        else:
            Util.printError("Invalid number - using infinite")
            maxImages = 0
        imagesQueued = 0
        imagesCompleted = 0

        Util.clearWindowIfAllowed()
        Print.generic("(Press [" + Util.getKeybindStopName() + "] at any time to stop image generation.)")
        Print.generic("Positive prompt:" + positivePrompt)

        if len(negativePrompt) > 0:
            Print.generic("Negative prompt:" + negativePrompt)

        Print.generic("Image Settings:")
        Print.generic("Dimensions (WxH): " + Configuration.getConfig("image_size"))
        Print.generic("Step: " + str(Configuration.getConfig("image_step")))
        Print.generic("Clip Skip: " + str(Configuration.getConfig("image_clipskip")))
        Print.generic("Images to Generate: " + (str(maxImages) if maxImages > 0 else "Infinite"))

        Util.setShouldInterruptCurrentOutputProcess(False)
        endlessImageFailed = False
        stopAllWorkersGracefully = False
        threads = {}
        requestId = Util.getRandomSeed()

        def __canStartWorker():
            nonlocal endlessImageFailed, imagesQueued, maxImages
            if not endlessImageFailed and \
               not stopAllWorkersGracefully and \
               not Util.getShouldInterruptCurrentOutputProcess() and \
               (imagesQueued < maxImages or maxImages == 0):
                return True
            return False

        def __worker(threadIdIn):
            nonlocal endlessImageFailed, imagesQueued, imagesCompleted, maxImages, stopAllWorkersGracefully, threads
            if __canStartWorker():
                imagesQueued += 1
                isMultiWorker = (threadIdIn != "single_worker")

                threads[threadIdIn] = True
                imageSeed = Util.getRandomSeed()
                threadTic = Time.perf_counter()
                if isMultiWorker:
                    Util.printDebug("[" + str(threadIdIn) + "]: Worker started at: " + Util.getTimeString())
                    workerId = threadIdIn
                else:
                    Util.printDebug("Worker started at: " + Util.getTimeString())
                    workerId = ""
                imageResponse = TextToImage.getResponse(requestId, positivePrompt, negativePrompt, imageSeed, 1, workerId)
                if imageResponse is not None:
                    imagesCompleted += 1
                    if isMultiWorker:
                        Print.response("[" + threadIdIn + "]: Image created: " + imageResponse, "\n")
                    else:
                        Print.response("Image created: " + imageResponse, "\n")
                    if maxImages > 0:
                        Util.printInfo("Completed image: " + str(imagesCompleted) + "/" + str(maxImages))
                else:
                    Util.printError("Error generating image - stopping workers.")
                    endlessImageFailed = True

                threadToc = Time.perf_counter()
                Util.printDebug(f"{threadToc - threadTic:0.3f} seconds (Completed at: " + Util.getTimeString() + ")")
                Print.separator()
                threads[threadIdIn] = False
                if __canStartWorker():
                    __worker(threadIdIn)
                else:
                    stopAllWorkersGracefully = True
                    Print.generic("Worker stopped: " + threadIdIn)
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
            Print.generic("Available Workers:")
            for t in threads.keys():
                Print.generic(t)
            Print.separator()
        else:
            if len(threads) == 0:
                threads["single_worker"] = False
            Util.printDebug("Using single worker.")

        for threadId, isRunning in threads.items():
            if not isRunning:
                Threading.Thread(target=__worker, args=(threadId,)).start()

        while True:
            if endlessImageFailed:
                if not checkForRunningThread():
                    Util.printError("A worker has failed to generate an image - returning to image menu.")
                    break
            elif Util.getShouldInterruptCurrentOutputProcess():
                if not checkForRunningThread():
                    Print.generic("Exiting continuous image generation - returning to image menu.")
                    break
            elif stopAllWorkersGracefully:
                if not checkForRunningThread():
                    Print.generic("Exiting continuous image generation - returning to image menu.")
                    break
            Time.sleep(0.5)
    else:
        Util.printError("Image prompt was empty - returning to image menu.")
    Util.setShouldInterruptCurrentOutputProcess(True)
    return


def submenuImageToImage():
    positivePrompt = getPositivePrompt()
    if not Util.checkEmptyString(positivePrompt):
        negativePrompt = getNegativePrompt()
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
            Print.generic("Getting response...")
            result = ImageToImage.getResponse(positivePrompt, negativePrompt, filePath, seed)

            if result is not None:
                Print.response("Image created: " + result, "\n")
            else:
                Util.printError("Error generating image.")
        else:
            Util.printError("File path was empty - returning to image menu.")
    else:
        Util.printError("Image prompt was empty - returning to image menu.")
    return


def submenuImageToText():
    # TODO: leave prompt blank for basic image transcription
    prompt = getPositivePrompt()
    if not Util.checkEmptyString(prompt):
        filePath = Util.printInput("Enter file path")
        if len(filePath) > 0:
            filePath = Util.getFilePathFromPrompt(filePath)
            if len(filePath) == 1:
                filePath = filePath[0]
                if Operation.fileExists(filePath):
                    Print.generic("Getting response...")
                    result = ImageToText.getResponse(prompt, filePath)
                    if result is not None:
                        Print.response(result, "\n")
                    else:
                        Util.printError("No result from server.")
                else:
                    Util.printError("File cannot be found - exiting.")
            else:
                Util.printError("Multiple files were given - exiting.")
        else:
            Util.printError("File path cannot be empty - exiting.")
    else:
        Util.printError("Prompt cannot be empty - exiting.")
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
        Print.generic("Getting response...")
        result = ImageToVideo.getResponse(prompt, filePath, seed)

        if result is not None:
            Print.response(result, "\n")
        else:
            Util.printError("Error generating video.")
    else:
        Util.printError("File path was empty - returning to image menu.")
    return


def submenuImageSettings():
    def __menu():
        choices = [
            "Clip Skip",
            "Size",
            "Step",
        ]

        desc = "Clip Skip:  " + str(Configuration.getConfig("image_clipskip")) + "\n" + "Size (WxH): " + Configuration.getConfig("image_size") + "\n" + "Step:       " + str(Configuration.getConfig("image_step"))
        selection = Util.printMenu("Image Settings", desc, choices)

        if selection is None:           return
        elif selection == "Clip Skip":  submenuImageSettingsClipSkip()
        elif selection == "Size":       submenuImageSettingsSize()
        elif selection == "Step":       submenuImageSettingsStep()
        else:                           Util.printError("Invalid selection.")
        __menu()
        return
    __menu()
    Print.generic("Returning to image menu.")
    return


def submenuImageSettingsClipSkip():
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
    Print.generic("Resolution is in [width]x[height].")

    Configuration.setConfig(
        "image_size",
        Util.setOrDefault(
            "Enter the new image size",
            Configuration.getConfig("image_size"),
            Util.imageSizeVerifier,
            "Keeping current image size",
            "Image size set to",
            "Resolution is not in the correct format, or is not divisible by 8 - keeping current image size."
        )
    )
    return


def submenuImageSettingsStep():
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
    TypeCheck.enforce(stringIn, Types.STRING)
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
