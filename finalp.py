import pyttsx3
import speech_recognition as sr
import imaplib
import email
from email.header import decode_header
import smtplib

# ------------------- GLOBAL CONFIG ------------------- #
IMAP_SERVER = 'imap.gmail.com'
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL = 'mrudulaligade05@gmail.com'
PASSWORD = 'sark pgvz jhlt scqm'   # use Gmail App password

# ------------------- INIT ENGINE ------------------- #
engine = pyttsx3.init(driverName='sapi5')

def speak(text):
    print("Assistant:", text)
    engine.say(text)
    engine.runAndWait()

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

# ------------------- EMAIL FUNCTIONS ------------------- #
def get_recent_emails():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL, PASSWORD)
    mail.select('inbox')

    status, data = mail.search(None, 'ALL')
    mail_ids = data[0].split()

    recent_emails = []
    for num in mail_ids[-5:]:
        status, data = mail.fetch(num, '(RFC822)')
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)

        subject, _ = decode_header(msg['Subject'])[0]
        if isinstance(subject, bytes):
            subject = subject.decode('utf-8', 'ignore')

        from_, _ = decode_header(msg['From'])[0]
        if isinstance(from_, bytes):
            from_ = from_.decode('utf-8', 'ignore')

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

def send_email(to_email, subject, body):
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL, PASSWORD)
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(EMAIL, to_email, message)
        speak("Email sent successfully!")
    except Exception as e:
        speak("Error sending email")
        print(f"Error: {e}")

# ------------------- MAIN LOOP ------------------- #
while True:
    speak("Say check mail or send mail or exit")
    command = get_voice_input()

    if not command:
        continue

    command = command.lower()

    # --- CHECK MAIL --- #
    if "check mail" in command:
        speak("Checking your recent emails")
        emails = get_recent_emails()
        for idx, em in enumerate(emails, start=1):
            email_text = f"Email {idx}: From {em['from']}, Subject {em['subject']}."
            print(email_text)
            speak(email_text)

            speak("Say read body if you want to hear the content")
            choice = get_voice_input()
            if choice and "read body" in choice.lower():
                speak("Reading email content")
                print(em['body'])
                speak(em['body'])

    # --- SEND MAIL --- #
    elif "send mail" in command:
        speak("Please say the recipient's email address")
        to_email = get_voice_input()
        if not to_email:
            continue
        to_email = to_email.replace("at the rate", "@").replace(" ", "").lower()

        speak("Please say the subject")
        subject = get_voice_input()
        if not subject:
            continue

        speak("Please say the body")
        body = get_voice_input()
        if not body:
            continue

        send_email(to_email, subject, body)

    # --- EXIT --- #
    elif "exit" in command:
        speak("Goodbye!")
        break
