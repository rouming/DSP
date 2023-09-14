#!/usr/bin/python3
"""
Draw DFFT
"""
import sys
import arcade as ar
import numpy as np
import datetime
import seaborn as sns
import soundfile as sf

# Constants
SCREEN_TITLE = "Draw DFFT"
PALETTE = [(int(255 * rgb[0]),int(255 * rgb[1]),int(255 * rgb[2])) for rgb in
           sns.color_palette("Spectral", 100)]
FREQ_LIM   = 100
AMPL_SCALE = 200
TIME_SCALE = 1./80

class freq():
    def __init__(self, f, ampl):
        self.f = f
        self.ampl = ampl

    def draw(self, dt, center):
        p = np.exp(2*np.pi*1j*dt*self.f)
        p = np.array([p.real, p.imag])

        radius = AMPL_SCALE * self.ampl
        p = center + p * radius

        color = PALETTE[int(self.f) % len(PALETTE)]

        ar.draw_circle_outline(center[0], center[1],  radius, color)
        ar.draw_circle_filled(center[0], center[1], 3.0, color)
        ar.draw_line(center[0], center[1], p[0], p[1], color, 2)
        ar.draw_circle_filled(p[0], p[1], 3.0, color)

        return p


class draw_fft(ar.Window):
    def __init__(self, fft_freq, fft_data):
        sz = ar.get_display_size(0)
        super().__init__(sz[0], sz[1], SCREEN_TITLE)
        ar.set_background_color(ar.csscolor.CORNFLOWER_BLUE)

        fft_mag = np.abs(fft_data)
        fft_mag = fft_mag / np.linalg.norm(fft_mag)
        fft_freq = fft_freq[:FREQ_LIM]

        self.ts = datetime.datetime.now().timestamp()
        self.points = np.empty((0,2))
        self.freqs = []
        for f, mag in zip(fft_freq, fft_mag):
            self.freqs.append(freq(f, mag))

    def setup(self):
        pass

    def on_draw(self):
        """ Render the screen. """
        ar.start_render()

        ts = datetime.datetime.now().timestamp()
        dt = (ts - self.ts) * TIME_SCALE
        revol_n = np.floor(dt)

        w, h = self.get_size()
        start_p = p = np.array([w/2 - 400, h/2])

        for freq in self.freqs:
            p = freq.draw(dt, p)

        if revol_n >= 1:
            self.points = self.points[1:]

        end = np.array([start_p[0] + 300, p[1]])
        ar.draw_line(p[0], p[1], end[0], end[1], ar.color.BLACK, 1)
        p = end

        self.points = np.append(self.points, [p], axis=0)

        # Shift all points to the right
        self.points += (0.4, 0)

        ar.draw_points(self.points.tolist(), ar.color.GREEN, 5)



def main(args):
    if len(args) == 1:
        print("Usage: <file>...")
        sys.exit(1)

    data, rate = sf.read(args[1])
    fft_freq = np.fft.rfftfreq(len(data), d=1./rate)
    fft_data = np.fft.rfft(data)

    window = draw_fft(fft_freq, fft_data)
    window.setup()
    ar.run()


if __name__ == "__main__":
    main(sys.argv)
