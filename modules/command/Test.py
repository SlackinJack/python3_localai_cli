# modules.command


import modules.connection.response.TextToAudio as TextToAudio
import modules.connection.response.TextToImage as TextToImage
import modules.connection.response.TextToText as TextToText
import modules.string.Path as Path
import modules.Configuration as Configuration
import modules.Conversation as Conversation
import modules.Print as Print
import modules.PromptHandler as PromptHandler
import modules.Trigger as Trigger
import modules.Util as Util


def commandTest():
    Print.generic(
        "\nWe will run a few tests to ensure everything works with the server...and in the script! :)\n"
        "(This may take a really long time.)\n"
    )

    if Util.printYNQuestion("Do you want to continue?") == 0:
        currentReadOutputsSetting = Configuration.getConfig("read_outputs")
        currentFunctionsSetting = Configuration.getConfig("enable_functions")
        currentInternetSetting = Configuration.getConfig("enable_internet")
        currentModelSwitchSetting = Configuration.getConfig("enable_automatic_model_switching")
        currentHistorySetting = Configuration.getConfig("enable_chat_history_consideration")
        currentConversationName = Conversation.getConversationName()
        Configuration.setConfig("read_outputs_with_tts", False)
        Configuration.setConfig("enable_functions", False)
        Configuration.setConfig("enable_internet", False)
        Configuration.setConfig("enable_automatic_model_switching", False)
        Configuration.setConfig("enable_chat_history_consideration", False)
        Conversation.setConversation("test_conversation_" + Conversation.getRandomConversationName())
        Print.generic("\nCopied the current settings.\n")

        seed = 1
        Util.startTimer(0)
        testsPassed = 0
        target = 0

        Print.separator()

        target += 1
        Util.startTimer(1)
        Print.generic("\nTesting Text-to-Text...")
        result = TextToText.getTextToTextResponseStreamed("Hi there, how are you?", seed, [], False)
        if result is not None:
            Print.green("\nChat completion test passed!")
            testsPassed += 1
        else:
            Print.error("\nChat completion test failed!")
        Util.endTimer(1)

        Print.separator()

        target += 1
        Util.startTimer(1)
        Print.generic("\nTesting chat history...")
        Configuration.setConfig("enable_chat_history_consideration", True)
        testConversationName = "test_conversation_" + Conversation.getRandomConversationName()
        Conversation.setConversation(testConversationName)
        userContent = "What is the Eiffel Tower?"
        Conversation.writeConversation(testConversationName, "USER: " + userContent)
        assistantContent = "The Eiffel Tower is a famous iron lattice tower located in Paris, France."
        Conversation.writeConversation(testConversationName, "ASSISTANT: " + assistantContent)
        result = TextToText.getTextToTextResponseStreamed("Could you tell me what we were just talking about previously?", seed, [], False)
        Configuration.setConfig("enable_chat_history_consideration", False)
        if result is not None:
            Print.green("\nChat history test passed!")
            testsPassed += 1
        else:
            Print.error("\nChat history test failed!")
        Util.endTimer(1)

        Print.separator()

        target += 1
        Util.startTimer(1)
        Print.generic("\nTesting model switcher...")
        Configuration.setConfig("enable_automatic_model_switching", True)
        result = TextToText.getTextToTextResponseModel("Write a simple python function that prints \"Hello, World!\"", seed)
        Configuration.setConfig("enable_automatic_model_switching", False)
        if result is not None:
            Print.green("\nModel switcher test passed!")
            testsPassed += 1
        else:
            Print.error("\nModel switcher test failed!")
        Util.endTimer(1)

        Print.separator()

        target += 1
        Util.startTimer(1)
        Print.generic("\nTesting functions...")
        Configuration.setConfig("enable_functions", True)
        Configuration.setConfig("enable_internet", True)
        result = TextToText.getTextToTextResponseFunctions("Search the internet for information on Big Ben.", seed, [])
        Configuration.setConfig("enable_functions", False)
        Configuration.setConfig("enable_internet", False)
        if result is not None:
            Print.green("\nFunctions test passed!")
            testsPassed += 1
        else:
            Print.error("\nFunctions test failed!")
        Util.endTimer(1)

        Print.separator()

        for testFile in Path.TESTS_FILE_PATH:
            target += 1
            Util.startTimer(1)
            Print.generic("\nTesting input file: " + testFile)
            result = PromptHandler.handlePrompt(Trigger.checkTriggers("Tell me about the contents of the provided file '" + testFile + "'"), 1)
            if result is not None:
                Print.green("\nInput file test " + testFile + " passed!")
                testsPassed += 1
            else:
                Print.error("\nInput file test " + testFile + " failed!")
            Util.endTimer(1)
            Print.separator()

        target += 1
        Util.startTimer(1)
        Print.generic("\nTesting internet browse...")
        result = PromptHandler.handlePrompt(Trigger.checkTriggers("Summarize this webpage https://example.com/"), 1)
        if result is not None:
            Print.green("\nInternet browse test passed!")
            testsPassed += 1
        else:
            Print.error("\nInternet browse test failed!")
        Util.endTimer(1)

        Print.separator()

        target += 1
        Util.startTimer(1)
        Print.generic("\nTesting YouTube...")
        result = PromptHandler.handlePrompt(Trigger.checkTriggers("Summarize this YouTube video https://www.youtube.com/watch?v=TVLYtiunWJA"), 1)
        if result is not None:
            Print.green("\nYouTube test passed!")
            testsPassed += 1
        else:
            Print.error("\nYouTube test failed!")
        Util.endTimer(1)

        Print.separator()

        target += 1
        Util.startTimer(1)
        Print.generic("\nTesting Text-to-Image...")
        result = TextToImage.getTextToImageResponse("A red apple on a wooden desk.", "", seed, False, "")
        if result is not None:
            Print.green("\nText-to-Image test passed!")
            testsPassed += 1
        else:
            Print.error("\nText-to-Image test failed!")
        Util.endTimer(1)

        Print.separator()

        target += 1
        Util.startTimer(1)
        Print.generic("\nTesting Text-to-Audio...")
        result = TextToAudio.getTextToAudioResponse("Hi there, it is so nice to meet you!", False)
        if result is not None:
            Print.green("\nText-to-Audio test passed!")
            testsPassed += 1
        else:
            Print.error("\nText-to-Audio test failed!")
        Util.endTimer(1)

        Print.separator()

        if target == testsPassed:
            Print.green("\nAll tests passed!")
        else:
            Print.error("\nSome tests failed - read log for details.")
        Util.endTimer(0)

        Configuration.setConfig("read_outputs_with_tts", currentReadOutputsSetting)
        Configuration.setConfig("enable_functions", currentFunctionsSetting)
        Configuration.setConfig("enable_internet", currentInternetSetting)
        Configuration.setConfig("enable_automatic_model_switching", currentModelSwitchSetting)
        Configuration.setConfig("enable_chat_history_consideration", currentHistorySetting)
        Conversation.setConversation(currentConversationName)
        Print.separator()
        Print.generic("\nSettings reverted.\n")
    else:
        Print.generic("\nReturning to menu.\n")
    return
