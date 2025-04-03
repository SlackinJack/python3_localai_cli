# modules.command


import os as OS


import modules.string.Path as Path
import modules.Conversation as Conversation
import modules.Print as Print
import modules.Util as Util


def commandConversation():
    convoList = ["*** [Random Name] ***"]

    for conversation in OS.listdir(Path.CONVERSATIONS_FILE_PATH):
        if conversation.endswith(".convo"):
            convoName = conversation.replace(".convo", "")
            convoList.append(convoName)

    choices = convoList

    def verifier(convoNameIn):
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
            conversationName = verifier(selection)
            Conversation.setConversation(conversationName)
            Print.green("\nConversation set to: " + conversationName + "\n")
        else:
            Print.error("\nInvalid selection - returning to menu.\n")
    else:
        Print.red("\nKeeping current conversation: " + Conversation.getConversationName() + "\n")
    return
