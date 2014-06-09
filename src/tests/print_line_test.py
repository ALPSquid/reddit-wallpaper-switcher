import sys
import time

number = 11
spaces = ""
for i in range(60):
    spaces += " "

def print_line():
    global number
    for i in range(number):
        print("\r"+spaces),
        print("\rTest"+str(number-i)),
        time.sleep(0.5)

def write_line():
    global number
    for i in range(number):
        sys.stdout.flush()
        sys.stdout.write("Test"+str(number-i))    
        time.sleep(0.5)

#write_line()
print_line()
