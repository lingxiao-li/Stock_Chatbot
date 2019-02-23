# -*- coding: utf-8 -*-
"""
Created on Wed Feb  6 17:02:02 2019

@author: Lingxiao Li
"""
# import modules
import re
import random
from wxpy import *
from rasa_nlu.training_data import load_data
from rasa_nlu.config import RasaNLUModelConfig
from rasa_nlu.model import Trainer
from rasa_nlu import config
from iexfinance.stocks import Stock
from datetime import datetime
from iexfinance.stocks import get_historical_data
from iexfinance.stocks import get_historical_intraday
import matplotlib.pyplot as plt
# Create a trainer that uses this config
trainer = Trainer(config.load("config_spacy.yml"))

# Load the training data
training_data = load_data('training-data.json')
interpreter = trainer.train(training_data)

# Define the states
INIT=0 
CHOOSE_COMPANY=1
CHOOSE_FUNCTION = 2

# Define the policy rules dictionary
policy_rules = {
    (INIT, "greet"): (INIT, "Hello! I am a robot helping you to check the stock price! What do you want from me?"),
    (INIT, "affirm"): (INIT, "No problem! I'm always ready!"),
    (INIT, "goodbye"): (INIT, "Goodbye, have a nice day!"),
    (INIT, "others"): (INIT, "Sorry, I don't understand what you said, please ask me something about stock."),
    (INIT, "ask_function"): (INIT, "I have three functions now:\n 1. Check the current stock price of a specific company.\n 2. Check the stock price of a company between a priod of time.\n 3. Check the open stock price of a company."),
    (INIT, "choose_company"): (CHOOSE_COMPANY, "Ok, which stock price do you want to check?"),
    (INIT, "get_historical_price"): (CHOOSE_FUNCTION, "Please wait! The data is loading..."),
    (INIT, "get_open_price"): (CHOOSE_FUNCTION, "Please wait! The data is loading..."),
    (INIT, "get_price"): (CHOOSE_FUNCTION, "Please wait! The data is loading..."),
    (CHOOSE_COMPANY, "others"): (CHOOSE_COMPANY, "Sorry, I don't understand what you said, please ask me something about stock."),
    (CHOOSE_COMPANY, "get_price"): (CHOOSE_FUNCTION, "Please wait! The data is loading..."),
    (CHOOSE_COMPANY, "get_historical_price"): (CHOOSE_FUNCTION, "Please wait! The data is loading..."),
    (CHOOSE_COMPANY, "get_open_price"): (CHOOSE_FUNCTION, "Please wait! The data is loading..."),
    (CHOOSE_COMPANY, "ask_function"): (CHOOSE_COMPANY, "I have three functions now:\n 1. Check the current stock price of a specific company.\n 2. Check the stock price of a company between a priod of time.\n 3. Check the open stock price of a company."),  
    (CHOOSE_COMPANY, "greet"): (CHOOSE_COMPANY, "Hello! I am a robot helping you to check the stock price! What do you want from me?"),
    (CHOOSE_COMPANY, "affirm"): (CHOOSE_COMPANY, "No problem! I'm always ready!"),
    (CHOOSE_COMPANY, "goodbye"): (INIT, "Goodbye, have a nice day!"),
    (CHOOSE_FUNCTION, "choose_company"): (CHOOSE_COMPANY, "Ok, which stock price do you want to check?"),
    (CHOOSE_FUNCTION, "others"): (CHOOSE_FUNCTION, "Sorry, I don't understand what you said, please ask me something about stock."),
    (CHOOSE_FUNCTION, "goodbye"): (INIT, "Goodbye, have a nice day!"),
    (CHOOSE_FUNCTION, "get_historical_price"): (INIT, "Please wait! The data is loading..."),
    (CHOOSE_FUNCTION, "get_open_price"): (CHOOSE_FUNCTION, "Please wait! The data is loading..."),
    (CHOOSE_FUNCTION, "get_price"): (CHOOSE_FUNCTION, "Please wait! The data is loading..."),
    (CHOOSE_FUNCTION, "affirm"): (CHOOSE_FUNCTION, "No problem! I'm always ready!"),
    (CHOOSE_FUNCTION, "greet"): (INIT, "Hello! I am a robot helping you to check the stock price! What do you want from me?")
}

# Define chitchat_response()
def chitchat_response(message):
    # Call match_rule()
    response, phrase = match_rule(rules, message)
    # Return none is response is "default"
    if response == "default":
        return None
    if '{0}' in response:
        # Replace the pronouns of phrase
        phrase = replace_pronouns(phrase)
        # Calculate the response
        response = response.format(phrase)
    return response

def match_rule(rules, message):
    for pattern, responses in rules.items():
        match = re.search(pattern, message)
        if match is not None:
            response = random.choice(responses)
            var = match.group(1) if '{0}' in response else None
            return response, var
    return "default", None

#define match rules
rules = {'If (.*)': ["Do you really think it's likely that {0}",
         'Do you wish that {0}', 'What do you think about {0}',
         'Really--if {0}'], 
         'Do you think (.*)': ['if {0}? Absolutely.', 'No chance'],  
         'Do you remember (.*)': ['Did you think I would forget {0}', 
         "Why haven't you been able to forget {0}", 'What about {0}', 'Yes .. and?']}

#define replace_pronouns()
def replace_pronouns(message):
    #replace personal pronouns
    message = message.lower()
    if 'me' in message:
        return re.sub('me', 'you', message)
    if 'i' in message:
        return re.sub('i', 'you', message)
    elif 'my' in message:
        return re.sub('my', 'your', message)
    elif 'am' in message:
        return re.sub('am', 'are', message)
    elif 'your' in message:
        return re.sub('your', 'my', message)
    elif 'you' in message:
        return re.sub('you', 'me', message)

    return message

# define send_message()
def send_message(state, message, params):
    print("USER : {}".format(message))
    response = chitchat_response(message)
    if response is not None:
        print("BOT : {}".format(response))
        my_friend.send(response)
        return state, params
    # Calculate the new state and params
    new_state, response, new_params = respond(state, message, params)
    print("BOT : {}".format(response))
    my_friend.send(response)
    return new_state, new_params

# define respond()       
def respond(state, message, params):
    entities = interpreter.parse(message)["entities"]
    intent = interpreter.parse(message)["intent"]["name"]
    # Initialize an empty params dictionary
    #params = {}
    # Fill the dictionary with entities
    for ent in entities:
        params[ent["entity"]] = str(ent["value"])
    # find the match response
    (new_state, response) = policy_rules[(state, intent)]
    # extract the name of company
    if new_state == 1:
        for ent in params:
            if ent == "company":
                company = str(params[ent])
    if new_state == 2:
        if intent == "get_price":
            for ent in params:
                if ent == "company":
                    company = str(params[ent])
            stock = Stock(company)
            price = str(stock.get_price())
            response = "The current stock price of "+ company +" is " + price
        if intent == "get_historical_price":
            my_friend.send("Loading diagram...")
            for ent in params:
                if ent == "company":
                    company = str(params[ent])
                if ent == "start_date":
                    startdateStr = str(params[ent])
                    startda = startdateStr.split('.')
                    start = datetime(int(startda[0]), int(startda[1]), int(startda[2]))
                if ent == "end_date":
                    enddateStr = str(params[ent])
                    endda = enddateStr.split('.')
                    end = datetime(int(endda[0]), int(endda[1]), int(endda[2]))
            df = get_historical_data(company, start, end, output_format='pandas')        
            df.plot()
            plt.savefig("./figure.jpg")
            my_friend.send_image('figure.jpg')
            response = "The stock price diagram of " + company
        if intent == "get_open_price":
            for ent in params:
                if ent == "company":
                    company = str(params[ent])
            stock = Stock(company)
            price = str(stock.get_open())
            response = "The open price of " + company + " is " + price
    return new_state, response, params

# define send_messages
def send_messages(messages):
    state = INIT
    params = {}
    for msg in messages:
        state, params = send_message(state, msg, params)
        #print(state)

# initialise the bot
state = INIT
params = {}
bot = Bot()
# search the friend with nanme "Jethro", sex is male and city is Qingdao
my_friend = bot.friends().search('Jethro', sex=MALE, city='青岛')[0]
# sent a start message   
my_friend.send('Hello! I\'m here!')
# reply the message send by my_friend
@bot.register(my_friend)

def reply_my_friend(msg):
    global state, params
    state, params = send_message(state, msg.text, params)
    return None         

