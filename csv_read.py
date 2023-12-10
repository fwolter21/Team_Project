import pandas as pd 
import numpy as np


def read_csv(file):
    try: 
        data = pd.read_csv(file)
        return data 
    except Exception as e: 
        print(f'sorry but there is a problem: {e}')
        return None








