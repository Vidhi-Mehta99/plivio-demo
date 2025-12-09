import os
from flask import Flask, Response, request, url_for
from plivo import plivoxml
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get base URL from environment variables
BASE_URL = os.getenv('BASE_URL', 'https://condescending-hazardous-cinderella.ngrok-free.dev')

# Welcome message - Language selection
WelcomeMessage = "Welcome! Please choose a language. Press 1 for English or Press 2 for Spanish."
EnglishMenuMessage = "Press 1 to play a message. Press 2 to connect to a live associate."
SpanishMenuMessage = "Pulse 1 para reproducir un mensaje. Pulse 2 para conectarse con un agente."
NoInput = "Sorry, I didn't catch that. Please hang up and try again"
WrongInput = "Sorry, that's not a valid input"

app = Flask(__name__)

@app.route('/assistant/', methods=['GET', 'POST'])
def answer_call():
    # Level 1: Language selection
    print("Answer call route hit!")
    element = plivoxml.ResponseElement()
    
    if request.method == 'GET' or request.method == 'POST':
        response = (
            element.add(
                plivoxml.GetInputElement()
                .set_action(f'{BASE_URL}/language/')
                .set_method('POST')
                .set_input_type('dtmf')
                .set_digit_end_timeout(5)
                .set_redirect(True)
                .set_language('en-US')
                .add_speak(
                    content=WelcomeMessage, voice='Polly.Salli', language='en-US'
                )
            )
            .add_speak(content=NoInput)
            .to_string(False)
        )
    
    print(f"XML Response:\n{response}")
    return Response(response, mimetype='text/xml')

@app.route('/language/', methods=['GET', 'POST'])
def handle_language():
    response = plivoxml.ResponseElement()
    digit = request.form.get('Digits')
    print(f"digit pressed: {digit}")
    
    if digit == '1':
        text = "You selected English"
        params = {'language': 'en-US'}
        response.add(plivoxml.SpeakElement(text, **params))
        
        element = plivoxml.ResponseElement()
        response = (
            element.add(
                plivoxml.GetInputElement()
                .set_action(f'{BASE_URL}/menu/?lang=en')
                .set_method('POST')
                .set_input_type('dtmf')
                .set_digit_end_timeout(5)
                .set_redirect(True)
                .set_language('en-US')
                .add_speak(
                    content=EnglishMenuMessage, voice='Polly.Salli', language='en-US'
                )
            )
            .add_speak(content=NoInput)
            .to_string(False)
        )
        print(response)
        return Response(response, mimetype='text/xml')
        
    elif digit == '2':
        text = "Seleccionaste español"
        params = {'language': 'es-ES'}
        response.add(plivoxml.SpeakElement(text, **params))
        
        element = plivoxml.ResponseElement()
        response = (
            element.add(
                plivoxml.GetInputElement()
                .set_action(f'{BASE_URL}/menu/?lang=es')
                .set_method('POST')
                .set_input_type('dtmf')
                .set_digit_end_timeout(5)
                .set_redirect(True)
                .set_language('es-ES')
                .add_speak(
                    content=SpanishMenuMessage, voice='Polly.Lupe', language='es-ES'
                )
            )
            .add_speak(content=NoInput)
            .to_string(False)
        )
        print(response)
        return Response(response, mimetype='text/xml')
    
    # Handle invalid input
    response = plivoxml.ResponseElement()
    response.add_speak(WrongInput)
    return Response(response.to_string(False), mimetype='text/xml')

@app.route('/menu/', methods=['GET', 'POST'])
def handle_menu():
    lang = request.args.get('lang', 'en')
    digit = request.form.get('Digits')
    
    if digit == '1':
        # Play a message
        if lang == 'es':
            message = "Gracias por llamar. Hasta luego."
            voice = 'Polly.Lupe'
            language = 'es-ES'
        else:
            message = "Thank you for calling. Goodbye."
            voice = 'Polly.Salli'
            language = 'en-US'
            
        response = plivoxml.ResponseElement()
        response.add_speak(message, voice=voice, language=language)
        response.add_hangup()
        return Response(response.to_string(False), mimetype='text/xml')
        
    elif digit == '2':
        # Connect to a live associate
        response = plivoxml.ResponseElement()
        dial = response.add(plivoxml.DialElement(
            caller_id=os.getenv('PLIVO_NUMBER'),
            callback_url=f"{BASE_URL}/call_action/",
            callback_method='GET'
        ))
        dial.add_number(os.getenv('SECONDARY_NUMBER'))
        return Response(response.to_string(False), mimetype='text/xml')
    
    # Handle invalid input
    response = plivoxml.ResponseElement()
    response.add_speak(WrongInput)
    return Response(response.to_string(False), mimetype='text/xml')

@app.route('/call_action/', methods=['GET', 'POST'])
def call_action():
    # This endpoint handles call status callbacks
    call_status = request.args.get('DialAction')
    call_duration = request.args.get('DialDuration')
    
    print(f"Call status: {call_status}")
    print(f"Call duration: {call_duration} seconds")
    
    # Return an empty 200 OK response
    return ("", 200)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 9000))
    host = os.getenv('HOST', '0.0.0.0')
    app.run(host=host, port=port, debug=True)