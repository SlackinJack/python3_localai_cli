# modules.command


import modules.Configuration as Configuration
import modules.Conversation as Conversation
import modules.Model as Model
import modules.Print as Print
import modules.Util as Util


def commandMessages():
    promptHistory = []
    currentConversationName = Conversation.getConversationName()
    conversation = Conversation.getConversation(currentConversationName)
    chatFormat = Model.getChatModelFormat(Configuration.getConfig("default_text_to_text_model"))
    promptHistory = Conversation.getPromptHistoryFromConversation(conversation, chatFormat)
    if len(promptHistory) == 0:
        Print.generic("\nThere are no chat messages in the current conversation.\n")
    else:
        Print.generic("\nChat history:")
        for msg in promptHistory:
            if "system" in msg["role"].lower(): Print.generic("\n" + msg["content"])
            else:                               Print.response("\n" + msg["content"], "\n")
        Print.generic("")
    return
