# package modules.command


import os as OS


import modules.Conversation as Conversation
import modules.core.Print as Print
import modules.core.Util as Util
import modules.string.Path as Path


def command():
    convoList = ["*** [Random Name] ***"]

    for conversation in OS.listdir(Path.CONVERSATIONS_FILE_PATH):
        if conversation.endswith(".convo"):
            convoName = conversation.replace(".convo", "")
            convoList.append(convoName)
    choices = convoList

    def __verifier(convoNameIn):
        if len(convoNameIn) > 0:
            if convoNameIn == "*** [Random Name] ***":
                return Conversation.getRandomConversationName()
            else:
                for conversation in convoList:
                    if convoNameIn in conversation:
                        return conversation
        return convoNameIn

    selection = Util.printMenu("Conversations available", "", choices)
    if selection is not None:
        if len(selection) > 0:
            conversationName = __verifier(selection)
            Conversation.setConversation(conversationName)
            Print.green("Conversation set to: " + conversationName)
        else:
            Util.printError("Invalid selection - returning to menu.")
    else:
        Print.red("Keeping current conversation: " + Conversation.getConversationName())
    return
