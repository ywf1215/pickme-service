"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function
import requests
import json

url = 'http://ec2-54-77-46-23.eu-west-1.compute.amazonaws.com:5000'
# url = 'http://54.77.46.23:5000'
rider_id = None


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


def ask_for_input():
    return {
        'shouldEndSession': False,
        'directives': [{
            'type': 'Dialog.Delegate'
        }]
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Hello. Welcome to the Optibus On-Demand service," \
                    "What do you want to do?"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "What do you want to do?"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the Optibus On-Demand service," \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def create_favorite_color_attributes(favorite_color):
    return {"favoriteColor": favorite_color}


def on_trip_plan(intent, session, intent_name):

    print('intent: ' + str(intent))
    # print('session: ' + str(session))

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    service_url = url + '/riders/add'
    print('before rest: ' + service_url)
    res = requests.post(service_url, data=json.dumps({
        "name": "Moshe",
        "start_time": 640,
        "origin_stop_id": 1,
        "destination_stop_id": 2,
        "text": "Be at the corner at 08:00"
    }), headers={'content-type': 'application/json'})
    print('After rest:')

    data = res.json()
    print('response: ' + str(data))
    global rider_id
    rider_id = data['id']
    speech_output = data['text']

    # if 'Color' in intent['slots']:
    #     favorite_color = intent['slots']['Color']['value']
    #     session_attributes = create_favorite_color_attributes(favorite_color)
    #     speech_output = "I now know your favorite color is " + \
    #                     favorite_color + \
    #                     ". You can ask me your favorite color by saying, " \
    #                     "what's my favorite color?"
    #     reprompt_text = "You can ask me your favorite color by saying, " \
    #                     "what's my favorite color?"
    # else:
    #     speech_output = "I'm not sure what your favorite color is. " \
    #                     "Please try again."
    #     reprompt_text = "I'm not sure what your favorite color is. " \
    #                     "You can tell me your favorite color by saying, " \
    #                     "my favorite color is red."

    # speech_output = "You should depart from " + \
    #                 intent['slots']['From']['value'] + " at 8:53 am and arrive " + \
    #                 intent['slots']['To']['value'] + " at 10:24 am"
    reprompt_text = ""

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def on_trip_status(intent, session, intent_name):

    print('intent: ' + str(intent))
    # print('session: ' + str(session))

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False
    speech_output = 'There is still no update on your route'

    service_url = url + '/riders/status'
    print('before rest: ' + service_url)
    res = requests.get(service_url, headers={'content-type': 'application/json'})
    print('After rest:')

    data = res.json()
    print('response: ' + str(data))
    riders = data['riders']
    for rider in riders:
        if rider['id'] == rider_id:
            text = data.get('text')
            if text is not None:
                speech_output = text

    reprompt_text = ""

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("intent_request: " + str(intent_request))
    # print("on_intent requestId=" + intent_request['requestId'] +
    #      ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if (intent_request['dialogState'] != "COMPLETED"):
        print('No From 1')
        response = build_response({}, ask_for_input())
        print('from response: ' + str(response))
        return response
    elif intent_name == "PlanMyTrip":
        response = on_trip_plan(intent, session, intent_name)
        print('trip response: ' + str(response))
        return response
    elif intent_name == "TripStatus":
        response = on_trip_status(intent, session, intent_name)
        print('trip response: ' + str(response))
        return response
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])
    print('event: ' + str(event))

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
