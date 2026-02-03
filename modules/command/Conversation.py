# package modules.command


import os as OS


import modules.Conversation as Conversation
import modules.core.Print as Print
import modules.core.Util as Util
import modules.string.Path as Path


def __buildConversationList():
    convoList = ["*** [Random Name] ***"]

    for conversation in OS.listdir(Path.CONVERSATIONS_FILE_PATH):
        if conversation.endswith(".convo"):
            convoName = conversation.replace(".convo", "")
            convoList.append(convoName)
    return convoList


def command():
    choices = __buildConversationList()

    selection = Util.printMenu("Conversations available", "", choices)
    if selection is not None:
        if len(selection) > 0:
            conversationName = changeConversation(selection)
            Print.green("Conversation set to: " + conversationName)
        else:
            Util.printError("Invalid selection - returning to menu.")
    else:
        Print.red("Keeping current conversation: " + Conversation.getConversationName())
    return


def changeConversation(conversationNameIn):
    choices = __buildConversationList()

    def __verifier(convoNameIn):
        if len(convoNameIn) > 0:
            if convoNameIn == "*** [Random Name] ***":
                return Conversation.getRandomConversationName()
            else:
                for conversation in choices:
                    if convoNameIn in conversation:
                        return conversation
        return convoNameIn

    conversationName = __verifier(conversationNameIn)
    Conversation.setConversation(conversationName)
    return conversationName
