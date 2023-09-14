#!/usr/bin/python3
"""
Draw DFFT
"""
import arcade as ar
import numpy as np
import datetime
import seaborn as sns

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Draw DFFT"

PALETTE = [(int(255 * rgb[0]),int(255 * rgb[1]),int(255 * rgb[2])) for rgb in
           sns.color_palette("Spectral", 20)]

class freq():
    def __init__(self, f, ampl):
        self.f = f
        self.ampl = ampl

    def draw(self, dt, center):
        p = np.exp(2*np.pi*1j*dt*self.f)
        p = np.array([p.real, p.imag])

        radius = 100 * self.ampl
        p = center + p * radius

        ar.draw_circle_outline(center[0], center[1],  radius, PALETTE[self.f])
        ar.draw_circle_filled(center[0], center[1], 3.0, PALETTE[self.f])
        ar.draw_line(center[0], center[1], p[0], p[1], PALETTE[self.f], 2)
        ar.draw_circle_filled(p[0], p[1], 3.0, PALETTE[self.f])

        return p


class MyGame(ar.Window):
    """
    Main application class.
    """

    def __init__(self):

        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        ar.set_background_color(ar.csscolor.CORNFLOWER_BLUE)

        self.ts = datetime.datetime.now().timestamp()
        self.points = []
        self.freqs = [freq(1, 1), freq(3, 0.5), freq(7, 0.3), freq(10, 0.1)]

    def setup(self):
        """ Set up the game here. Call this function to restart the game. """
        pass

    def on_draw(self):
        """ Render the screen. """
        ar.start_render()

        ts = datetime.datetime.now().timestamp()
        dt = (ts - self.ts)/10
        revol_n = np.floor(dt)

        w, h = self.get_size()
        p = np.array([w/2, h/2])

        for freq in self.freqs:
            p = freq.draw(dt, p)

        if revol_n >= 1:
            self.points.pop(0)
        self.points.append(p)

#        self.points += 1

        ar.draw_points(self.points, ar.color.GREEN, 5)



def main():
    """ Main method """
    window = MyGame()
    window.setup()
    ar.run()


if __name__ == "__main__":
    main()
