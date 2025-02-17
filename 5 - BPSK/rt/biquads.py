import numpy as np

class BiQuad():
    def __init__(self, b, a):
        self.a, self.b = a, b
        self.w1, self.w2 = 0, 0

    def filter(self, x):
        # biquad, direct form II implementation
        w = x - self.a[1] * self.w1 - self.a[2] * self.w2
        y = self.b[0] * w + self.b[1] * self.w1 + self.b[2] * self.w2
        self.w2, self.w1 = self.w1, w
        return y


class BQLowpass(BiQuad):
    def __init__(self, fc, sf):
        # using the biquad recipe from the cookbook
        Q = 1 / np.sqrt(2)
        w = 2 * np.pi * fc / sf
        alpha = np.sin(w) / (2 * Q)
        c = np.cos(w)
        a = np.array([1 + alpha, -2 * c, 1 - alpha])
        b = np.array([(1 - c) / 2, 1 - c, (1 - c) / 2])
        super().__init__(b / a[0], a / a[0])


class BQBandpass(BiQuad):
    def __init__(self, fc, bw, sf):
        # using the biquad recipe from the cookbook
        w = 2 * np.pi * fc / sf
        alpha = np.tan(np.pi * bw / sf)
        c = np.cos(w)
        b = np.array([alpha, 0, -alpha])
        a = np.array([1 + alpha, -2 * c, 1 - alpha])
        super().__init__(b / a[0], a / a[0])