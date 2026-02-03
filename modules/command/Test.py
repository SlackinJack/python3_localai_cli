# package modules.command


import modules.connection.response.TextToAudio as TextToAudio
import modules.connection.response.TextToImage as TextToImage
import modules.connection.response.TextToText as TextToText
import modules.Conversation as Conversation
import modules.core.Configuration as Configuration
import modules.core.Print as Print
import modules.core.Util as Util
import modules.PromptHandler as PromptHandler
import modules.string.Path as Path
import modules.Trigger as Trigger


def command():
    Print.generic("We will run a few tests to ensure everything works with the server...and in the script! :)")
    Print.generic("(This may take a really long time.)")

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
        Print.generic("Copied the current settings.")

        seed = 1
        Util.startTimer(0)
        testsPassed = 0
        target = 0

        Print.separator()

        # test basic text-to-text
        target += 1
        Util.startTimer(1)
        Print.generic("Testing Text-to-Text...")
        prompt = "Hi there, how are you?"
        try:
            for _ in TextToText.getStreamedResponse(prompt, seed, [], False, False, False, ""):
                pass
            Print.green("Chat completion test passed!")
            testsPassed += 1
        except:
            Util.printError("Chat completion test failed!")
        Util.endTimer(1)

        Print.separator()

        # test text-to-text chat history
        target += 1
        Util.startTimer(1)
        Print.generic("Testing chat history...")
        Configuration.setConfig("enable_chat_history_consideration", True)
        testConversationName = "test_conversation_" + Conversation.getRandomConversationName()
        Conversation.setConversation(testConversationName)
        userContent = "What is the Eiffel Tower?"
        Conversation.writeConversation(testConversationName, "USER: " + userContent)
        assistantContent = "The Eiffel Tower is a famous iron lattice tower located in Paris, France."
        Conversation.writeConversation(testConversationName, "ASSISTANT: " + assistantContent)
        prompt = "Tell me what we were just talking about previously."
        try:
            for _ in TextToText.getStreamedResponse(prompt, seed, [], False, False, False, ""):
                pass
            Print.green("Chat history test passed!")
            testsPassed += 1
        except:
            Util.printError("Chat history test failed!")
        Configuration.setConfig("enable_chat_history_consideration", False)
        Util.endTimer(1)

        Print.separator()

        # test text-to-text model switcher
        target += 1
        Util.startTimer(1)
        Print.generic("Testing model switcher...")
        Configuration.setConfig("enable_automatic_model_switching", True)
        try:
            for _ in TextToText.getTextToTextResponseModel("Write a simple python function that prints \"Hello, World!\"", seed):
                pass
            Print.green("Model switcher test passed!")
            testsPassed += 1
        except:
            Util.printError("Model switcher test failed!")
        Configuration.setConfig("enable_automatic_model_switching", False)
        Util.endTimer(1)

        Print.separator()

        # test text-to-text functions
        target += 1
        Util.startTimer(1)
        Print.generic("Testing functions...")
        Configuration.setConfig("enable_functions", True)
        Configuration.setConfig("enable_internet", True)
        try:
            PromptHandler.handlePrompt(["Search the internet for information on Big Ben."], 1)
            Print.green("Functions test passed!")
            testsPassed += 1
        except:
            Util.printError("Functions test failed!")
        Configuration.setConfig("enable_functions", False)
        Configuration.setConfig("enable_internet", False)
        Util.endTimer(1)

        Print.separator()

        # test open-file operations (audio-to-text, image-to-text, text-to-text)
        for testFile in Path.TESTS_FILE_PATH:
            target += 1
            Util.startTimer(1)
            Print.generic("Testing input file: " + testFile)
            try:
                PromptHandler.handlePrompt(Trigger.checkTriggers("Tell me about the contents of the provided file " + testFile + ""), 1)
                Print.green("Input file test " + testFile + " passed!")
                testsPassed += 1
            except:
                Util.printError("Input file test " + testFile + " failed!")
            Util.endTimer(1)
            Print.separator()

        # test text-to-text with internet
        target += 1
        Util.startTimer(1)
        Print.generic("Testing internet browse...")
        try:
            PromptHandler.handlePrompt(Trigger.checkTriggers("Summarize this webpage https://example.com/"), 1)
            Print.green("Internet browse test passed!")
            testsPassed += 1
        except:
            Util.printError("Internet browse test failed!")
        Util.endTimer(1)

        Print.separator()

        # test text-to-test with youtube transcribe
        target += 1
        Util.startTimer(1)
        Print.generic("Testing YouTube...")
        try:
            PromptHandler.handlePrompt(Trigger.checkTriggers("Summarize this YouTube video https://www.youtube.com/watch?v=TVLYtiunWJA"), 1)
            Print.green("YouTube test passed!")
            testsPassed += 1
        except:
            Util.printError("YouTube test failed!")
        Util.endTimer(1)

        Print.separator()

        # test text-to-image
        target += 1
        Util.startTimer(1)
        Print.generic("Testing Text-to-Image...")
        result = TextToImage.getResponse(0, "A red apple on a wooden desk.", "", seed, 0, None)
        if result is not None:
            Print.green("Text-to-Image test passed!")
            testsPassed += 1
        else:
            Util.printError("Text-to-Image test failed!")
        Util.endTimer(1)

        Print.separator()

        # test text-to-audio
        target += 1
        Util.startTimer(1)
        Print.generic("Testing Text-to-Audio...")
        result = TextToAudio.getResponse("Hi there, it is so nice to meet you!", False)
        if result is not None:
            Print.green("Text-to-Audio test passed!")
            testsPassed += 1
        else:
            Util.printError("Text-to-Audio test failed!")
        Util.endTimer(1)

        Print.separator()

        if target == testsPassed:   Print.green("All tests passed!")
        else:                       Util.printError("Some tests failed - read log for details.")
        Util.endTimer(0)

        Configuration.setConfig("read_outputs_with_tts", currentReadOutputsSetting)
        Configuration.setConfig("enable_functions", currentFunctionsSetting)
        Configuration.setConfig("enable_internet", currentInternetSetting)
        Configuration.setConfig("enable_automatic_model_switching", currentModelSwitchSetting)
        Configuration.setConfig("enable_chat_history_consideration", currentHistorySetting)
        Conversation.setConversation(currentConversationName)
        Print.separator()
        Print.generic("Settings reverted.")
    else:
        Print.generic("Returning to menu.")
    return
