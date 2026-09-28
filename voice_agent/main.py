import speech_recognition as sr

def main():
    r = sr.Recognizer() #speech to Text

    with sr.Microphone() as source: # Mic Access
        r.adjust_for_ambient_noise(source)
        r.pause_threshold = 2 

        print("Speak Somethings...")
        audio = r.listen(source)

        print("processing Audio... (STT)")
        stt = r.recognize_google(audio)

        print("You Said: ", stt)

main()