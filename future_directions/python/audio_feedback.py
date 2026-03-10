import numpy as np
import sounddevice as sd

def beep():

    fs = 44100

    t = np.linspace(0,0.1,int(fs*0.1))

    tone = np.sin(2*np.pi*800*t)

    sd.play(tone,fs)