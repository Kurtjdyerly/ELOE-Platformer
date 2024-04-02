# Initial Code from https://www.educative.io/answers/how-to-play-an-audio-file-in-pygame
import pygame
from pygame import mixer

def sound():
    mixer.init()
    mixer.music.load("Assets/SpaceMusic1Edit.wav")
    mixer.music.set_volume(0.2)
    mixer.music.play(-1)

def pause(key):
    if key[pygame.K_p]:
        mixer.music.pause()

def resume(key):
    if key[pygame.K_r]:
        mixer.music.unpause()

def death():
    death_cry = mixer.Sound("Assets\DeathCry1.wav")
    mixer.Sound.set_volume(death_cry, 0.2)
    mixer.Sound.play(death_cry)

def jumping():
    jump_noise = mixer.Sound("Assets\Jump_01.wav")
    mixer.Sound.set_volume(jump_noise, 0.2)
    mixer.Sound.play(jump_noise)