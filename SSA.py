# -*- coding: utf-8 -*-
"""
Created on Wed Feb  6 17:02:02 2019

@author: Lingxiao Li
"""
# import modules
import re
import random
import sqlite3
from rasa_nlu.training_data import load_data
from rasa_nlu.config import RasaNLUModelConfig
from rasa_nlu.model import Trainer
from rasa_nlu import config
import datetime
from wxpy import *
# Create a trainer that uses this config
trainer = Trainer(config.load("config_spacy.yml"))

# Load the training data
training_data = load_data('training-data.json')
interpreter = trainer.train(training_data)

# Define the states
INIT=0 
CREATE_EVENT = 1
DELETE_EVENT = 2
CREATE_PENDING = 3
DELETE_PENDING = 4

# Define the policy rules dictionary
policy_rules = {
    (INIT, "greet"): (INIT, "Hello! I am a smart robot helping you to manage your schedules! What do you want from me?"),
    (INIT, "affirm"): (INIT, "No problem! I'm always ready!"),
    (INIT, "goodbye"): (INIT, "Goodbye, have a nice day!"),
    (INIT, "others"): (INIT, "Sorry, I don't understand what you said, please tell me something about schedules."),
    (INIT, "ask_function"): (INIT, "I have three functions now:\n 1. Create a new schedule.\n 2. Search schedules already created.\n 3. Delete a schedule."),
    (INIT, "create_event"): (CREATE_EVENT, "Let's get started! Please provide details about the event."),
    (INIT, "delete_event"): (DELETE_EVENT, "Which schedule do you want to delete? Please provide more details."),
    (INIT, "search_event"): (INIT, "Got it!"),
    (INIT, "negation"): (INIT, "Got it! Job cancelled!"),
    (CREATE_EVENT, "add_detail"): (CREATE_PENDING, "Got it!"),
    (DELETE_EVENT, "add_detail"): (DELETE_PENDING, "Got it!"),
    (CREATE_EVENT, "negation"): (INIT, "Got it! Job cancelled!"),
    (DELETE_EVENT, "negation"): (INIT, "Got it! Job cancelled!"),
    (CREATE_PENDING, "affirm"): (INIT, "Good to go!"),
    (CREATE_PENDING, "negation"): (INIT, "Got it! Job cancelled!"),
    (DELETE_PENDING, "affirm"): (INIT, "Good to go!"),
    (DELETE_PENDING, "negation"): (INIT, "Got it! Job cancelled!"),
    (CREATE_PENDING, "greet"): (CREATE_PENDING, "Hello! I am a robot helping you to check the stock price! What do you want from me?"),
    (CREATE_PENDING, "others"): (CREATE_PENDING, "Sorry, I don't understand what you said, please tell me something about schedules."),
    (CREATE_PENDING, "ask_function"): (CREATE_PENDING, "I have three functions now:\n 1. Create a new schedule.\n 2. Search schedules already created.\n 3. Update and delete a schedule."),
    (CREATE_PENDING, "goodbye"): (INIT, "Goodbye, have a nice day!"),
    (DELETE_PENDING, "greet"): (DELETE_PENDING, "Hello! I am a robot helping you to check the stock price! What do you want from me?"),
    (DELETE_PENDING, "others"): (DELETE_PENDING, "Sorry, I don't understand what you said, please tell me something about schedules."),
    (DELETE_PENDING, "ask_function"): (DELETE_PENDING, "I have three functions now:\n 1. Create a new schedule.\n 2. Search schedules already created.\n 3. Update and delete a schedule."),
    (DELETE_PENDING, "goodbye"): (INIT, "Goodbye, have a nice day!")
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
        #my_friend.send(response)
        return state, params
    # Calculate the new state and params
    new_state, response, new_params = respond(state, message, params)
    print("BOT : {}".format(response))
    #my_friend.send(response)
    return new_state, new_params

# Define find_hotels()
def find_events(params, date, time):
    for ent in params:
        if ent == "date":
            params[ent] = date
        if ent == "time":
            params[ent] = time
    # Create the base query
    print(params)
    query = 'SELECT * FROM events'
    # Add filter clauses for each of the parameters
    if len(params) > 0:
        filters = ["{}=?".format(k) for k in params]
        query += " WHERE " + " and ".join(filters)
    # Create the tuple of values
    t = tuple(params.values())
    
    # Open connection to DB
    conn = sqlite3.connect("events.db")
    # Create a cursor
    c = conn.cursor()
    # Execute the query
    c.execute(query, t)
    # Return the results
    return c.fetchall()

def create_event(name, time, date, location):
    # Create the base query
    query = "INSERT INTO events(schedule_id, user_id, event_name, time, date, location) VALUES(1, 1, '" + str(name) + "', '" + str(time) + "', '" + str(date) + "', '" + str(location) + "')"
    
    # Open connection to DB
    conn = sqlite3.connect("events.db")
    # Create a cursor
    c = conn.cursor()
    # Execute the query
    c.execute(query)
    c.execute("commit")
    
def delete_event(params, date, time):
    for ent in params:
        if ent == "date":
            #print(date)
            params[ent] = date
        if ent == "time":
            print(time)
            params[ent] = time
    query = 'DELETE FROM events'
    # Add filter clauses for each of the parameters
    if len(params) > 0:
        filters = ["{}=?".format(k) for k in params]
        query += " WHERE " + " and ".join(filters)
    # Create the tuple of values
    t = tuple(params.values())
    
    # Open connection to DB
    conn = sqlite3.connect("events.db")
    # Create a cursor
    c = conn.cursor()
    # Execute the query
    c.execute(query, t)
    c.execute("commit")
    
    
def formatDate(date):  
    year = "2019"
    month = "01"
    day = "01"
    
    if 'January' in date:
        month = "01"
    if 'Jan' in date:
        month = "01"
    if 'january' in date:
        month = "01"
    if 'jan' in date:
        month = "01"
    if 'February' in date:
        month = "02"
    if 'Feb' in date:
        month = "02"
    if 'february' in date:
        month = "02"
    if 'feb' in date:
        month = "02"
    if 'March' in date:
        month = "03"
    if 'Mar' in date:
        month = "03"
    if 'march' in date:
        month = "03"
    if 'mar' in date:
        month = "03"
    if 'April' in date:
        month = "04"
    if 'Apr' in date:
        month = "04"
    if 'april' in date:
        month = "04"
    if 'apr' in date:
        month = "04"
    if 'May' in date:
        month = "05"
    if 'may' in date:
        month = "05"
    if 'June' in date:
        month = "06"
    if 'Jun' in date:
        month = "06"
    if 'june' in date:
        month = "06"
    if 'jun' in date:
        month = "06"
    if 'July' in date:
        month = "07"
    if 'Jul' in date:
        month = "07"
    if 'july' in date:
        month = "07"
    if 'jul' in date:
        month = "07"
    if 'August' in date:
        month = "08"
    if 'Aug' in date:
        month = "08"
    if 'august' in date:
        month = "08"
    if 'aug' in date:
        month = "08"
    if 'September' in date:
        month = "09"
    if 'Sep' in date:
        month = "09"
    if 'september' in date:
        month = "09"
    if 'sep' in date:
        month = "09"
    if 'October' in date:
        month = "10"
    if 'Oct' in date:
        month = "10"
    if 'october' in date:
        month = "10"
    if 'oct' in date:
        month = "10"
    if 'November' in date:
        month = "11"
    if 'Nov' in date:
        month = "11"
    if 'november' in date:
        month = "11"
    if 'nov' in date:
        month = "11"
    if 'December' in date:
        month = "12"
    if 'Dec' in date:
        month = "12"
    if 'december' in date:
        month = "12"
    if 'dec' in date:
        month = "12"
    if '1st' in date:
        day = "01"
    if '2nd' in date:
        day = "02"
    if '3rd' in date:
        day = "03"
    if '4th' in date:
        day = "04"
    if '5th' in date:
        day = "05"
    if '6th' in date:
        day = "06"
    if '7th' in date:
        day = "07"
    if '8th' in date:
        day = "08"
    if '9th' in date:
        day = "09"
    if '10th' in date:
        day = "10"
    if '11th' in date:
        day = "11"
    if '12th' in date:
        day = "12"
    if '13th' in date:
        day = "13"
    if '14th' in date:
        day = "14"
    if '15th' in date:
        day = "15"
    if '16th' in date:
        day = "16"
    if '17th' in date:
        day = "17"
    if '18th' in date:
        day = "18"
    if '19th' in date:
        day = "19"
    if '20th' in date:
        day = "20"
    if '21st' in date:
        day = "21"
    if '22nd' in date:
        day = "22"
    if '23rd' in date:
        day = "23"
    if '24th' in date:
        day = "24"
    if '25th' in date:
        day = "25"
    if '26th' in date:
        day = "26"
    if '27th' in date:
        day = "27"
    if '28th' in date:
        day = "28"
    if '29th' in date:
        day = "29"
    if '30th' in date:
        day = "30"
    if '31st' in date:
        day = "31"
        
    if 'today' in date:
        date = datetime.date.today()        
    elif 'the day after tomorrow' in date:
        date = datetime.date.today() + datetime.timedelta(days=2)           
    elif 'tomorrow' in date:
        date = datetime.date.today() + datetime.timedelta(days=1)        
    elif 'the day before yesterday' in date:
        date = datetime.date.today() - datetime.timedelta(days=2)        
    elif 'yesterday' in date:
        date = datetime.date.today() - datetime.timedelta(days=1)
    elif '-' in date:
        date = date
    else:
        date = year + "-" + month + "-" + day
    
    return str(date)
    
    
    
    
    
    
def formatTime(time):
    
    time = time.lower()
    if "one o'clock" in time:
        time = "1 AM"
    if "1 o'clock" in time:
        time = "1 AM"
    if "one am" in time:
        time = "1 AM"
    if "1 am" in time:
        time = "1 AM"
    if "two o'clock" in time:
        time = "2 AM"
    if "2 o'clock" in time:
        time = "2 AM"
    if "two am" in time:
        time = "2 AM"
    if "2 am" in time:
        time = "2 AM"
    if "three o'clock" in time:
        time = "3 AM"
    if "3 o'clock" in time:
        time = "3 AM"
    if "three am" in time:
        time = "3 AM"
    if "3 am" in time:
        time = "3 AM"
    if "four o'clock" in time:
        time = "4 AM"
    if "4 o'clock" in time:
        time = "4 AM"
    if "four am" in time:
        time = "4 AM"
    if "4 am" in time:
        time = "4 AM"
    if "five o'clock" in time:
        time = "5 AM"
    if "5 o'clock" in time:
        time = "5 AM"
    if "five am" in time:
        time = "5 AM"
    if "5 am" in time:
        time = "5 AM"
    if "six o'clock" in time:
        time = "6 AM"
    if "6 o'clock" in time:
        time = "6 AM"
    if "six am" in time:
        time = "6 AM"
    if "6 am" in time:
        time = "6 AM"
    if "seven o'clock" in time:
        time = "7 AM"
    if "7 o'clock" in time:
        time = "7 AM"
    if "seven am" in time:
        time = "7 AM"
    if "7 am" in time:
        time = "7 AM"
    if "eight o'clock" in time:
        time = "8 AM"
    if "8 o'clock" in time:
        time = "8 AM"
    if "eight am" in time:
        time = "8 AM"
    if "8 am" in time:
        time = "8 AM"
    if "nine o'clock" in time:
        time = "9 AM"
    if "9 o'clock" in time:
        time = "9 AM"
    if "nine am" in time:
        time = "9 AM"
    if "9 am" in time:
        time = "9 AM"
    if "ten o'clock" in time:
        time = "10 AM"
    if "10 o'clock" in time:
        time = "10 AM"
    if "ten am" in time:
        time = "10 AM"
    if "10 am" in time:
        time = "10 AM"
    if "eleven o'clock" in time:
        time = "11 AM"
    if "11 o'clock" in time:
        time = "11 AM"
    if "eleven am" in time:
        time = "11 AM"
    if "11 am" in time:
        time = "11 AM"
    if "twelve o'clock" in time:
        time = "12 AM"
    if "12 o'clock" in time:
        time = "12 AM"
    if "twelve am" in time:
        time = "12 AM"
    if "12 am" in time:
        time = "12 AM"
    if "1 pm" in time:
        time = "1 PM"
    if "2 pm" in time:
        time = "2 PM"
    if "3 pm" in time:
        time = "3 PM"
    if "4 pm" in time:
        time = "4 PM"
    if "5 pm" in time:
        time = "5 PM"
    if "6 pm" in time:
        time = "6 PM"
    if "7 pm" in time:
        time = "7 PM"
    if "8 pm" in time:
        time = "8 PM"
    if "9 pm" in time:
        time = "9 PM"
    if "10 pm" in time:
        time = "10 PM"
    if "11 pm" in time:
        time = "11 PM"
    if "12 pm" in time:
        time = "12 PM"
    
    return str(time)

# define respond()       
def respond(state, message, params):
    intent = "others"
    if state == 0:
        params = {}
    entities = interpreter.parse(message)["entities"]
    intent = interpreter.parse(message)["intent"]["name"]
    # Initialize an empty params dictionary
    #params = {}
    # Fill the dictionary with entities
    for ent in entities:
        params[ent["entity"]] = str(ent["value"])
    # find the match response
    (new_state, response) = policy_rules[(state, intent)]
    #print(response)
    #print(params)
    if state == 0:
        name = None
        time = None
        location = None
        date = None
        
        if intent == "search_event":
            for ent in params:
                if ent == "time":
                    time = str(params[ent])
                    time = formatTime(time)
                if ent == "location":
                    location = str(params[ent])
                    #print(location)
                if ent == "date":
                    date = str(params[ent])
                    date = formatDate(date)
                    print(date)
                if ent == "event_name":
                    name = str(params[ent])
            result = find_events(params, date, time)
            #print(result)
            if len(result) == 0:
                response = "You have no schedule"
            if len(result) >= 1:
                response = "You have " + str(len(result)) + " schedule(s)"
                
            if name != None:
                response += " called " + name
            if location != None:
                response += " in " + location
            if date != None:
                response += " on " + date
            if time != None:
                response += " at " + time
            response += "\n"
                
            for r in result:
                response += "\n"
                response += "Event Name: " + r[2] + "\n"
                response += "Time: " + r[3] + "\n"
                response += "Date: " + r[4] + "\n"
                response += "Location: " + r[5] + "\n"
                response += "\n"
            
    if state == 1:
        name = None
        time = None
        location = None
        date = None
        if intent == "add_detail": 
            for ent in params:
                if ent == "time":
                    time = str(params[ent])
                    time = formatTime(time)
                    #print(time)
                if ent == "location":
                    location = str(params[ent])
                    #print(location)
                if ent == "date":
                    date = str(params[ent])
                    #print(date)
                    date = formatDate(date)
                if ent == "event_name":
                    name = str(params[ent])
            response = "Got it! Create event: \n"
            response += "\n"
            response += "Event Name: " + str(name) + "\n"
            response += "Time: " + str(time) + "\n"
            response += "Date: " + str(date) + "\n"
            response += "Location: " + str(location) + "\n"
            response += "\n"
            response += "Please confirm the information."
            
    if state == 2:
        name = None
        time = None
        location = None
        date = None
        for ent in params:
            if ent == "time":
                time = str(params[ent])
                time = formatTime(time)
            if ent == "location":
                location = str(params[ent])
                #print(location)
            if ent == "date":
                date = str(params[ent])
                date = formatDate(date)
            if ent == "event_name":
                name = str(params[ent])
        if intent == "add_detail": 
            result = find_events(params, date, time)
            if len(result) == 0:
                new_state = 0
                response = "You have no schedule"
            if len(result) > 0:
                response = "Got it! Delete event: \n"
                for r in result:
                    response += "\n"
                    response += "Event Name: " + r[2] + "\n"
                    response += "Time: " + r[3] + "\n"
                    response += "Date: " + r[4] + "\n"
                    response += "Location: " + r[5] + "\n"
                    response += "\n"
                response += "Please confirm the information."
            
    if state == 3:
        name = None
        time = None
        location = None
        date = None
        for ent in params:
                if ent == "time":  
                    time = str(params[ent])
                    time = formatTime(time)
                if ent == "location":
                    location = str(params[ent])
                    #print(location)
                if ent == "date":
                    date = str(params[ent])
                    date = formatDate(date)
                if ent == "event_name":
                    name = str(params[ent])
        if intent == "affirm":
            create_event(name, time, date, location)
            response = "Event created!"
        if intent == "nagation":
            response = "Operation cancelled!"
            
    if state == 4:
        name = None
        time = None
        location = None
        date = None
        #print(params)
        for ent in params:
            if ent == "time":     
                time = str(params[ent])
                time = formatTime(time)
                #print(time)
            if ent == "location":
                location = str(params[ent])
                #print(location)
            if ent == "date":
                date = str(params[ent])
                date = formatDate(date)
                #print(date)
            if ent == "event_name":
                name = str(params[ent])
        if intent == "affirm":
            delete_event(params, date, time)
            response = "Event deleted!"
        if intent == "nagation":
            response = "Operation cancelled!"

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
# Send the messages

send_messages([
    "Do you think robort will replace you?",
    "Hello",
    "What can you do for me?",
    "1234567890",
    #"SHow me the events today",
    "SHow me the events tomorrow",
    "delete an event",
    "delete the event today",
    #"yes"
    #"Create an event",
    #"a meeting at 2 am in London today",
    #"a meeting at 2 am in Liverpool tomorrow",
    #"OK",
    #"Create another event",
    #"buy some egges at 5pm in Tesco",
    #"OK"   
])   
'''
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
'''