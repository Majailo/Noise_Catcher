import psutil

def list_audio_devices():
    devices = psutil.disk_partitions()
    audio_devices = [device.device for device in devices if 'audio' in device.opts]
    return audio_devices

audio_devices = list_audio_devices()
print("Périphériques audio connectés :", audio_devices)