import pyaudio
import curiosity


p = pyaudio.PyAudio()

print(p.get_default_input_device_info())
print(p.get_device_count())