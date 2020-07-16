from pathlib import Path
import json
import numpy as np


def load_last_sample():
    
    my_file = Path("last_sample.json")
    if my_file.is_file():
        with open(my_file) as f:
            last_sample = json.load(f)

        upper_hsv = np.array(last_sample['upper'])
        lower_hsv = np.array(last_sample['lower'])
        return lower_hsv, upper_hsv