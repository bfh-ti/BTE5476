class BPSK:
    Fs = 16000
    CARRIER_HZ = 2000
    BPS = 50

    def __init__(self, fc=CARRIER_HZ, bps=BPS, sf=Fs):
        self.sf = sf
        print(f'target values at Fs={sf} Hz: {bps} bits per second, {fc} Hz carrier')
        # we want an integer number of samples per bit, so we adjust the other params accordingly
        self.spb = int(sf / bps)
        self.bps = sf / self.spb
        self.ppb = int(fc / self.bps)
        self.fc = self.ppb * self.bps
        print(
            f'  best match: {self.bps:.2f} bits per second ({self.spb} samples per bit), {self.fc:.2f} Hz carrier ({self.ppb} periods per bit)')
        self.wc = 6.283185307179586 * self.fc / sf