import pyttsx3
import speech_recognition as sr
while True:
    print("say check mail or send mail or exit")
    engine = pyttsx3.init()
    engine.say("say check mail or send mail or exit")
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
    voice_input = get_voice_input()
    if voice_input and "check mail" in voice_input.lower():
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
        
        try:
            print("Please say 'check my email' to retrieve your recent emails")
            engine.say("Please say 'check my email' to retrieve your recent emails")
            engine.runAndWait()
            voice_input = get_voice_input()
            if voice_input and "check my email" in voice_input.lower():
                recent_emails = get_recent_emails()
                for idx, email in enumerate(recent_emails, start=1):
                    email_text = f"Email {idx}: From {email['from']}, Subject {email['subject']}."
                    print(email_text)
                    engine.say(email_text)
                    engine.runAndWait()
                    engine.say("say read body to listen body of email")          
                    engine.runAndWait()
                    voice_input = get_voice_input()
                    if voice_input and "read body" in voice_input.lower():
                        engine.say("Reading email content.")          
                        engine.runAndWait()
                        email_body = email['body']
                        print(email_body)
                        engine.say(email_body)
                        engine.runAndWait()
        except Exception as e:
            speak("error reading email")
            print("Error reading email")
        
    if voice_input and "send mail" in voice_input.lower():
        import smtplib
        import speech_recognition as sr
        import pyttsx3  # Text-to-speech library
        def listen():
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                print("Listening...")
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)
            try:
                print("Recognizing...")
                text = recognizer.recognize_google(audio)
                text= text.replace("at the rate","@").replace("dash","-")
                text=text.strip()
                text=text.replace(" ","")
                text=text.lower()
                print("You said:", text)
                return text
            except sr.UnknownValueError:
                print("Could not understand audio.")
                return None
            except sr.RequestError as e:
                print("Error with the speech recognition service; {0}".format(e))
                return None
        def speak(text):
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        #def send_email(sender_email, sender_password, to_email, subject, body):
            #message = f"Subject: {subject}\n\n{body}"
        def send_email(to_email, subject, body):
            sender_email="mrudulaligade05@gmail.com"
            sender_password= "pcnt xivo html jxoy"
            try:
                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                    server.starttls()
                    server.login(sender_email, sender_password)
                    message = f"Subject: {subject}\n\n{body}"
                    server.sendmail(sender_email, to_email, message)
                speak("Email sent successfully!")
                print("Email sent sucessfully!")

            except Exception as e:
                speak("error sending email")
                print("Error sending email: {e}")
        def main():
            print("Please say the recipient's email address:")
            speak("Please say the recipient's email address:")
            to_email = listen()
            if not to_email:
                print("Exiting.")
                return
            speak(f"You said the recipient's email address is {to_email}")
            # Get email subject
            speak("Please say the email subject:")
            subject = listen()
            if not subject:
                print("Exiting.")
                return
            speak(f"You said the email subject is {subject}")
            # Get email body
            speak("Please say the email body:")
            body = listen()
            if not body:
                print("Exiting.")
                return
            speak(f"You said the email body is {body}")
            # Send the email
            send_email(to_email, subject, body)

        if __name__ == "__main__":
            main()
    if voice_input and "exit" in voice_input.lower():
        if voice_input and "exit" in voice_input.lower():
            exit()
