import numpy as np
from scipy.io.wavfile import write

# Gera um bip de 100ms a 880Hz
sample_rate = 44100
duration = 0.1  # 100ms
frequency = 880  # 880Hz (nota A5)

t = np.linspace(0, duration, int(sample_rate * duration), False)
audio = np.sin(frequency * t * 2 * np.pi) * 0.5  # 0.5 = volume médio
audio_int16 = (audio * 32767).astype(np.int16)

write("bip.wav", sample_rate, audio_int16)