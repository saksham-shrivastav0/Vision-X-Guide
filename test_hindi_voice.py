import asyncio
import edge_tts
import pygame
import os

VOICE = "hi-IN-SwaraNeural"

TEST_MESSAGE = (
    "Namaste! Main Vision X Guide hoon. "
    "Aapke left side ek vyakti hai. "
    "Kripya aage badhne se pehle apne aas paas ka dhyan rakhein."
)

AUDIO_FILE = "hindi_voice_test.mp3"


async def generate_speech():
    communicate = edge_tts.Communicate(
        TEST_MESSAGE,
        VOICE,
        rate="-5%",
    )
    await communicate.save(AUDIO_FILE)


def main():
    try:
        print("Generating Hindi voice...")

        asyncio.run(generate_speech())

        print("Playing Hindi voice...")
        pygame.mixer.init()
        pygame.mixer.music.load(AUDIO_FILE)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.wait(100)

        pygame.mixer.quit()
        print("Hindi voice test completed!")

    except Exception as error:
        print(f"[ERROR] {type(error).__name__}: {error}")

    finally:
        if pygame.mixer.get_init():
            pygame.mixer.quit()

        if os.path.exists(AUDIO_FILE):
            try:
                os.remove(AUDIO_FILE)
            except OSError:
                pass


if __name__ == "__main__":
    main()
