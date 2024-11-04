import numpy as np

from BPSK import BPSK
from datalink import DataLink
from biquads import BQLowpass, BQBandpass


class BPSK_RX(BPSK, DataLink):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        DataLink.__init__(self)

    # your code here...


    def receive(self, s):
        # your code here...
        pass


if __name__ == '__main__':
    import sys
    import time
    from scipy.io import wavfile
    import pyaudio

    CAPTURE_LEN_SEC = 20

    # set up pyaudio for real-time processing
    Fs = 16000
    audio_io = pyaudio.PyAudio()

    if len(sys.argv) <3:
        print('usage: receiver.py audio_device bps [capture]')
        print('Available audio input devices:')
        info = audio_io.get_host_api_info_by_index(0)
        n = info.get('deviceCount')
        for i in range(0, n):
            if (audio_io.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                print(f'  device id {i} : ', audio_io.get_device_info_by_host_api_device_index(0, i).get('name'))
        exit()

    capture_buffer, capture_ix = None, 0
    if len(sys.argv) == 4:
        capture_buffer = np.zeros(Fs * CAPTURE_LEN_SEC).astype(np.int16)

    # instantiate the receiver
    receiver = BPSK_RX(bps=int(sys.argv[2]), sf=Fs)

    # portaudio callback
    def callback(in_data, frame_count, time_info, status):
        global receiver, capture_buffer, capture_ix
        in_audio = np.frombuffer(in_data, dtype=np.int16)
        N = len(in_audio)
        if capture_buffer is not None:
            m = max(0, min(len(capture_buffer) - capture_ix, N))
            capture_buffer[capture_ix:capture_ix+m] = in_audio[:m]
            capture_ix += m
        receiver.receive(in_audio / 32767.0)
        return None, pyaudio.paContinue

    # start
    stream = audio_io.open(
                    input_device_index=int(sys.argv[1]),
                    format=audio_io.get_format_from_width(2),   # 16 bits per sample
                    channels=1,                                 # mono input
                    rate=Fs,
                    input=True,
                    output=False,
                    frames_per_buffer=1024,
                    stream_callback=callback)

    stream.start_stream()
    while stream.is_active():
        if capture_buffer is not None and capture_ix >= len(capture_buffer):
            wavfile.write(f'../capture{sys.argv[2]}.wav', Fs, capture_buffer)
            capture_buffer = None
            print(f'audio capture saved')
        time.sleep(1)

    stream.stop_stream()
    stream.close()
    audio_io.terminate()
