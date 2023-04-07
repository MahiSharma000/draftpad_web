import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging

cred = credentials.Certificate(r"C:\Users\ortha\Videos\secret.json")
firebase_admin.initialize_app(cred)
print("Initialized")

def send_message(token, title, body):
    message = messaging.Message(data={'title': title,'body': body,}, token=token)
    response = messaging.send(message)
    print('Successfully sent message:', response)
    