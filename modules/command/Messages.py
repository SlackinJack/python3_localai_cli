# package modules.command


import modules.Conversation as Conversation
import modules.core.Configuration as Configuration
import modules.core.Print as Print
import modules.Model as Model


def command():
    for _ in messagesServer():
        pass
    return


def messagesServer():
    promptHistory = []
    currentConversationName = Conversation.getConversationName()
    conversation = Conversation.getConversation(currentConversationName)
    chatFormat = Model.getChatModelFormat(Configuration.getConfig("default_text_to_text_model"))
    promptHistory = Conversation.getPromptHistoryFromConversation(conversation, "alpaca")
    if len(promptHistory) == 0:
        yield from Print.generic("There are no chat messages in the current conversation.")
    else:
        yield from Print.generic("Chat history:")
        for msg in promptHistory:
            if "system" in msg["role"].lower():
                yield from Print.generic(msg["content"])
            elif "user" in msg["role"].lower():
                yield from Print.generic(msg["content"])
            else:
                yield from Print.response(msg["content"], "\n")
