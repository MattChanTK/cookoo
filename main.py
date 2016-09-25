"""
Cookoo Cooking Assistant for Alexa Echo
-------------------------------------------
2016-09-24
Matthew Chan; Tammy Fan
"""

from __future__ import print_function
from Queue import Queue

session_attributes_key = ["user_name",
                          "questions",
                          "qindex",
                          "score",
                          "hindex"]

# --------------- Helpers that build all of the responses ----------------------
def initialize_game():
    questions = [{
                    'q': ['Do you want to build a wall. A huge wall between US and Mexico. Who am I referring to?',
                        'The guy with flying golden hair who\'s running for the next US president',
                        'Idiot'],
                    'a': 'Donald Trump'
                 },
                 {
                     'q': [''],
                     'a': ''
                 }]
    question_index = 0
    hint_index = 1
    return {'score': 0, 'questions': questions, 'qindex': question_index, 'hindex': hint_index}


def build_speechlet_response(title, output, reprompt_text=None, should_end_session=False):
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

# --------------- Test functions -----------------------------

def get_testing_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Testing"
    speech_output = "Here here. I am here."

    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Are you still here?"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def read_session_attributes(session):

    card_title = "Testing"

    speech_output = "Your session attributes are: "
    for key, value in session.iteritems():
        if key in session_attributes_key:
            speech_output += ("%s: %s \n" % (key, value))

    return build_response(session["attributes"], build_speechlet_response(
        card_title, speech_output))


# --------------- Functions that control the skill's behavior ------------------
def get_start_new_game_response():
    card_title = "New Game"
    session_attributes = initialize_game()
    speech_output = "A new game is started. First question: " + session_attributes['questions'][0]['q'][0]
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, speech_output, should_end_session))

def get_next_hint_response(intent, session):

    session_attributes = session['attributes']

    question_index = int(session_attributes['qindex'])
    card_title = 'Hint'
    hint_index = int(session_attributes['hindex'])
    speech_output = session_attributes['questions'][question_index]['q'][hint_index]
    session_attributes['hindex'] = hint_index+1 if hint_index < len(session_attributes['questions'][question_index]['q']) else 0

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output))

def check_answer(intent, session):
    session_attributes = session['attributes']

    if 'user_ans' in intent['slots'] and 'value' in intent['slots']['user_ans']:
        user_ans = intent['slots']['user_ans']['value']
        question_index = int(session_attributes['qindex'])
        correct_ans = session_attributes['questions'][question_index]['a']
        if user_ans.lower() == correct_ans.lower():
            speech_output = "You are right!"
        else:
            speech_output = "You are wrong! It is not %s!" % user_ans

        return build_response(session_attributes, build_speechlet_response(
            "answering", speech_output))

    else:
        handle_unknown_intent(session)


def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """
    session_attributes = initialize_game()

    card_title = "Welcome"
    speech_output = "Hello! I am Cookoo. Let's play a game. " \
                    "Are you ready to play?"

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output))

def handle_yes_intent(session):
    try:
        if int(session["attributes"]["qindex"]) ==  0:
            get_start_new_game_response()
    except:
        handle_exception(session)

def handle_unknown_intent(session):

    card_title = "Unknown Intent"
    speech_output = "What? What did you say?"
    return build_response({}, build_speechlet_response(
        card_title, speech_output))

def handle_exception(session):
    card_title = "Error"
    speech_output = "Sorry, I encounter some internal issues."
    return build_response({}, build_speechlet_response(
        card_title, speech_output))

def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Hope it was fun for you too. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

def set_name_in_session(intent, session):
    """
    Record the name of the user
    """

    card_title = "Generic"
    should_end_session = False
    session_attributes = session["attributes"]
    session_attributes["user_name"] = "Bob"

    if 'user_name' in intent['slots'] and 'value' in intent['slots']['user_name']:
        user_name = intent['slots']['user_name']['value']
        session_attributes["user_name"] = user_name
        speech_output = "I now know your name is %s." % session_attributes["user_name"]
        reprompt_text = None
    else:
        speech_output = "I'm not sure what your name is. " \
                        "Please try again."
        reprompt_text = "I'm not sure what your name is. " \
                        "I guess I will call you %s." % session_attributes["user_name"]

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_name_in_session(session):
    card_title = "Generic"

    if "user_name" in session["attributes"]:
        speech_output = "Hello " + session["attributes"]["user_name"]

    else:
        speech_output = "I don't know who you are."

    return build_response(session["attributes"], build_speechlet_response(
        card_title, speech_output, None, False))


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """
    initialize_game()
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

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "Testing":
        return get_testing_response()

    if intent_name == "Testing":
        return get_testing_response()
    elif intent_name == "ReadSessionAttributes":
        return read_session_attributes(session)
    elif intent_name == "SetTeamNameIntent":
        return set_name_in_session(intent, session)
    elif intent_name == "GetTeamNameIntent":
        return get_name_in_session(session)
    elif intent_name == "StartNewGameIntent":
        return get_start_new_game_response()
    elif intent_name == "NextHintIntent":
        return get_next_hint_response(intent, session)
    elif intent_name == "GiveAnswerIntent":
        return check_answer(intent, session)
    elif intent_name == "AMAZON.YesIntent":
        return handle_yes_intent(session)
    elif intent_name == "AMAZON.NoIntent":
        return handle_yes_intent(session)
    elif intent_name == "AMAZON.RepeatIntent":
        return get_testing_response()
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or  intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        return handle_unknown_intent(session)


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

    """
    Populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """

    for key, value in event.iteritems():
        print ("%s: %s" % (key, value))

    if (event['session']['application']['applicationId'] !=
            "amzn1.ask.skill.89e4d29c-e363-4c02-bc59-96521815a0af"):
        raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])