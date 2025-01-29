import soundcard as sc
import numpy as np
import cv2
import math
from collections import deque

# Filtro de suavização
historico_angulo = deque(maxlen=5)  # Média móvel para suavizar

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
def calcular_angulo_som(left_channel, right_channel, samplerate):
    # Normalizar os sinais 
    left_channel = left_channel - np.mean(left_channel)
    right_channel = right_channel - np.mean(right_channel)

    # Calcular volume médio
    volume_left = np.mean(np.abs(left_channel))
    volume_right = np.mean(np.abs(right_channel))
    volume_total = (volume_left + volume_right) / 2

    # Se o volume for menor que o limiar, considerar silêncio
    if volume_total < LIMIAR_SILENCIO:
        historico_angulo.clear()  # Resetar histórico para evitar erro
        return 0  # Centralizar a bolinha

    # Tempo de atraso entre os canais
    correlation = np.correlate(left_channel, right_channel, mode='full')
    lag = np.argmax(correlation) - (len(left_channel) - 1)
    time_difference = lag / samplerate

    # Diferença de volume entre os canais
    volume_diff = (volume_left - volume_right) / (volume_left + volume_right + 1e-6)

    # Ajustar pesos para equilíbrio entre o tempo de atraso e a diferença dos volumes
    peso_itd = 0.7
    peso_ild = 0.3

    # Normalizar tempo de atraso para ±90°
    max_time_difference = 0.0008
    angulo_itd = np.clip((time_difference / max_time_difference) * 90, -90, 90)

    # Converter para ângulo (-90 a 90 baseado na diferença de volume)
    angulo_ild = np.clip(volume_diff * 90, -90, 90)

    # Combinar os dois cálculos para um ângulo mais preciso
    angulo_final = (peso_itd * angulo_itd) + (peso_ild * angulo_ild)

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
