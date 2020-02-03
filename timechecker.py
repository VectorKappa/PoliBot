import time
import datetime

poprawneGodziny = (8, 9, 10, 11, 12)

def czyPrzerwa():
    now = datetime.datetime.now()
    for now.hour in poprawneGodziny:
        
    print(now.hour, now.minute)
    pass

czyPrzerwa()