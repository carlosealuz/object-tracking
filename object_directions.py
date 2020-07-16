import keyboard_movement_functions as kb_function

def check_direction_to_move(object_center):
    x = object_center[0]
    y = object_center[1]
    if (x >= 0 and x <= 155) and (y >= 100 and y <= 380):
        return 'left'
    if (x >= 485 and x <= 640) and (y >= 100 and y <= 380):
        return 'right'
    if (x >= 160 and x <= 480) and (y >= 0 and y <= 100):
        return 'up'
    if (x >= 160 and x <= 480) and (y >= 380 and y <= 640):
        return 'down'

def direction_to_action(object_direction):
    switcher = {
        'left': kb_function.previous_browser_tab,
        'right': kb_function.next_browser_tab,
        'up': kb_function.page_up,
        'down': kb_function.page_down
    }
    function = switcher.get(object_direction, lambda: 'No direction')
    return function()