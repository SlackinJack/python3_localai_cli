# package modules.connection.request


import openai as OpenAI


import modules.connection.request.Request as Request
import modules.string.Endpoint as Endpoint
import modules.core.Configuration as Configuration
import modules.core.typecheck.TypeCheck as TypeCheck
import modules.core.typecheck.Types as Types
import modules.core.Util as Util


def createRequest(dataIn):
    TypeCheck.enforce(dataIn, Types.DICTIONARY)

    # language              str
    # n                     int
    # top_p                 float
    # top_k                 float
    # max_tokens            int
    # echo                  bool
    # batch                 int
    # ignore_eos            bool
    # repeat_penalty        int/float
    # repeat_last_n         int/float
    # tfz                   ?
    # typical_p             ? (int/float)
    # rope_freq_base        int/float
    # rope_freq_scale       int/float
    # use_fast_tokenizer    bool
    # instruction           str
    # input                 ? (str)
    # stop                  ? (str)
    # mode                  int
    # backend               str
    # model_base_name       str

    while not Util.getShouldInterruptCurrentOutputProcess():
        result = Request.sendRequest(Util.getRandomSeed(), Endpoint.TEXT_ENDPOINT, dataIn, False, True)
        if result is not None:
            if result.get("choices") is not None:
                choices = result["choices"]
                if len(choices) > 0:
                    choices0 = choices[0]
                    if choices0.get("message") is not None:
                        message = choices0["message"]
                        message["usage"] = result["usage"]
                        return message
        return None
    return None


# Only used for streaming chat
def createStreamedRequest(dataIn):
    TypeCheck.enforce(dataIn, Types.DICTIONARY)

    # handled in response
    # while not Util.getShouldInterruptCurrentOutputProcess():
    try:
        OpenAI.api_key = "sk-xxx"
        OpenAI.api_base = Configuration.getConfig("address")  # openai <= 0.28.0
        OpenAI.base_url = Configuration.getConfig("address")  # openai > 0.28.0

        model = dataIn.get("model", None)
        messages = dataIn.get("messages", None)
        seed = dataIn.get("seed", None)
        stream = True
        requestTimeout = 99999
        streamOptions = {"include_usage": True}

        Request.updateLastUsed(1, model)

        requestDict = {
            "model": model,
            "messages": messages,
            "seed": seed,
            "stream": stream,
            "request_timeout": requestTimeout,
            "stream_options": streamOptions,
        }

        Util.printDebug("\nSending request to: " + Configuration.getConfig("address"))
        Util.printDump("\nRequest Data:\n" + Util.formatJSONToString(requestDict))

        return OpenAI.ChatCompletion.create(
            model=model,
            messages=messages,
            seed=seed,
            stream=stream,
            request_timeout=requestTimeout,
            stream_options=streamOptions,
        )
    except Exception as e:
        Util.printError("\nError communicating with server.")
        Util.printError(str(e))
    return None
