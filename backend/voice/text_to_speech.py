import pyttsx3


class TextToSpeech:

    def __init__(
        self,
        rate=175,
        volume=1.0
    ):

        self.engine = (
            pyttsx3.init()
        )

        self.set_rate(
            rate
        )

        self.set_volume(
            volume
        )

    # ==========================================
    # RATE
    # ==========================================

    def set_rate(
        self,
        rate
    ):

        rate = int(rate)

        if rate <= 0:
            raise ValueError(
                "Speech rate must be positive."
            )

        self.engine.setProperty(
            "rate",
            rate
        )

    # ==========================================
    # VOLUME
    # ==========================================

    def set_volume(
        self,
        volume
    ):

        volume = float(volume)

        if not 0.0 <= volume <= 1.0:

            raise ValueError(
                "Volume must be between 0 and 1."
            )

        self.engine.setProperty(
            "volume",
            volume
        )

    # ==========================================
    # VOICES
    # ==========================================

    def get_voices(self):

        voices = (
            self.engine.getProperty(
                "voices"
            )
        )

        results = []

        for voice in voices:

            results.append({
                "id": voice.id,
                "name": getattr(
                    voice,
                    "name",
                    ""
                ),
                "languages": getattr(
                    voice,
                    "languages",
                    []
                )
            })

        return results

    # ==========================================
    # SPEAK
    # ==========================================

    def speak(
        self,
        text
    ):

        if text is None:
            return False

        text = str(
            text
        ).strip()

        if not text:
            return False

        try:

            self.engine.say(
                text
            )

            self.engine.runAndWait()

            return True

        except Exception as error:

            print(
                f"AEGIS TTS ERROR: {error}"
            )

            return False

    # ==========================================
    # STOP
    # ==========================================

    def stop(self):

        try:
            self.engine.stop()
        except Exception:
            pass

    # ==========================================
    # CLOSE
    # ==========================================

    def close(self):

        self.stop()


if __name__ == "__main__":

    tts = TextToSpeech()

    print(
        "Available voices:"
    )

    for voice in tts.get_voices():

        print(
            voice
        )

    print(
        "\nTesting speech..."
    )

    tts.speak(
        "Hello. I am AEGIS. "
        "Voice output is working."
    )

    tts.close()