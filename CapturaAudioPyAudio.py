import pyaudio
import wave

# Parâmetros da gravação
FORMAT = pyaudio.paInt16
CHANNELS = 2  # Número de canais (estéreo)
RATE = 44100  # Taxa de amostragem (44.1kHz)
CHUNK = 1024  # Número de frames por buffer
DURATION = 10  
OUTPUT_FILE = "audio_capturado_pyaudio.wav"

p = pyaudio.PyAudio()
device_index = 3

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=CHUNK)

print("Gravando...")

frames = []

# Captura o áudio
for _ in range(0, int(RATE / CHUNK * DURATION)):
    data = stream.read(CHUNK)
    frames.append(data)

print("Gravação concluída.")

# Encerra o stream
stream.stop_stream()
stream.close()
p.terminate()

# Salva o áudio capturado em um arquivo WAV
with wave.open(OUTPUT_FILE, 'wb') as wf:
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))

print(f"Áudio salvo em: {OUTPUT_FILE}")
