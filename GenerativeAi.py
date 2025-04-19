import os
import azure.cognitiveservices.speech as speechsdk
from openai import AzureOpenAI
import string

speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
speech_config.speech_recognition_language="en-US"

emotion_keywords = {
    "happy": ["great", "awesome", "happy", "good", "fantastic"],
    "sad": ["bad", "sad", "terrible", "awful", "sorry"],
    "angry": ["mad", "angry", "annoyed", "frustrated", "hate"],
    "neutral": ["okay", "fine", "alright", "whatever"]
}

keyword_to_emotion = {}
for emotion, keywords in emotion_keywords.items():
    for keyword in keywords:
        keyword_to_emotion[keyword] = emotion
        
emotion_scores = {"happy": 0, "sad": 0, "angry": 0, "neutral": 0}

def detect_emotion(user_input):
    words = user_input.lower().split()
    words = [word.translate(str.maketrans('', '', string.punctuation)) for word in words]
    
    for word in words:
        if word in keyword_to_emotion:
            emotion_scores[keyword_to_emotion[word]] += 1
    
    dominant_emotion = max(emotion_scores, key=emotion_scores.get)
    max_score = emotion_scores[dominant_emotion]
    
    return "neutral" if max_score == 0 else dominant_emotion

def recognize_from_microphone():
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    print("Speak into your microphone.")
    speech_recognition_result = speech_recognizer.recognize_once_async().get()

    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Recognized: {}".format(speech_recognition_result.text))
        return speech_recognition_result.text
    elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
        return "No voice detected"
    elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_recognition_result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
            print("Did you set the speech resource key and region values?")
    
    
def textToSpeech(text):
    speaker_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=speaker_config)
    text2speech = speech_synthesizer.speak_text_async(text).get()

def generate_respond(update_emotion, playOrNot):
    client = AzureOpenAI(
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
        api_key = os.getenv("AZURE_OPENAI_API_KEY"),  
        api_version="2024-12-01-preview"
    )
    
    count = 0
    current_emotion0 = "neutral"
    playMusic = True 
    
    conversation=[{"role": "system", "content": "You are a helpful home assistant. You should always care about the user's feeling"}]

    conversation.append({"role": "assistant", "content": "How is your day?"})
    textToSpeech("How is your day?")
    print("How is your day?")
    
    while True:
        
        user_input = recognize_from_microphone()  
         
        if user_input == "No voice detected":
            textToSpeech("Sorry, can you say it again?")
            continue
        elif "No" in user_input  and count == 3:
            playMusic = False
        
        conversation.append({"role": "user", "content": user_input})
        current_emotion0 = detect_emotion(user_input)
        print("test: " + str(emotion_scores))
        print("cur: " + current_emotion0)

        response = client.chat.completions.create(
                model="gpt-35-turbo", # model = "deployment_name".
                messages=conversation
            )

        if count == 2:
            conversation.append({"role": "assistant", "content": response.choices[0].message.content + "Do you want some music?"})
            print("\n" + response.choices[0].message.content + " So do you want some music?\n")
            textToSpeech(response.choices[0].message.content + " So do you want some music?")
        else:
            conversation.append({"role": "assistant", "content": response.choices[0].message.content})
            print("\n" + response.choices[0].message.content + "\n")
            textToSpeech(response.choices[0].message.content)
        
        if "bye" in response.choices[0].message.content.lower() or "goodbye" in response.choices[0].message.content.lower() or count == 2:
            playOrNot(playMusic)
            update_emotion(current_emotion0)
            break
        
        count += 1

