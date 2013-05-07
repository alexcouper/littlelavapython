import RPi.GPIO as GPIO, time
import thread
from Queue import Queue

input_queue = Queue()

LEDS = {
    'r': 25,
    'g': 23,
    'b': 18,
}

BUTTONS = {
    'r': 22,
    'g': 17,
    'b': 4,
}


def configure_board():
    GPIO.setmode(GPIO.BCM)

    for pin in LEDS.values():
        GPIO.setup(pin, GPIO.OUT)

    for pin in BUTTONS.values():
        GPIO.setup(pin, GPIO.IN)


def set_colour(colour, on=True):
    """Set the given colour to the ``on`` state.

    :param colour:
        The colour identifier to set.

    :param on:
        If True, the LED will turn on. If False turned off.
    """
    GPIO.output(LEDS[colour], on)


def flash(on=True):
    for led_col, pin in LEDS.items():
        GPIO.output(pin, on)


def game_emulate_buttons():
    while 1:
        colours, on = input_queue.get(block=True)
        print "Show button game: Got {0}, {1}".format(colours, on)
        for col in colours:
            set_colour(col, on)


def input_loop():
    last_time = {}
    while True:
        gone_down = []
        gone_up = []
        for colour, pin in BUTTONS.items():
            last_val = last_time.get(pin, True)
            now_val = GPIO.input(pin)

            if last_val != now_val:
                last_time[pin] = now_val
                if not now_val:
                    gone_down.append(colour)
                else:
                    gone_up.append(colour)

        # detect double or triple clicks:
        if gone_down:
            input_queue.put((tuple(gone_down), True))
        if gone_up:
            input_queue.put((tuple(gone_up), False))

        time.sleep(0.1)


def main():
    configure_board()
    flash(False)
    thread.start_new_thread(game_emulate_buttons, ())
    input_loop()

if __name__ == '__main__':
    main()
