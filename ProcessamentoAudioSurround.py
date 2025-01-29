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
    x = int(200 + raio * math.cos(math.radians(angulo)))
    y = int(200 - raio * math.sin(math.radians(angulo)))

    # Desenhar ponto no radar
    cv2.circle(img, (x, y), 10, (0, 0, 255), -1)

    cv2.imshow("Radar de Som", img)
    cv2.waitKey(10)

# Calculo do ângulo do som
def calcular_angulo_som(canais, samplerate):
    # Normalizar os sinais (remover offset DC)
    canais = canais - np.mean(canais, axis=0)

    volumes = np.mean(np.abs(canais), axis=0)
    volume_total = np.sum(volumes)

    # Se o volume for menor que o limiar
    if volume_total < LIMIAR_SILENCIO:
        historico_angulo.clear()  # Resetar histórico para evitar erro
        return 0  # Centralizar a bolinha

    # Determinar o canal com maior volume (usando uma média ponderada entre todos os canais)
    max_volume_index = np.argmax(volumes)

    # Mapear o canal com maior volume para uma direção específica
    angulos = {
        0: 0,   # Centro
        1: -45, # Frente esquerda
        2: 45,  # Frente direita
        3: -90, # Trás esquerda
        4: 90,  # Trás direita
        5: -135, # Esquerda
        6: 135, # Direita
        7: 180  # Subwoofer (opcional)
    }
    
    angulo_final = angulos.get(max_volume_index, 0)

    # Aplicar suavização usando média móvel
    historico_angulo.append(angulo_final)
    angulo_suavizado = np.mean(historico_angulo)

    return angulo_suavizado

# Processamento de audio
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
        cv2.destroyAllWindows()  # Fecha a janela do radar

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
