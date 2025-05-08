import nest_asyncio
import asyncio
import edge_tts
from IPython.display import Audio, display
import numpy as np
from pydub import AudioSegment
import io
import os
import re
import time
import speech_recognition as sr

# Apply nest_asyncio to run asyncio in Jupyter
nest_asyncio.apply()


class NepaliVoiceAssistant:
    def __init__(self, voice="ne-NP-HemkalaNeural", volume_boost=3.0, wake_word="सहयोगी"):
        """
        Initialize the Nepali Voice Assistant

        Parameters:
        - voice: Voice ID (default: ne-NP-HemkalaNeural)
        - volume_boost: How much to increase volume in dB (default: 3.0)
        - wake_word: Word to activate the assistant (default: "सहयोगी" - Helper)
        """
        self.voice = voice
        self.volume_boost = volume_boost
        self.wake_word = wake_word
        self.listening = False

        # Conversation mapping - customize these responses
        self.responses = {
            # Greetings
            "नमस्ते": ["नमस्ते! म तपाईंलाई कसरी सहयोग गर्न सक्छु?", "नमस्कार! म तपाईंको लागि के गर्न सक्छु?"],
            "हेलो": ["नमस्ते! कसरी सहयोग गर्न सक्छु?", "हजुर, भन्नुहोस्!"],

            # Wake words and activations
            wake_word: ["हजुर, भन्नुहोस्", "म सुन्दै छु", "हजुर, के आवश्यक छ?"],
            "सहयोगी": ["हजुर, म यहाँ छु", "सुन्दै छु"],
            "उठ": ["म तयार छु", "हजुर, सहयोग गर्न तयार छु"],

            # Questions
            "कस्तो छ": ["म राम्रै छु, धन्यवाद! तपाईंलाई कसरी सहयोग गर्न सक्छु?", "सबै ठिक छ, तपाईंलाई?"],
            "तिमी को हौ": ["म तपाईंको नेपाली डिजिटल सहयोगी हुँ", "म नेपाली भाषामा सहयोग गर्ने एक डिजिटल सहायक हुँ"],

            # Commands
            "समय": ["अहिले समय {current_time} भएको छ"],
            "मौसम": ["क्षमा गर्नुहोस्, मौसम जानकारी हेर्न मलाई इन्टरनेट आवश्यक छ"],

            # Closings
            "धन्यवाद": ["स्वागत छ", "खुशी लाग्यो सहयोग गर्न पाउँदा"],
            "बिदा": ["फेरि भेटौंला", "नमस्कार, राम्रो दिन बिताउनुहोस्"],

            # Default response
            "default": ["क्षमा गर्नुहोस्, मैले बुझिनँ", "फेरि भन्नुहोस्", "माफ गर्नुहोस्, थप स्पष्ट हुन सक्नुहुन्छ?"]
        }

        # Action mapping - for handling specific functions
        self.actions = {
            "समय बताउ": self.tell_time,
            "समय कति भयो": self.tell_time,
            "घडी हेर": self.tell_time,

            "गीत बजाऊ": self.play_music,
            "संगीत": self.play_music,

            "मौसम": self.weather_info,
            "मौसम कस्तो छ": self.weather_info
        }

        # Initialize the audio enhancement tools
        try:
            import pydub
        except ImportError:
            print("Installing pydub for audio enhancement...")
            import pip
            pip.main(['install', 'pydub'])

        try:
            import speech_recognition
        except ImportError:
            print("Installing speech recognition...")
            import pip
            pip.main(['install', 'SpeechRecognition'])

    async def speak(self, text, output_file="response.mp3"):
        """Generate Nepali TTS with enhanced volume and clarity"""
        try:
            # Format the text with any dynamic content
            formatted_text = self._format_dynamic_content(text)

            # Generate speech using Edge TTS
            communicate = edge_tts.Communicate(text=formatted_text, voice=self.voice)
            await communicate.save(output_file)

            # Enhance the audio
            try:
                # Load the generated audio
                audio = AudioSegment.from_file(output_file)

                # Boost volume
                boosted_audio = audio + self.volume_boost

                # Apply light compression for clarity
                enhanced_audio = self._compress_dynamic_range(boosted_audio)

                # Cut very low frequencies for better clarity
                enhanced_audio = enhanced_audio.high_pass_filter(300)

                # Export the enhanced audio
                enhanced_output = f"enhanced_{output_file}"
                enhanced_audio.export(enhanced_output, format="mp3")

                # Play the audio
                audio_obj = Audio(enhanced_output, autoplay=True)
                display(audio_obj)

                return enhanced_output

            except Exception as e:
                print(f"Enhancement error: {e}")
                # Fallback to original audio
                audio_obj = Audio(output_file, autoplay=True)
                display(audio_obj)
                return output_file

        except Exception as e:
            print(f"Speech generation error: {e}")
            return None

    def _compress_dynamic_range(self, sound, threshold=-20.0, ratio=1.5):
        """Basic dynamic range compression for clearer audio"""

        def gain_computer(dB, threshold, ratio):
            if dB < threshold:
                return 0
            else:
                return (threshold - dB) * (1 - 1 / ratio)

        # Process the audio
        samples = np.array(sound.get_array_of_samples())
        # Convert to float & normalize
        samples = samples.astype(np.float32) / np.iinfo(np.int16).max

        # Calculate dB
        dB = 20 * np.log10(np.abs(samples) + 1e-10)
        gain_reduction = np.array([gain_computer(d, threshold, ratio) for d in dB])
        gain_reduction_linear = 10 ** (gain_reduction / 20)
        compressed_samples = samples * gain_reduction_linear

        # Convert back to int16
        compressed_samples = (compressed_samples * np.iinfo(np.int16).max).astype(np.int16)

        # Create a new audio segment
        compressed_sound = sound._spawn(compressed_samples.tobytes())
        return compressed_sound

    def _format_dynamic_content(self, text):
        """Replace placeholders with dynamic content"""
        if "{current_time}" in text:
            import datetime
            # Format time in Nepali style
            now = datetime.datetime.now()
            time_str = now.strftime("%I:%M %p")
            text = text.replace("{current_time}", time_str)
        return text

    async def listen(self):
        """Listen for user input - simplified version for demo"""
        # In a real implementation, this would use a microphone
        # For now, we'll simulate with text input
        print("🎤 कृपया बोल्नुहोस् (वा टाइप गर्नुहोस्):")
        user_input = input()
        return user_input

    async def process_command(self, text):
        """Process the user's command and determine response"""
        # Check for direct matches in responses dictionary
        for key, responses in self.responses.items():
            if key.lower() in text.lower():
                # Get a random response from the list
                import random
                response = random.choice(responses)
                await self.speak(response)
                return True

        # Check for action triggers
        for key, action_func in self.actions.items():
            if key.lower() in text.lower():
                await action_func()
                return True

        # If no match found, use default response
        import random
        default = random.choice(self.responses["default"])
        await self.speak(default)
        return False

    # Action functions
    async def tell_time(self):
        """Tell the current time in Nepali"""
        import datetime
        now = datetime.datetime.now()
        # Format time in Nepali style
        time_str = now.strftime("%I:%M %p")

        response = f"अहिले समय {time_str} भएको छ"
        await self.speak(response)

    async def play_music(self):
        """Simulate playing music"""
        await self.speak("माफ गर्नुहोस्, अहिले संगीत बजाउने सुविधा उपलब्ध छैन")

    async def weather_info(self):
        """Simulate providing weather information"""
        await self.speak("माफ गर्नुहोस्, मौसम जानकारी हेर्न मलाई इन्टरनेट आवश्यक छ")

    async def run(self):
        """Run the voice assistant in continuous mode"""
        await self.speak("नमस्ते! म तपाईंको नेपाली सहयोगी हुँ। मलाई बोलाउन '{}' भन्नुहोस्।".format(self.wake_word))

        self.listening = False

        while True:
            # Wait for user input
            user_input = await self.listen()

            # Check if this is a wake word when not already listening
            if not self.listening:
                if self.wake_word.lower() in user_input.lower():
                    self.listening = True
                    wake_responses = self.responses.get(self.wake_word, ["हजुर, भन्नुहोस्"])
                    import random
                    await self.speak(random.choice(wake_responses))
                continue

            # Process the command
            if user_input.lower() in ["बन्द गर", "बिदा", "धन्यवाद"]:
                await self.speak("ठिक छ, फेरि भेटौंला")
                self.listening = False
                continue

            # Otherwise process the command
            await self.process_command(user_input)

    def add_custom_response(self, trigger, responses):
        """Add or modify custom responses to the assistant

        Parameters:
        - trigger: The text that triggers this response
        - responses: List of possible responses to choose from
        """
        if not isinstance(responses, list):
            responses = [responses]  # Convert single string to list

        self.responses[trigger] = responses
        print(f"Added response for '{trigger}'")

    def add_custom_action(self, trigger, action_function):
        """Add a custom action to the assistant

        Parameters:
        - trigger: The text that triggers this action
        - action_function: Async function to call when triggered
        """
        self.actions[trigger] = action_function
        print(f"Added action for '{trigger}'")


# Example usage
async def main():
    # Create the assistant
    assistant = NepaliVoiceAssistant(
        voice="ne-NP-HemkalaNeural",
        volume_boost=4.0,
        wake_word="सहयोगी"
    )

    # Add some custom responses
    assistant.add_custom_response("मेरो नाम", ["तपाईंको भेट्न पाउँदा खुसी लाग्यो"])
    assistant.add_custom_response("मौसम कस्तो छ", ["आज मौसम सफा छ", "आज घाम लागेको छ"])

    # Example of adding a custom action (must be async)
    async def tell_joke():
        await assistant.speak(
            "एउटा नेपाली जोक: एक जना मान्छे होटलमा गए अनि भने, 'चिया खानु होला!'. होटेल संचालकले भने, 'चिया पिउनु हुन्छ कि खानु हुन्छ?'")

    assistant.add_custom_action("जोक सुनाउ", tell_joke)

    # Test with some examples
    print("\n👋 स्वागतम् नेपाली सहयोगी (Nepali Voice Assistant)")
    print("---------------------------------------------")

    # Test basic responses
    print("\n🔊 Testing basic greeting:")
    await assistant.speak("नमस्ते! म तपाईंको नेपाली डिजिटल सहयोगी हुँ। तपाईंलाई कसरी मद्दत गर्न सक्छु?")

    # Test time function
    print("\n🔊 Testing time function:")
    await assistant.tell_time()

    # Example conversation loop
    print("\n🔊 Starting conversation mode (type 'बन्द गर' to exit):")
    print("---------------------------------------------")
    print("सहयोगी (to wake up the assistant)")
    print("तिमी को हौ? (to ask who the assistant is)")
    print("समय कति भयो? (to ask the time)")
    print("जोक सुनाउ (to hear a joke)")
    print("मौसम कस्तो छ? (to ask about weather)")
    print("बन्द गर (to exit)")

    # Uncomment to run in interactive mode
    # await assistant.run()

    # For demo purposes, simulate a conversation
    print("\n🔊 Demo conversation:")
    await assistant.process_command("सहयोगी")
    time.sleep(1)
    await assistant.process_command("तिमी को हौ")
    time.sleep(1)
    await assistant.process_command("समय कति भयो")
    time.sleep(1)
    await assistant.process_command("जोक सुनाउ")
    time.sleep(1)
    await assistant.process_command("धन्यवाद")


# Run the assistant
if __name__ == "__main__" or 'ipykernel' in sys.modules:
    asyncio.run(main())