# Initial Code from https://www.educative.io/answers/how-to-play-an-audio-file-in-pygame
from pygame import mixer

def sound():
    mixer.init()
    mixer.music.load("C:\\Users\\shaun\\Desktop\\Shaun\\Winter2024Classes\\Applied_Programming\\ELOE-Platformer\\Assets\\SpaceMusic1Edit.wav")
    mixer.music.set_volume(0.2)
    mixer.music.play()
    # while True:
    #     print("Press 'p' to pause the music")
    #     print("Press 'r' to resume the music")
    #     print("Press 'e' to exit the program")
    
    #     #take user input
    #     userInput = input(" ")
        
    #     if userInput == 'p':

    #         # Pause the music
    #         mixer.music.pause()	
    #         print("music is paused....")
    #     elif userInput == 'r':

    #         # Resume the music
    #         mixer.music.unpause()
    #         print("music is resumed....")
    #     elif userInput == 'e':

    #         # Stop the music playback
    #         mixer.music.stop()
    #         print("music is stopped....")
    #         break