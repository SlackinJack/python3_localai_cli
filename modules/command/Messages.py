# package modules.command


import modules.Conversation as Conversation
import modules.core.Configuration as Configuration
import modules.core.Print as Print
import modules.Model as Model


def command():
    promptHistory = []
    currentConversationName = Conversation.getConversationName()
    conversation = Conversation.getConversation(currentConversationName)
    chatFormat = Model.getChatModelFormat(Configuration.getConfig("default_text_to_text_model"))
    promptHistory = Conversation.getPromptHistoryFromConversation(conversation, chatFormat)
    if len(promptHistory) == 0:
        Print.generic("There are no chat messages in the current conversation.")
    else:
        Print.generic("Chat history:")
        for msg in promptHistory:
            if "system" in msg["role"].lower(): Print.generic( msg["content"])
            else:                               Print.response(msg["content"], "")
        Print.generic("")
    return
