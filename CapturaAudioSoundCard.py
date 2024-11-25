import soundcard as sc
import numpy as np
import soundfile as sf

#speaker = sc.get_speaker("Alto-falantes (Realtek(R) Audio)") 
speaker = sc.get_speaker("Alto-falantes (2- USB Audio Device)") 
mic = sc.get_microphone(speaker.name, include_loopback=True)

# Define a taxa de amostragem, o número de frames por amostra e a duração da gravação em segundos
samplerate = 44100
numframes = 1024
duration_seconds = 10
output_file = "audio_capturado_soundcard.wav"

total_frames = duration_seconds * samplerate

with sf.SoundFile(output_file, mode='w', samplerate=samplerate, channels=2) as file:
    with mic.recorder(samplerate=samplerate) as recorder:
        frames_recorded = 0
        while frames_recorded < total_frames:
            data = recorder.record(numframes=numframes)
            print("Gravando:", frames_recorded / samplerate, "segundos")
            file.write(data) 
            frames_recorded += numframes

print("Gravação concluída.")
