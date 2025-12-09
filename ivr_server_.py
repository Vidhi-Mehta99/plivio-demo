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
    digit = request.args.get('Digits') or request.form.get('Digits')
    
    if not digit:
        # If no digit was pressed, redirect back to language selection
        response = plivoxml.ResponseElement()
        response.add_redirect(f'{BASE_URL}/assistant/', method='GET')
        return Response(response.to_string(False), mimetype='text/xml')
    
    if digit == '1':
        # Play the audio file
        audio_url = "https://s3.amazonaws.com/plivocloud/Trumpet.mp3"
        response = plivoxml.ResponseElement()
        
        # Add a message before playing the audio
        if lang == 'es':
            response.add_speak("Reproduciendo el audio.", voice='Polly.Lupe', language='es-ES')
        else:
            response.add_speak("Playing the audio.", voice='Polly.Salli', language='en-US')
        
        # Add the audio file to be played
        response.add_play(audio_url)
        
        # After playing the audio, give options to continue or hang up
        if lang == 'es':
            response.add_speak("Para volver al menú principal, presione 1. Para finalizar la llamada, presione 2.", 
                             voice='Polly.Lupe', language='es-ES')
        else:
            response.add_speak("To return to the main menu, press 1. To end the call, press 2.",
                             voice='Polly.Salli', language='en-US')
        
        # Get input from the user after playing the audio
        response.add_get_digits(
            action=f"{BASE_URL}/post_audio_menu/?lang={lang}",
            method='POST',
            timeout=10,
            num_digits=1,
            retries=1
        )
        
        # If no input is received, say goodbye
        if lang == 'es':
            response.add_speak("Gracias por llamar. Hasta luego.", voice='Polly.Lupe', language='es-ES')
        else:
            response.add_speak("Thank you for calling. Goodbye.", voice='Polly.Salli', language='en-US')
        response.add_hangup()
        
        return Response(response.to_string(False), mimetype='text/xml')
        
    elif digit == '2':
        # Connect to a live associate
        response = plivoxml.ResponseElement()
        
        # Add a message before connecting
        if lang == 'es':
            response.add_speak("Conectándote con un agente. Por favor, espere.", 
                             voice='Polly.Lupe', 
                             language='es-ES')
        else:
            response.add_speak("Connecting you to a live associate. Please hold.",
                             voice='Polly.Salli',
                             language='en-US')
        
        # Add the dial element to connect to the secondary number
        dial = response.add(plivoxml.DialElement(
            caller_id=os.getenv('PLIVO_NUMBER'),
            action=f"{BASE_URL}/call_action/",
            method='GET',
            timeout=30,  # Wait up to 30 seconds for the call to be answered
            hangup_on_star=False,
            time_limit=14400  # Maximum call duration: 4 hours
        ))
        
        # Add the secondary number to dial
        dial.add_number(os.getenv('SECONDARY_NUMBER'))
        
        return Response(response.to_string(False), mimetype='text/xml')
    
    # Handle invalid input
    response = plivoxml.ResponseElement()
    if lang == 'es':
        response.add_speak("Opción no válida. Por favor, intente de nuevo.", 
                         voice='Polly.Lupe',
                         language='es-ES')
    else:
        response.add_speak("Invalid option. Please try again.",
                         voice='Polly.Salli',
                         language='en-US')
    
    # Redirect back to the menu
    response.add_redirect(f"{BASE_URL}/menu/?lang={lang}", method='GET')
    return Response(response.to_string(False), mimetype='text/xml')

@app.route('/post_audio_menu/', methods=['POST'])
def post_audio_menu():
    lang = request.args.get('lang', 'en')
    digit = request.form.get('Digits')
    
    response = plivoxml.ResponseElement()
    
    if digit == '1':
        # Return to the main menu
        response.add_redirect(f"{BASE_URL}/assistant/", method='GET')
    else:
        # End the call
        if lang == 'es':
            response.add_speak("Gracias por llamar. Hasta luego.", voice='Polly.Lupe', language='es-ES')
        else:
            response.add_speak("Thank you for calling. Goodbye.", voice='Polly.Salli', language='en-US')
        response.add_hangup()
    
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
