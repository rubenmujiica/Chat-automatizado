from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Diccionario para guardar el estado de cada usuario
user_state = {}

@app.route("/whatsapp", methods=['POST'])
def whatsapp():
    incoming_msg = request.values.get('Body', '').strip()
    from_number = request.values.get('From', '')

    # Cargamos el estado del usuario (o empezamos desde cero)
    state = user_state.get(from_number, 'start')

    resp = MessagingResponse()
    msg = resp.message()

    # Reiniciar el estado si el usuario envía "reiniciar" o algo similar
    if incoming_msg.lower() == 'reiniciar':
        user_state[from_number] = 'start'
        msg.body('La conversación se ha reiniciado.')
    elif state == 'start':
        msg.body('¡Hola! ¿Cómo te llamas?')
        user_state[from_number] = 'ask_name'
    elif state == 'ask_name':
        user_state[from_number] = {'name': incoming_msg, 'next': 'ask_age'}
        msg.body('Encantado, {}. ¿Cuántos años tienes?'.format(incoming_msg))
    elif isinstance(user_state[from_number], dict) and user_state[from_number]['next'] == 'ask_age':
        user_state[from_number]['age'] = incoming_msg
        user_state[from_number]['next'] = 'ask_experience'
        msg.body('Perfecto. ¿Tienes experiencia previa en este puesto? (Sí/No)')
    elif isinstance(user_state[from_number], dict) and user_state[from_number]['next'] == 'ask_experience':
        # Manejar posibles respuestas erróneas
        if incoming_msg.lower() not in ['sí', 'no', 'si', 'Si', 'Sí', 'No']:
            msg.body('Por favor, responde con "Sí" o "No". ¿Tienes experiencia previa en este puesto? (Sí/No)')
        else:
            user_state[from_number]['experience'] = incoming_msg
            name = user_state[from_number]['name']
            age = user_state[from_number]['age']
            experience = incoming_msg
            msg.body('Gracias {}. Has indicado que tienes {} años y que experiencia previa: {}.'.format(name, age, experience))
            user_state[from_number] = 'done'
    else:
        msg.body('¡Gracias! Ya hemos terminado la entrevista.')

    return str(resp)

if __name__ == "__main__":
    app.run(port=5000)
