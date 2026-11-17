import time
import pyttsx3

messages = [
    "First message. Vision X Guide voice test.",
    "Second message. A person is detected on your left.",
    "Third message. A vehicle is detected ahead.",
]

for index, message in enumerate(messages, start=1):
    print(f"\nInitializing engine for message {index}...")

    engine = None

    try:
        engine = pyttsx3.init("sapi5")
        engine.setProperty("rate", 165)
        engine.setProperty("volume", 1.0)

        print(f"Speaking message {index}: {message}")
        engine.say(message)
        engine.runAndWait()

        print(f"Message {index} playback call completed.")

    except Exception as error:
        print(f"ERROR on message {index}: {error}")

    finally:
        if engine is not None:
            engine.stop()
            del engine

    time.sleep(1.5)

print("\nAll messages processed.")
