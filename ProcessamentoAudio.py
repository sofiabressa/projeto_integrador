import soundcard as sc
import numpy as np

def listar_dispositivos_audio():
    speakers = sc.all_speakers()
    print("Dispositivos de alto-falante disponíveis:")
    for i, speaker in enumerate(speakers):
        print(f"{i}: {speaker.name}")
    return speakers

def obter_alto_falante_padrao():
    default_speaker = sc.default_speaker()
    print(f"\nUsando o dispositivo de áudio: {default_speaker.name}")
    return default_speaker

def ativar_loopback(default_speaker):
    mic = sc.get_microphone(default_speaker.name, include_loopback=True)
    if not mic:
        print("Não foi possível ativar o loopback para este dispositivo. Verifique a compatibilidade.")
        exit()
    return mic

def calcular_direcao(left_channel, right_channel, samplerate):
    correlation = np.correlate(left_channel, right_channel, mode='full')
    lag = np.argmax(correlation) - (len(left_channel) - 1)
    time_difference = lag / samplerate

    if time_difference > 0:
        return "Direita"
    elif time_difference < 0:
        return "Esquerda"
    else:
        return "Centro"

def processar_audio_em_tempo_real(mic, samplerate, numframes):
    try:
        with mic.recorder(samplerate=samplerate) as recorder:
            print("Processamento de áudio iniciado...")
            while True:
                # Capturar um frame de áudio
                data = recorder.record(numframes=numframes)

                # Verifica se os dados possuem dois canais
                if data.shape[1] == 2:
                    left_channel = data[:, 0]
                    right_channel = data[:, 1]

                    # Calcular a direção do som
                    direcao = calcular_direcao(left_channel, right_channel, samplerate)
                    print(f"Direção do som: {direcao}")
                else:
                    print("O dispositivo não possui canais estéreo. Direção não pode ser calculada.")
    except KeyboardInterrupt:
        print("\nProcessamento de áudio encerrado.")

def main():
    
    listar_dispositivos_audio()
    default_speaker = obter_alto_falante_padrao()
    mic = ativar_loopback(default_speaker)
    samplerate = 44100
    numframes = 1024
    processar_audio_em_tempo_real(mic, samplerate, numframes)

if __name__ == "__main__":
    main()
