import numpy as np


class DataLink:
    WAIT_SYNC, WAIT_START, DECODE, SKIP_1, SKIP_2 = 0, 1, 2, 3, 4

    def __init__(self):
        self.MAX_ONES, self.SYNC_WORD = 5, self.char2bits(chr(0b01111110))
        self.START_SYNCS = 5
        self.FRAME_SIZE = 10  # bytes
        self.last_bit = False
        self.reset()

    @classmethod
    def char2bits(cls, c):
        return np.array([b == '1' for b in format(ord(c), '08b')])

    @classmethod
    def bits2char(cls, b):
        return chr(np.uint8(b @ [128, 64, 32, 16, 8, 4, 2, 1]))

    def encode_message(self, text, repeat=1, preamble=0):
        self.count, self.ones = 0, 0
        ret = np.tile(self.SYNC_WORD, preamble)

        for i in range(0, repeat):
            ret = np.r_[ret, np.tile(self.SYNC_WORD, self.START_SYNCS + 1)]
            for c in text:
                self.count += 1
                if self.count >= self.FRAME_SIZE:
                    ret = np.r_[ret, self.SYNC_WORD]
                    self.count, self.ones = 0, 0

                for b in self.char2bits(c):
                    ret = np.r_[ret, b]
                    self.ones = self.ones + 1 if b else 0
                    if self.ones == self.MAX_ONES:
                        ret = np.r_[ret, False]  # bit stuffing
                        self.ones = 0

                        # append a "wrong" sync word to stop the receiver
        ret = np.r_[ret, self.SYNC_WORD, self.SYNC_WORD[:-1], True]

        # differential encoding via XOR
        for n in range(1, len(ret)):
            ret[n] = ret[n] != ret[n - 1]
        return ret

    def reset(self):
        self.count, self.ones, self.syncs = 0, 0, 0
        self.buf = np.full(8, False)
        self.state, self.resume = self.WAIT_SYNC, self.WAIT_START

    def decode_stream(self, bits, reset=False):
        if reset:
            self.reset()

        ret = ''
        for bit in bits:
            # differential decoding via XOR
            b = self.last_bit != bit
            self.last_bit = bit

            if self.state == self.SKIP_1:
                # if we're here, either there's a stuffed bit or a new sync word
                self.state = self.SKIP_2 if b else self.DECODE
                continue
            elif self.state == self.SKIP_2:
                if b:  # something's wrong, let's wait for the next start burst
                    self.reset()
                else:
                    self.count = 0
                    self.state = self.DECODE
                continue

            self.count += 1
            self.buf = np.r_[self.buf[1:], b]
            self.ones = self.ones + 1 if b else 0

            if self.state == self.WAIT_SYNC:
                if np.equal(self.buf, self.SYNC_WORD).all():
                    self.count, self.ones, self.syncs = 0, 0, 0
                    self.state = self.resume

            elif self.state == self.WAIT_START:
                if self.count == 8:
                    self.count = 0
                    self.syncs = self.syncs + 1 if np.equal(self.buf, self.SYNC_WORD).all() else 0
                if self.syncs >= self.START_SYNCS:
                    self.count, self.ones, self.syncs = 0, 0, 0
                    self.state = self.resume = self.DECODE

            else:  # decoding
                if self.count == 8:
                    ret += self.bits2char(self.buf)
                    self.count = 0
                if self.ones == self.MAX_ONES:
                    # remove stuffed bit or skip sync word
                    self.ones = 0
                    self.state = self.SKIP_1
        return ret