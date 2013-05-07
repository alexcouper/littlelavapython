import RPi.GPIO as GPIO, time
import thread
from Queue import Queue

input_queue = Queue()
LEDS = {
    'g': 18,
    'r': 23,
    'b': 25
}
BUTTONS = {
    'g': 4,
    'r': 17,
    'b': 22,
}

LEVELS = [
    (['r', 'g', 'b', 'b'], 0.5),
    (['r', 'g', 'g', 'b', 'b'], 0.4),
    (['r', 'g', 'b', 'g', 'r'], 0.35),
    (['g', 'g', 'b', 'r', 'r', 'g', 'b', 'b', 'g'], 0.3),
    (['g', 'b', 'b', 'g', 'g', 'r'], 0.25),
    (['b', 'r', 'g', 'b', 'r'], 0.2),
]


def configure_board():
    GPIO.setmode(GPIO.BCM)

    for pin in LEDS.values():
        GPIO.setup(pin, GPIO.OUT)

    for pin in BUTTONS.values():
        GPIO.setup(pin, GPIO.IN)


def play_level(seq, pause):
    for col in seq:
        set_colour(col, single=True)
        time.sleep(0.1)
        set_colour(col, on=False)
        time.sleep(pause)


def set_colour(colour, on=True, single=False):
    """Set the given colour to the ``on`` state.

    :param colour:
        The colour identifier to set.

    :param on:
        If True, the LED will turn on. If False turned off.

    :param single:
        If ``on`` and True then all other lights will be turned off.
        Otherwise this is ignored.
    """
    GPIO.output(LEDS[colour], on)
    if on and single:
        for led_col, pin in LEDS.items():
            if led_col != colour:
                GPIO.output(pin, False)


def flash(on=True):
    for led_col, pin in LEDS.items():
        GPIO.output(pin, on)


def level_complete():
    print "LEVEL COMPLETE"
    for i in range(4):
        flash(True)
        time.sleep(0.2)
        flash(False)
        time.sleep(0.2)


def level_failed():
    print "LEVEL FAILED"
    for i in range(4):
        set_colour('r', single=True)
        time.sleep(0.2)
        set_colour('r', on=False)
        time.sleep(0.2)


def game_copy_sequence():
    level_complete()
    for sequence, pause in LEVELS:
        passed = False
        while not passed:
            play_level(sequence, pause)
            answer = wait_for_answer()
            if check_answer(answer, sequence):
                level_complete()
                passed = True
            else:
                level_failed()
                flash(False)
                time.sleep(0.5)
        print "NEXT LEVEL!"


def check_answer(answer, test):
    print "answer was: {0}".format(answer)
    print "test was: {0}".format(test)
    return answer == test


def wait_for_answer():
    answer = []
    time.sleep(0.3)
    while 1:
        try:
            colour, on = input_queue.get(block=True, timeout=0.5)
            if on:
                answer.append(colour)
        except Exception as e:
            print e, type(e)
            break
    return answer


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
