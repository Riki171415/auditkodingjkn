from concurrent.futures import ProcessPoolExecutor
from modules.data_loader import get_icd_dict

def task(i):
    return len(get_icd_dict())

if __name__ == '__main__':
    p = ProcessPoolExecutor(1)
    print(p.submit(task, 1).result())
