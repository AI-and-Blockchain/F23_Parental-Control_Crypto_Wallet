# this file is meant to connect the webserver to the FedLab and blockchain components

# imports
# from ..blockchain import contract_test as contract


# region chatGPT code
from openai import OpenAI
import os
import json

client = OpenAI(
    api_key = os.getenv('apitoken') or json.load(open('./secrets/config.json'))['APITOKEN']
)

STARTCONVOPROMPT = [{"role": "system", "content": "you are an AI chat bot that is helping a user learn more about their crypto wallet and crypto currencies as a whole."}]
chat_logs = dict()


def callAPI(chatId, uinp):
    try:
        if len(uinp) == 0:
            return 'Please provide a message!'
        
        # get the previous data or init
        if chatId not in chat_logs: return
        chat_logs[chatId].append({"role": "user", "content": "user: " + uinp})

        chat_completion = client.chat.completions.create(
            messages=chat_logs[chatId],
            model="gpt-3.5-turbo",
            stream=True
        )

        retStr = ''
        for part in chat_completion:
            retStr += part.choices[0].delta.content or ""

        chat_logs[chatId].append({"role": "assistant", "content": retStr})

        return retStr, chat_logs[chatId]
    except Exception as err:
        return str(err)
    
# endregion

# region fedlab
# from ai import model as fedImp
# model = fedImp.init_model()

# a = [0.00016591157871593997,-0.4196428571428571,-0.9765157558835261,-0.9703491389589427,-0.33342069786393624]  # 1
# b = [0.0005280176532643606,-0.4196428571428571,-0.9759910346268543,-0.9322903614990381,-0.49961232113912235]  # 1
# c = [9.351468739346202e-05,-0.4196428571428571,-0.979564362641746,-0.798657369127207,-0.8020313981902603]  # 3

# outp = fedImp.computePoint(model, b)
# print(outp)

# endregion
