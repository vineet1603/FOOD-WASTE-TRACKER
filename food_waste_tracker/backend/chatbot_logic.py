# chatbot_logic.py

def get_chatbot_response(user_message):
    user_message = user_message.lower()

    if 'hello' in user_message or 'hi' in user_message:
        return "Hello! 👋 I'm your Food Expiry Assistant. Please upload a food image!"
    elif 'upload' in user_message:
        return "Please select and upload a clear photo of your food item 📸."
    elif 'thank' in user_message:
        return "You're welcome! 😊 Happy to help!"
    else:
        return "Sorry, I didn't understand that. Please upload a food image to start."
