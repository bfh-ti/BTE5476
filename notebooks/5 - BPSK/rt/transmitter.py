import numpy as np

from datalink import DataLink
from BPSK import BPSK


class BPSK_TX(BPSK, DataLink):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        DataLink.__init__(self)

    def transmit(self, message, gap_len_ms=25, **kwargs):
        gap = np.zeros(int(self.sf / 1000 * gap_len_ms))
        bits = 2 * (self.encode_message(message, **kwargs) - 0.5)
        x = np.cos(self.wc * np.arange(0, len(bits) * self.spb)) * np.kron(bits, np.ones(self.spb))
        return np.r_[ gap, x, gap ], bits


if __name__ == '__main__':
    import sys
    from scipy.io import wavfile

    assert len(sys.argv) == 3, 'usage: transmit.py filename text'

    transmitter = Transmitter()
    x = transmitter.transmit(sys.argv[2])
    resc = np.array(32600 * x, dtype=np.int16)
    wavfile.write(sys.argv[1], 32000, resc)
    print(f'output written to {sys.argv[1]}')