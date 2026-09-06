from backend.voice.speech_to_text import SpeechToText
from backend.voice.text_to_speech import TextToSpeech


class VoiceManager:

    def __init__(
        self,
        microphone_device=1,
        stt_model="base.en"
    ):

        self.stt = SpeechToText(
            model_size=stt_model,
            microphone_device=microphone_device
        )

        self.tts = TextToSpeech()

    # ==========================================
    # LISTEN
    # ==========================================

    def listen(
        self,
        duration=5
    ):

        try:

            return self.stt.listen(
                duration
            )

        except Exception as error:

            return {
                "text": "",
                "error": str(error)
            }

    # ==========================================
    # SPEAK
    # ==========================================

    def speak(
        self,
        text
    ):

        return self.tts.speak(
            text
        )

    # ==========================================
    # INTERACTION
    # ==========================================

    def listen_and_speak_test(
        self,
        duration=5
    ):

        result = self.listen(
            duration
        )

        if result.get(
            "error"
        ):

            print(
                "AEGIS voice error:",
                result["error"]
            )

            return result

        text = result.get(
            "text",
            ""
        )

        print(
            "You:",
            text
        )

        if text:

            self.speak(
                f"I heard: {text}"
            )

        return result

    # ==========================================
    # CLOSE
    # ==========================================

    def close(self):

        self.stt.close()

        self.tts.close()


if __name__ == "__main__":

    voice = VoiceManager(
        microphone_device=1
    )

    try:

        voice.listen_and_speak_test(
            duration=5
        )

    finally:

        voice.close()
        