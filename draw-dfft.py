#!/usr/bin/python3
"""
Draw DFFT
"""
import sys
import arcade as ar
from arcade.experimental.uislider import UISlider
from arcade.gui import UIManager, UIAnchorWidget, UILabel
from arcade.gui.events import UIOnChangeEvent
import numpy as np
import datetime
import soundfile as sf
import random
from optparse import OptionParser
from PIL import Image
from svgpathtools import svg2paths, path
from tsp_solver.greedy_numpy import solve_tsp

# Constants
SCREEN_TITLE = "Draw DFFT"

# Don't show info about frequencies with magnitute below this threshold
MAG_THRESH = 0.1
# Don't show circles with radious below this threshold. This dramatically
# optimizes drawing on number of frequencies > 1000
RADIUS_THRESH = 2.0
AMPL_SCALE = 200
FREQ_SCALE = 0.5
_1_DIM_TIME_SCALE = 1
MAX_POINTS = 1000

BLACK_THRESHOLD = 128

class freq():
    def __init__(self, f, phase, ampl):
        self.f = f
        self.phase = phase
        self.ampl = ampl

    def draw(self, dt, center):
        # Calculate rotation vector
        p = np.exp(-1j * (self.phase + dt * self.f))
        p = np.array([p.real, p.imag])

        # Scale radius
        radius = AMPL_SCALE * self.ampl
        p = center + p * radius

        if radius > RADIUS_THRESH:
            # Don't spend resources on almost invisible circles.
            # This dramatically increases performance on number
            # of frequencies > 1000

            c1 = (200, 200, 200, 100)
            c2 = (100, 100, 100, 100)
            c3 = (150, 0, 0, 100)

            ar.draw_circle_outline(center[0], center[1],  radius, c1)
            ar.draw_line(center[0], center[1], p[0], p[1], c2, 2)
            ar.draw_circle_filled(center[0], center[1], 4.0, c3)

        return p

class draw_fft(ar.Window):
    def setup_ui(self, is_1_dim):
        sz = ar.get_display_size(0)
        super().__init__(sz[0], sz[1], SCREEN_TITLE)
        ar.set_background_color(ar.csscolor.CORNFLOWER_BLUE)

        # Required, create a UI manager to handle all UI widgets
        self.manager = UIManager()
        self.manager.enable()

        # Frequncy slider placement
        freq_slider = UISlider(value=50, width=500, height=50)
        @freq_slider.event()
        def on_change(event: UIOnChangeEvent):
            global FREQ_SCALE
            FREQ_SCALE = freq_slider.value / 100

        self.manager.add(UIAnchorWidget(anchor_x="right", anchor_y="top",
                                        align_x=-20,
                                        child=freq_slider))
        self.manager.add(UIAnchorWidget(anchor_x="right", anchor_y="top",
                                        align_x=-freq_slider.width - 40,
                                        align_y=-15,
                                        child=UILabel(text=f"Frequency")))

        # Amplitude slider placement
        ampl_slider = UISlider(value=50, width=500, height=50)
        @ampl_slider.event()
        def on_change(event: UIOnChangeEvent):
            global AMPL_SCALE
            AMPL_SCALE = ampl_slider.value * 4

        self.manager.add(UIAnchorWidget(anchor_x="right", anchor_y="top",
                                        align_x=-20,
                                        align_y=-50,
                                        child=ampl_slider))
        self.manager.add(UIAnchorWidget(anchor_x="right", anchor_y="top",
                                        align_x=-ampl_slider.width - 40,
                                        align_y=-ampl_slider.height - 15,
                                        child=UILabel(text=f"Amplitude",
                                        align_y=100)))

        # Points history slider placement
        hist_slider = UISlider(value=50, width=500, height=50)
        @hist_slider.event()
        def on_change(event: UIOnChangeEvent):
            global MAX_POINTS
            MAX_POINTS = int(1000 * (hist_slider.value/100))

        self.manager.add(UIAnchorWidget(anchor_x="right", anchor_y="top",
                                        align_x=-20,
                                        align_y=-100,
                                        child=hist_slider))
        self.manager.add(UIAnchorWidget(anchor_x="right", anchor_y="top",
                                        align_x=-ampl_slider.width - 40,
                                        align_y=-ampl_slider.height - 65,
                                        child=UILabel(text=f"History",
                                        align_y=100)))


        if is_1_dim:
            # 1-dim time slider placement
            time_slider = UISlider(value=50, width=500, height=50)
            @time_slider.event()
            def on_change(event: UIOnChangeEvent):
                global _1_DIM_TIME_SCALE
                _1_DIM_TIME_SCALE = time_slider.value / 50.0

            self.manager.add(UIAnchorWidget(anchor_x="right", anchor_y="top",
                                            align_x=-20,
                                            align_y=-150,
                                            child=time_slider))
            self.manager.add(UIAnchorWidget(anchor_x="right", anchor_y="top",
                                            align_x=-ampl_slider.width - 40,
                                            align_y=-ampl_slider.height - 115,
                                            child=UILabel(text=f"X axis (time)",
                                                          align_y=100)))

    def __init__(self, is_1_dim, fft_data, fft_freq):
        # Setup UI
        self.setup_ui(is_1_dim)

        # Get magnitude and normalize
        fft_mag = np.abs(fft_data)
        fft_mag = fft_mag / np.linalg.norm(fft_mag)
        # Get phase
        fft_phase = np.angle(fft_data)

        mag_indices = [{"mag": mag, "ind": i} for i, mag in
                       enumerate(fft_mag)]
        sorted_indices = [each['ind'] for each in
                          sorted(mag_indices, key=lambda each: each['mag'],
                                 reverse=True)]

        # Select magnitude higher than threshold
        ind = np.argwhere(fft_mag > MAG_THRESH)
        self.mag_thresh = fft_mag[ind].flatten()
        self.freq_thresh = fft_freq[ind].flatten()

        self.dt = 0
        self.is_1_dim = is_1_dim
        self.points = np.empty((0,2))
        self.freqs = []
        for i in sorted_indices:
            f = fft_freq[i]
            phase = fft_phase[i]
            mag = fft_mag[i]
            self.freqs.append(freq(f, phase, mag))

    def setup(self):
        pass

    def on_draw(self):
        """ Render the screen. """
        ar.start_render()
        w, h = self.get_size()

        # Draw found frequencies
        text_y = h/2
        for f in self.freq_thresh:
            text = "%3.3fHz" % f
            ar.draw_text(text, w/2, text_y, ar.color.WHITE,
                         10, width=300)
            text_y -= 20

        start_p = p = np.array([w/2 - 400, h/2])
        self.dt += 0.01 * FREQ_SCALE

        # Draw each frequency circle
        for freq in self.freqs:
            p = freq.draw(self.dt, p)

        if self.is_1_dim:
            # Draw projection line
            end = np.array([start_p[0] + 300, p[1]])
            ar.draw_line(p[0], p[1], end[0], end[1], ar.color.BLACK, 1)
            p = end

        # Limit points
        if len(self.points) > MAX_POINTS:
            self.points = self.points[len(self.points) - MAX_POINTS:]

        # Pick up a point
        self.points = np.append(self.points, [p], axis=0)

        if self.is_1_dim:
            # Simulate time for 1-dim case by shifting all points to the right.
            # For the 2-dim case time is Z-axis, which points to the screen,
            # which we don't see
            self.points += (0.7 * _1_DIM_TIME_SCALE, 0)

        # Draw the whole points list
        for p in self.points:
            r = 4.0
            ar.draw_circle_filled(p[0], p[1], r, ar.color.GREEN,
                                  num_segments=int(2.0 * np.pi * r / 3.0))

        # Draw UI
        self.manager.draw()


# Slow fourier transform :)
def sft(sig):
    n = len(sig)
    zeta = np.exp(-2 * np.pi * 1j / n)
    freq = np.array([np.array([sig[i] * zeta**(i * f) for i in range(0, n)]).sum()
            for f in range(0, n)])
    return freq

def image_to_points(image, num, threshold):
    h, w = image.shape
    black_pixels_n = (image < threshold).sum()
    assert black_pixels_n > num, "No pixels of specified threshold in the image!"
    points = np.zeros(num, dtype=complex)
    for i in range(num):
        while True:
            x = int(random.random() * w)
            y = int(random.random() * h)
            # Black threshold
            if image[y, x] < threshold:
                break
        # Convert to complex
        points[i] = x + y*1j
    return points

def distance_matrix(points):
    m = np.array([points] * len(points))
    return np.abs(m - m.T)

def read_raster_image(filename):
    image = Image.open(filename).convert("RGBA")
    # Alpha as white
    bg = Image.new("RGBA", image.size, (255,255,255))
    # Greyscale, stores only 'L'uminance
    image = Image.alpha_composite(bg, image).convert("L")
    return np.asarray(image)

def process_raster_file(filename, num):
    image = read_raster_image(filename)
    points = image_to_points(image, num, BLACK_THRESHOLD)
    dist = distance_matrix(points)
    indices = solve_tsp(dist)
    return points[indices]

def process_vector_file(filename, num):
    paths, _ = svg2paths(filename)
    paths = path.concatpaths(paths)
    time = np.linspace(0.0, 1.0, num)
    points = np.array([paths.point(t) for t in time], dtype=complex)
    return points

def process_audio_file(filename, num):
    data, rate = sf.read(filename)[:num]
    if len(data.shape) > 1:
        # Only first channel
        data = data[:, 0]
    return data, rate

def process_file_and_fft(filename, options):
    ext = filename.split(".")[-1]
    is_1_dim = False
    if ext == "wav":
        points, rate = process_audio_file(filename, options.samples_count)
        # Audio signal is 1-dim, so we are not interested in negative
        # frequencies
        start = len(points) // 2
        is_1_dim = True
    elif ext in ("png", "jpeg", "svg"):
        if ext == "svg":
            points = process_vector_file(filename, options.samples_count)
        else:
            points = process_raster_file(filename, options.samples_count)
        rate = len(points)
        # 2-dim signal, take negative frequencies into account
        start = len(points) // 2 - options.freq_count // 2

    end = start + options.freq_count

    # FFT calculation
    fft_freq = np.fft.fftfreq(len(points), d=1./rate)
    fft_data = np.fft.fft(points)
    # Drop 0 frequency
    fft_freq = fft_freq[1:]
    fft_data = fft_data[1:]
    # Orgainize frequencies naturally: from negative to positive
    fft_freq = np.fft.fftshift(fft_freq)
    fft_data = np.fft.fftshift(fft_data)
    # Slice
    fft_freq = fft_freq[start:end]
    fft_data = fft_data[start:end]

    return is_1_dim, fft_data, fft_freq


def main():
    usage = "Usage: %prog [OPTIONS] FILE"
    parser = OptionParser(usage=usage,
                          description="Draws an image or a signal from an audio (.wav), raster (.png, .jpeg) or vector (.svg) FILE using DTTF")
    parser.add_option("-p", "--samples-count", type="int", default=1000,
                      dest="samples_count", help="Number of samples extracted from input image or audio")
    parser.add_option("-c", "--freq-count", type="int", default=1000,
                      dest="freq_count", help="Number of frequencies")
    options, args = parser.parse_args()

    if len(args) == 0:
        parser.print_help()
        sys.exit(1)
    else:
        filename = args[0]

    is_1_dim, fft_data, fft_freq = process_file_and_fft(filename, options)

    window = draw_fft(is_1_dim, fft_data, fft_freq)
    window.setup()
    ar.run()

if __name__ == "__main__":
    main()
