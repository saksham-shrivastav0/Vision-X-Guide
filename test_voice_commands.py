import speech_recognition as sr
import time


def recognize_command(recognizer, audio):
    """
    Try Indian English first, then Hindi.
    The recognized text will be checked by our command handler later.
    """
    for language in ("en-IN", "hi-IN"):
        try:
            text = recognizer.recognize_google(
                audio,
                language=language,
            )
            return text, language

        except sr.UnknownValueError:
            continue

        except sr.RequestError as error:
            print(f"[NETWORK ERROR] {error}")
            return None, None

    return None, None


def main():
    recognizer = sr.Recognizer()

    print("VisionX Guide - Microphone Test")
    print("Initializing microphone...")

    try:
        with sr.Microphone() as source:
            print("Adjusting for background noise...")
            recognizer.adjust_for_ambient_noise(
                source,
                duration=1,
            )

            print("\nMicrophone ready!")
            print("Say: Help, Repeat, Pause, Resume")
            print("Or: Madad karo, Dobara bolo, Ruko")
            print("Press Ctrl+C to stop.\n")

            while True:
                try:
                    print("Listening...")

                    audio = recognizer.listen(
                        source,
                        timeout=5,
                        phrase_time_limit=4,
                    )

                    text, language = recognize_command(
                        recognizer,
                        audio,
                    )

                    if text:
                        print(f"[HEARD - {language}] {text}")
                    else:
                        print("[INFO] Speech not recognized.")

                except sr.WaitTimeoutError:
                    print("[INFO] No speech heard. Listening again.")

                except KeyboardInterrupt:
                    raise

    except KeyboardInterrupt:
        print("\nMicrophone test stopped.")

    except OSError as error:
        print(f"[MICROPHONE ERROR] {error}")
        print("Check your microphone and Windows permissions.")

    except Exception as error:
        print(f"[ERROR] {type(error).__name__}: {error}")


if __name__ == "__main__":
    main()
