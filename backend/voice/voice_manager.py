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
    # CALIBRATE
    # ==========================================

    def calibrate(self):

        return self.stt.calibrate()

    # ==========================================
    # LISTEN
    # ==========================================

    def listen(
        self,
        max_duration=8
    ):

        try:

            return self.stt.listen(
                max_duration=max_duration
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
    # CLOSE
    # ==========================================

    def close(self):

        self.stt.close()
        self.tts.close()