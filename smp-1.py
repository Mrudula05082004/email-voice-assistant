import imaplib
import email
from email.header import decode_header
import speech_recognition as sr
import pyttsx3

# IMAP settings
IMAP_SERVER = 'imap.gmail.com'
EMAIL = 'mrudulaligade05@gmail.com'
PASSWORD = 'pcnt xivo html jxoy'

def get_voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        print("Recognizing...")
        text = recognizer.recognize_google(audio)
        print("You said:", text)
        return text
    except sr.UnknownValueError:
        print("Could not understand audio.")
        return None
    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))
        return None

def get_recent_emails():
    # Connect to the IMAP server
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL, PASSWORD)
    mail.select('inbox')

    # Search for recent emails
    status, data = mail.search(None, 'ALL')
    mail_ids = data[0].split()

    recent_emails = []
    for num in mail_ids[-5:]:  # Get the 5 most recent emails
        status, data = mail.fetch(num, '(RFC822)')
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)
        subject = decode_header(msg['Subject'])[0][0]
        from_ = decode_header(msg['From'])[0][0]
# Get the email body
        if msg.is_multipart():
            body = ''
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    body += part.get_payload(decode=True).decode('utf-8', 'ignore')
        else:
            body = msg.get_payload(decode=True).decode('utf-8', 'ignore')

        recent_emails.append({'from': from_, 'subject': subject, 'body': body})
    mail.close()
    mail.logout()

    return recent_emails

# Initialize the pyttsx3 engine
engine = pyttsx3.init()
engine.setProperty('voice','english')
# Example usage
while True:
    print("Please say 'check my emails' to retrieve your recent emails otherwise say 'exit' to stop.")
    engine.say("Please say 'check my emails' to retrieve your recent emails otherwise say 'exit' to stop")
    engine.runAndWait()
    voice_input = get_voice_input()
    if voice_input and "check my emails" in voice_input.lower():
        recent_emails = get_recent_emails()
        for idx, email in enumerate(recent_emails, start=1):
            email_text = f"Email {idx}: From {email['from']}, Subject {email['subject']}."
            print(email_text)
            engine.say(email_text)
            engine.runAndWait()
            voice_input = get_voice_input()
            if voice_input and "check my emails" in voice_input.lower():
                engine.say("Reading email content.")          
                engine.runAndWait()
                email_body = email['body']
                print(email_body)
                engine.say(email_body)
                engine.runAndWait()
    else:
      if voice_input and "exit" in voice_input.lower():
            exit()
            
            
