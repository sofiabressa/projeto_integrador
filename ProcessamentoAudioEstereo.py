import soundcard as sc
import numpy as np
import cv2
import math
from collections import deque

# Filtro de suavização
historico_angulo = deque(maxlen=5)

# Limiar de silêncio (se o volume for menor que isso, zeramos o ângulo)
LIMIAR_SILENCIO = 0.01  

def desenhar_radar(angulo):
    img = np.zeros((400, 400, 3), dtype=np.uint8)
    
    # Desenhar círculo do radar
    cv2.circle(img, (200, 200), 150, (0, 255, 0), 2)
    
    # Converter ângulo em coordenadas no círculo
    raio = 150
    x = int(200 + raio * math.cos(math.radians(angulo + 90)))
    y = int(200 - raio * math.sin(math.radians(angulo + 90)))

    # Desenhar ponto no radar
    cv2.circle(img, (x, y), 10, (0, 0, 255), -1)

    cv2.imshow("Radar de Som", img)
    cv2.waitKey(10)

# Cálculo do ângulo do som para estéreo
def calcular_angulo_som(left_channel, right_channel, samplerate):
    # Normalizar os sinais (remover offset DC)
    left_channel = left_channel - np.mean(left_channel)
    right_channel = right_channel - np.mean(right_channel)

    # Calcular volume de cada canal
    volume_left = np.mean(np.abs(left_channel))
    volume_right = np.mean(np.abs(right_channel))
    volume_total = volume_left + volume_right

    # Se o volume for menor que o limiar, centralizar a bolinha
    if volume_total < LIMIAR_SILENCIO:
        historico_angulo.clear()
        return 0

    # Calcular a diferença de volume entre os canais
    volume_diff = (volume_left - volume_right) / (volume_left + volume_right + 1e-6)

    # Normalizar a diferença de volume para o intervalo [-90, 90]
    angulo_diff = np.clip(volume_diff * 90, -90, 90)

    # Aplicar suavização usando média móvel
    historico_angulo.append(angulo_diff)
    angulo_suavizado = np.mean(historico_angulo)

    return angulo_suavizado

# Processamento de áudio
def processar_audio_em_tempo_real(mic, samplerate, numframes):
    try:
        with mic.recorder(samplerate=samplerate) as recorder:
            print("Processamento de áudio iniciado...")
            while True:
                data = recorder.record(numframes=numframes)

                # Verifica se os dados possuem dois canais
                if data.shape[1] == 2:
                    left_channel = data[:, 0]
                    right_channel = data[:, 1]

                    # Calcular ângulo do som
                    angulo = calcular_angulo_som(left_channel, right_channel, samplerate)
                    print(f"Ângulo do som: {angulo:.2f}°")

                    desenhar_radar(angulo)
                else:
                    print("O dispositivo não possui canais estéreo. Direção não pode ser calculada.")
    except KeyboardInterrupt:
        print("\nProcessamento de áudio encerrado.")
        cv2.destroyAllWindows()

def main():
    speakers = sc.all_speakers()
    print("Dispositivos de alto-falante disponíveis:")
    for i, speaker in enumerate(speakers):
        print(f"{i}: {speaker.name}")

    default_speaker = sc.default_speaker()
    print(f"\nUsando o dispositivo de áudio: {default_speaker.name}")

    mic = sc.get_microphone(default_speaker.name, include_loopback=True)
    if not mic:
        print("Não foi possível ativar o loopback para este dispositivo.")
        exit()

    samplerate = 44100
    numframes = 1024
    processar_audio_em_tempo_real(mic, samplerate, numframes)

if __name__ == "__main__":
    main()
