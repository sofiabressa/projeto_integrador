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

# Cálculo do ângulo do som
def calcular_angulo_som(canais, samplerate):
    # Normalizar os sinais (remover offset DC)
    canais = canais - np.mean(canais, axis=0)

    # Calcular o volume de cada canal
    volumes = np.mean(np.abs(canais), axis=0)
    volume_total = np.sum(volumes)

    # Se o volume for menor que o limiar, centralizar a bolinha
    if volume_total < LIMIAR_SILENCIO:
        historico_angulo.clear()
        return 0 

    # Mapear os canais para ângulos específicos (em graus)
    angulos = {
        0: 30,   # Frente Esquerda (FL)
        1: 330,  # Frente Direita (FR)  (360 - 30)
        2: 0,    # Centro (C)
        3: 90,   # Lateral Esquerda (SL)
        4: 270,  # Lateral Direita (SR)
        5: 150,  # Trás Esquerda (RL)
        6: 210,  # Trás Direita (RR)
        7: None  # Subwoofer (LFE)
    }

    # Calcular a média ponderada dos ângulos com base nos volumes
    angulo_final = 0
    peso_total = 0
    for i, volume in enumerate(volumes):
        if i in angulos and angulos[i] is not None:  # Ignorar o subwoofer
            angulo_final += angulos[i] * volume
            peso_total += volume

    if peso_total > 0:
        angulo_final /= peso_total  # Normalizar pelo peso total
    else:
        angulo_final = 0

    # Aplicar suavização usando média móvel
    historico_angulo.append(angulo_final)
    angulo_suavizado = np.mean(historico_angulo)

    return angulo_suavizado

# Processamento de áudio
def processar_audio_em_tempo_real(mic, samplerate, numframes):
    try:
        with mic.recorder(samplerate=samplerate) as recorder:
            print("Processamento de áudio iniciado...")
            while True:
                data = recorder.record(numframes=numframes)

                if data.shape[1] == 8:
                    # Cada coluna representa um canal (7.1)
                    # Calcular ângulo do som com base nos canais
                    angulo = calcular_angulo_som(data, samplerate)
                    print(f"Ângulo do som: {angulo:.2f}°")

                    desenhar_radar(angulo)
                else:
                    print("O dispositivo não possui 7.1 canais. Direção não pode ser calculada.")
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