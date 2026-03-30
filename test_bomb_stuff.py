#################################
# CSC 102 Defuse the Bomb Project
# GUI and Phase class definitions
# Team: Kayla Riggall, Cyron Gray, Nabil Sabbooba
#################################

from bomb_configs import *
from tkinter import *
import tkinter
from threading import Thread
from time import sleep
import os
import sys

class Lcd(Frame):
    def __init__(self, window):
        super().__init__(window, bg="black")
        window.attributes("-fullscreen", True)
        self._timer = None
        self._button = None
        self.setupBoot()

    def setupBoot(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.columnconfigure(2, weight=1)
        self._lscroll = Label(self, bg="black", fg="white", font=("Courier New", 14), text="", justify=LEFT)
        self._lscroll.grid(row=0, column=0, columnspan=3, sticky=W)
        self.pack(fill=BOTH, expand=True)

    def setup(self):
        self._ltimer = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="Time left: ")
        self._ltimer.grid(row=1, column=0, columnspan=3, sticky=W)
        self._lkeypad = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="Keypad phase: ")
        self._lkeypad.grid(row=2, column=0, columnspan=3, sticky=W)
        self._lwires = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="Wires phase: ")
        self._lwires.grid(row=3, column=0, columnspan=3, sticky=W)
        self._lbutton = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="Button phase: ")
        self._lbutton.grid(row=4, column=0, columnspan=3, sticky=W)
        self._ltoggles = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="Toggles phase: ")
        self._ltoggles.grid(row=5, column=0, columnspan=2, sticky=W)
        self._lstrikes = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="Strikes left: ")
        self._lstrikes.grid(row=5, column=2, sticky=W)
        
        if (SHOW_BUTTONS):
            self._bpause = tkinter.Button(self, bg="red", fg="white", font=("Courier New", 18), text="Pause", command=self.pause)
            self._bpause.grid(row=6, column=0, pady=40)
            self._bquit = tkinter.Button(self, bg="red", fg="white", font=("Courier New", 18), text="Quit", command=self.quit)
            self._bquit.grid(row=6, column=2, pady=40)

    def setTimer(self, timer):
        self._timer = timer

    def setButton(self, button):
        self._button = button

    def pause(self):
        if (RPi):
            self._timer.pause()

    def conclusion(self, success=False):
        self._lscroll["text"] = "MISSION SUCCESS" if success else "FATAL ERROR: EXPLOSION"
        self._ltimer.destroy()
        self._lkeypad.destroy()
        self._lwires.destroy()
        self._lbutton.destroy()
        self._ltoggles.destroy()
        self._lstrikes.destroy()
        
        self._bretry = tkinter.Button(self, bg="red", fg="white", font=("Courier New", 18), text="Retry", command=self.retry)
        self._bretry.grid(row=1, column=0, pady=40)
        self._bquit = tkinter.Button(self, bg="red", fg="white", font=("Courier New", 18), text="Quit", command=self.quit)
        self._bquit.grid(row=1, column=2, pady=40)

    def retry(self):
        os.execv(sys.executable, ["python3"] + [sys.argv[0]])
        exit(0)

    def quit(self):
        if (RPi):
            self._timer._running = False
            self._timer._component.fill(0)
            for pin in self._button._rgb:
                pin.value = True
        exit(0)

class PhaseThread(Thread):
    def __init__(self, name, component=None, target=None):
        super().__init__(name=name, daemon=True)
        self._component = component
        self._target = target
        self._defused = False
        self._failed = False
        self._value = None
        self._running = False

class Timer(PhaseThread):
    def __init__(self, component, initial_value, name="Timer"):
        super().__init__(name, component)
        self._value = initial_value
        self._paused = False
        self._min = ""
        self._sec = ""
        self._interval = 1

    def run(self):
        self._running = True
        while (self._running):
            if (not self._paused):
                self._update()
                self._component.print(str(self))
                sleep(self._interval)
                if (self._value == 0):
                    self._running = False
                self._value -= 1
            else:
                sleep(0.1)

    def _update(self):
        self._min = f"{self._value // 60}".zfill(2)
        self._sec = f"{self._value % 60}".zfill(2)

    def pause(self):
        self._paused = not self._paused
        self._component.blink_rate = (2 if self._paused else 0)

    # Modification: Added Reset functionality
    def reset(self, new_value):
        self._value = new_value
        self._update()

    def __str__(self):
        return f"{self._min}:{self._sec}"

class Keypad(PhaseThread):
    def __init__(self, component, target, name="Keypad"):
        super().__init__(name, component, target)
        self._value = ""

    def run(self):
        self._running = True
        while (self._running):
            if (self._component.pressed_keys):
                while (self._component.pressed_keys):
                    try:
                        key = self._component.pressed_keys[0]
                    except:
                        key = ""
                    sleep(0.1)
                
                self._value += str(key)
                
                # Modification: Limit to 4 characters (showing last 4)
                if len(self._value) > 4:
                    self._value = self._value[-4:]

                if (self._value == self._target):
                    self._defused = True
                elif (self._value != self._target[0:len(self._value)]):
                    self._failed = True
            sleep(0.1)

    def __str__(self):
        return "DEFUSED" if self._defused else self._value

class Wires(PhaseThread):
    def __init__(self, component, target, name="Wires"):
        super().__init__(name, component, target)
        # Modification: Added invalid combination for Alarm/Status logic
        self._invalid_comb = "11111" 

    def run(self):
        self._running = True
        while (self._running):
            # Get current wire states (0 for connected/pulled down, 1 for disconnected)
            # Component is a list of pins
            current_state = "".join(["1" if pin.value else "0" for pin in self._component])
            self._value = current_state

            # Status logic: Check for invalid combination (all wires out)
            if self._value == self._invalid_comb:
                self._failed = True 
            
            # Win condition: check against target from genSerial()
            if int(self._value, 2) == self._target:
                self._defused = True
                
            sleep(0.1)

    def __str__(self):
        return "DEFUSED" if self._defused else self._value

class Button(PhaseThread):
    def __init__(self, component_state, component_rgb, target, color, timer, name="Button"):
        super().__init__(name, component_state, target)
        self._value = False
        self._pressed = False
        self._rgb = component_rgb
        self._color = color
        self._timer = timer
        # Modification: Added press counter
        self._press_count = 0

    def run(self):
        self._running = True
        # Set RGB LED color
        self._rgb[0].value = False if self._color == "R" else True
        self._rgb[1].value = False if self._color == "G" else True
        self._rgb[2].value = False if self._color == "B" else True
        
        while (self._running):
            self._value = self._component.value
            if (self._value):
                if not self._pressed:
                    # Modification: Increment counter on initial press
                    self._press_count += 1
                self._pressed = True
            else:
                if (self._pressed):
                    if (not self._target or self._target in self._timer._sec):
                        self._defused = True
                    else:
                        self._failed = True
                    self._pressed = False
            sleep(0.1)

    def __str__(self):
        if (self._defused):
            return f"DEFUSED ({self._press_count} presses)"
        return str("Pressed" if self._value else "Released")

class Toggles(PhaseThread):
    def __init__(self, component, target, name="Toggles"):
        super().__init__(name, component, target)

    def run(self):
        self._running = True
        while (self._running):
            # Read pins and convert to binary value
            current_val = "".join(["1" if pin.value else "0" for pin in self._component])
            self._value = int(current_val, 2)
            
            if self._value == self._target:
                self._defused = True
            sleep(0.1)

    def __str__(self):
        return "DEFUSED" if self._defused else bin(self._value if self._value else 0)[2:].zfill(4)
