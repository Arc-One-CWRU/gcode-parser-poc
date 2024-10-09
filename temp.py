from time import sleep
from duetwebapi import DuetWebAPI
duet = DuetWebAPI("http://192.168.0.4")
print("test")
all = []
flag = True

with open("temp.txt", "w") as f:
    while True:
        try:
            temp = duet.get_temperatures()
            all.append(temp)
            f.write(str(temp))
            print(temp)
            sleep(.2)
        except Exception as e:
            print(e)