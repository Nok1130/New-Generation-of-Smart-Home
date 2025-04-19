from EmotionDetection import *
from GenerativeAi import *
from playMusic import *
from threading import Thread, Event
import random

song_list = {
    "happy": [
        "Can't Stop the Feeling",
        "Happy",
        "Feel it",
        "Dancing Queen",
        "Cake By The Ocean"
    ],
    "sad": [
        "Sad Forever",
        "Tears in Heaven",
        "The Night We Met",
        "I Really Want To Stay At Your House",
        "Here With Me"
    ],
    "angry": [
        "Head In The Clouds",
        "Closure",
        "Wait",
        "Stars"
    ],
    "neutral": [
        "Espresso",
        "Nothing New",
        "Beautiful Things",
        "Am I Dreaming",
        "STAY"
    ]
}

emotion1, emotion2 = "", ""
playMusic = True
emotion1Updated = Event()
emotion2Updated = Event()
decidePlayMusic = Event()

def printEmotion1():
    print("Emotion 1 from Face Recognition AI is " + emotion1)
    
def printEmotion2():
    print("Emotion 2 from Generative AI is " + emotion2)   
    
def printPlayMusic():
    print("Play Music? " + str(playMusic))  
    
def update_emotion1(new_emotion):
    global emotion1
    emotion1 = new_emotion.lower()
    emotion1Updated.set()
    
def update_emotion2(new_emotion):
    global emotion2
    emotion2 = new_emotion.lower()
    emotion2Updated.set()
    
def playOrNot(answer):
    global playMusic
    playMusic = answer
    decidePlayMusic.set()

detectFace = Thread(target = main, args=(update_emotion1, ))
talk = Thread(target = generate_respond, args=(update_emotion2, playOrNot, ))

detectFace.start()
talk.start()

emotion1Updated.wait()

emotion2Updated.wait()

decidePlayMusic.wait()

detectFace.join()
talk.join()

printEmotion1()
printEmotion2()
printPlayMusic()

if emotion1 == emotion2 and playMusic == True:
    selected_song = random.choice(song_list[emotion1])
    play_song(selected_song)
elif emotion1 != emotion2 and playMusic == True:
    selected_song = random.choice(song_list["neutral"])
    play_song(selected_song)
