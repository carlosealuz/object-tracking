from pynput.keyboard import Key, Controller
import pynput.mouse as pymouse
import time

keyboard = Controller()
mouse = pymouse.Controller()

def debounce(s):
    """
    Decorator ensures function that can only be called once every `s` seconds.
    """
    def decorate(f):
        t = None

        def wrapped(*args, **kwargs):
            nonlocal t
            t_ = time.time()
            if t is None or t_ - t >= s:
                result = f(*args, **kwargs)
                t = time.time()
                return result
        return wrapped
    return decorate

@debounce(.5)
def next_browser_tab():
    keyboard.press(Key.ctrl_l)
    keyboard.press(Key.tab)
    keyboard.release(Key.tab)
    keyboard.release(Key.ctrl)

@debounce(.5)
def previous_browser_tab():
    keyboard.press(Key.ctrl_l)
    keyboard.press(Key.shift_l)
    keyboard.press(Key.tab)
    keyboard.release(Key.tab)
    keyboard.release(Key.shift_l)
    keyboard.release(Key.ctrl)

@debounce(.1)
def page_up():
    mouse.scroll(0, 2)

@debounce(.1)
def page_down():
    mouse.scroll(0, -2)


