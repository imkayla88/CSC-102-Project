#################################
# CSC 102 Defuse the Bomb Project
# GUI and Phase class definitions
# Team: Cyron, Kayla, and Nabil

#Dr Matt was here
#################################

# import the configs
from bomb_configs import *
# other imports
from tkinter import *
import tkinter
from threading import Thread
from time import sleep
import os
import sys
from PIL import Image, ImageTk
#########
# classes
#########
# the LCD display GUI
class Lcd(Frame):
    def __init__(self, window):
        super().__init__(window, bg="black")
        # make the GUI fullscreen
        window.attributes("-fullscreen", True)
        # we need to know about the timer (7-segment display) to be able to pause/unpause it
        self._timer = None
        # we need to know about the pushbutton to turn off its LED when the program exits
        self._button = None
        # setup the initial "boot" GUI
        self.setupBoot()

    # sets up the LCD "boot" GUI
    def setupBoot(self):
        self.pack(fill=BOTH, expand=True)
        
        # get the screen size
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # open and resize the background image to fit the screen
        bg = Image.open("starsbackground.gif")
        bg = bg.resize((screen_width, screen_height))
        
        # convert it so Tkinter can use it
        self.bg_image = ImageTk.PhotoImage(bg)
        
        # place the background behind everything
        self.bg_label = Label(self, image=self.bg_image)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_label.lower()
        # set column weights
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.columnconfigure(2, weight=1)
        self._title = Label(self, bg="black", fg="#00ff00", font=("Courier New", 30, "bold"), text="DEFUSE THE BOMB")
        self._title.grid(row=0, column=0, columnspan=3, pady=(30, 10))
        # the scrolling informative "boot" text
        self._lscroll = Label(self, bg="black", fg="#00ff00", font=("Courier New", 14), text="", justify=LEFT)
        self._lscroll.grid(row=1, column=0, columnspan=3, sticky=W, padx=40)
        self.pack(fill=BOTH, expand=True)
        
        # kill switch button (always visible)
        self._bkill = tkinter.Button(
        self,
        bg="red",
        fg="white",
        font=("Courier New", 16),
        text="KILL SWITCH",
        command=self.kill_switch)
        self._bkill.place(relx=1, rely=0, anchor="ne")
    def kill_switch(self):
        import pygame
        pygame.mixer.music.stop()
        self.quit()

    # sets up the LCD GUI
    def setup(self):
        # the keypad passphrase
        self._lkeypad = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="Keypad phase: ")
        self._lkeypad.grid(row=2, column=0, columnspan=3, sticky=W)
        # the jumper wires status
        self._lwires = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="Wires phase: ")
        self._lwires.grid(row=3, column=0, columnspan=3, sticky=W)
        # the pushbutton status
        self._lbutton = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="Button phase: ")
        self._lbutton.grid(row=4, column=0, columnspan=3, sticky=W)
        # the toggle switches status
        self._ltoggles = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="Toggles phase: ")
        self._ltoggles.grid(row=5, column=0, columnspan=2, sticky=W)
        # the strikes left
        self._lstrikes = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="Strikes left: ")
        self._lstrikes.grid(row=5, column=2, sticky=W)
        if (SHOW_BUTTONS):
            # the pause button (pauses the timer)
            self._bpause = tkinter.Button(self, bg="red", fg="white", font=("Courier New", 18), text="Pause", anchor=CENTER, command=self.pause)
            self._bpause.grid(row=6, column=0, pady=40)
            # the quit button
            self._bquit = tkinter.Button(self, bg="red", fg="white", font=("Courier New", 18), text="Quit", anchor=CENTER, command=self.quit)
            self._bquit.grid(row=6, column=2, pady=40)

    # lets us pause/unpause the timer (7-segment display)
    def setTimer(self, timer):
        self._timer = timer

    # lets us turn off the pushbutton's RGB LED
    def setButton(self, button):
        self._button = button

    # pauses the timer
    def pause(self):
        if (RPi):
            self._timer.pause()

    # setup the conclusion GUI (explosion/defusion)
    def conclusion(self, success=False):
        # clear the old text
        self._lscroll["text"] = ""

        # remove the game labels from the screen
        self._lkeypad.destroy()
        self._lwires.destroy()
        self._lbutton.destroy()
        self._ltoggles.destroy()
        self._lstrikes.destroy()

        if (SHOW_BUTTONS):
            self._bpause.destroy()
            self._bquit.destroy()

        # choose the correct ending GIF
        if success:
            self.end_image = PhotoImage(file="win.gif")
        else:
            self.end_image = PhotoImage(file="lose.gif")

        # show the GIF on the screen
        self.end_label = Label(self, image=self.end_image, bg="black")
        self.end_label.grid(row=0, column=0, columnspan=3, pady=20)

        # retry button
        self._bretry = tkinter.Button(
            self,
            bg="red",
            fg="white",
            font=("Courier New", 18),
            text="Retry",
            anchor=CENTER,
            command=self.retry
        )
        self._bretry.grid(row=1, column=0, pady=40)

        # quit button
        self._bquit = tkinter.Button(
            self,
            bg="red",
            fg="white",
            font=("Courier New", 18),
            text="Quit",
            anchor=CENTER,
            command=self.quit
        )
        self._bquit.grid(row=1, column=2, pady=40)

    # re-attempts the bomb (after an explosion or a successful defusion)
    def retry(self):
        # re-launch the program (and exit this one)
        os.execv(sys.executable, ["python3"] + [sys.argv[0]])
        exit(0)

    # quits the GUI, resetting some components
    def quit(self):
        if (RPi):
            # turn off the 7-segment display
            self._timer._running = False
            self._timer._component.blink_rate = 0
            self._timer._component.fill(0)
            # turn off the pushbutton's LED
            for pin in self._button._rgb:
                pin.value = True
        # exit the application
        exit(0)

# template (superclass) for various bomb components/phases
class PhaseThread(Thread):
    def __init__(self, name, component=None, target=None):
        super().__init__(name=name, daemon=True)
        # phases have an electronic component (which usually represents the GPIO pins)
        self._component = component
        # phases have a target value (e.g., a specific combination on the keypad, the proper jumper wires to "cut", etc)
        self._target = target
        # phases can be successfully defused
        self._defused = False
        # phases can be failed (which result in a strike)
        self._failed = False
        # phases have a value (e.g., a pushbutton can be True/Pressed or False/Released, several jumper wires can be "cut"/False, etc)
        self._value = None
        # phase threads are either running or not
        self._running = False

# the timer phase
class Timer(PhaseThread):
    def __init__(self, component, initial_value, name="Timer"):
        super().__init__(name, component)
        # the default value is the specified initial value
        self._value = initial_value
        # is the timer paused?
        self._paused = False
        # initialize the timer's minutes/seconds representation
        self._min = ""
        self._sec = ""
        # by default, each tick is 1 second
        self._interval = 1

    # runs the thread
    def run(self):
        self._running = True
        while (self._running):
            if (not self._paused):
                # update the timer and display its value on the 7-segment display
                self._update()
                
                self._component.print(str(self))
                # wait 1s (default) and continue
                sleep(self._interval)
                # the timer has expired -> phase failed (explode)
                if (self._value == 0):
                    self._running = False
                self._value -= 1
            else:
                sleep(0.1)

    # updates the timer (only internally called)
    def _update(self):
        self._min = f"{self._value // 60}".zfill(2)
        self._sec = f"{self._value % 60}".zfill(2)

    # pauses and unpauses the timer
    def pause(self):
        # toggle the paused state
        self._paused = not self._paused
        # blink the 7-segment display when paused
        self._component.blink_rate = (2 if self._paused else 0)

    # returns the timer as a string (mm:ss)
    def __str__(self):
        return f"{self._min}:{self._sec}"

# the keypad phase
class Keypad(PhaseThread):
    def __init__(self, component, target, name="Keypad"):
        super().__init__(name, component, target)
        # the default value is an empty string
        self._value = ""

    # runs the thread
    def run(self):
        self._running = True
        while (self._running):
            # process keys when keypad key(s) are pressed
            if (self._component.pressed_keys):
                # debounce
                while (self._component.pressed_keys):
                    try:
                        # just grab the first key pressed if more than one were pressed
                        key = self._component.pressed_keys[0]
                    except:
                        key = ""
                    sleep(0.1)
                # log the key
                self._value += str(key)
                # the combination is correct -> phase defused
                if (self._value == self._target):
                    self._defused = True
                # the combination is incorrect -> phase failed (strike)
                elif (self._value != self._target[0:len(self._value)]):
                    self._failed = True
            sleep(0.1)

    # returns the keypad combination as a string
    def __str__(self):
        if (self._defused):
            return "DEFUSED"
        else:
            return self._value


# the jumper wires phase
class Wires(PhaseThread):
    def __init__(self, component, target, name="Wires"):
        super().__init__(name, component, target)
        # Identify which wires SHOULD be cut based on the binary target
        # e.g., if target is 5 (00101), sequence is [2, 4]
        self._target_sequence = [i for i in range(5) if (self._target & (1 << (4 - i)))]
        # Tracks our progress through the required sequence
        self._current_cut_index = 0 

    # runs the thread
    def run(self):
        self._running = True
        # Initial state: all wires connected (True)
        previous_state = [pin.value for pin in self._component] 
        
        while (self._running):
            # Read current physical state of wires
            current_state = [pin.value for pin in self._component]
            
            # Only process if a wire was just disconnected
            if (current_state != previous_state):
                for i in range(5):
                    # Check if THIS specific wire was just cut (True -> False transition)
                    if previous_state[i] and not current_state[i]:
                        
                        # Check if we have more wires left to cut in our sequence
                        if self._current_cut_index < len(self._target_sequence):
                            expected_wire = self._target_sequence[self._current_cut_index]
                            
                            if i == expected_wire:
                                # Correct wire cut in the correct order!
                                self._current_cut_index += 1
                                
                                # Check if the phase is now fully defused
                                if self._current_cut_index == len(self._target_sequence):
                                    self._defused = True
                            else:
                                # Wrong wire OR wrong order -> Strike!
                                self._failed = True
                        else:
                            # User cut an extra wire after already defusing/finishing sequence
                            self._failed = True
                
                # Update state to prepare for the next cut
                previous_state = current_state
                
            sleep(0.1)

    # returns the jumper wires state as a string for the Label UI
    def __str__(self):
        if (self._defused):
            return "DEFUSED"
        else:
            # Shows 1 for connected, 0 for cut (e.g., "11011")
            return "".join(["1" if pin.value else "0" for pin in self._component])
# the pushbutton phase
class Button(PhaseThread):
    def __init__(self, component_state, component_rgb, target, color, timer, name="Button"):
        super().__init__(name, component_state, target)
        # the default value is False/Released
        self._value = False
        # has the pushbutton been pressed?
        self._pressed = False
        # we need the pushbutton's RGB pins to set its color
        self._rgb = component_rgb
        # the pushbutton's randomly selected LED color
        self._color = color
        # we need to know about the timer (7-segment display) to be able to determine correct pushbutton releases in some cases
        self._timer = timer

    # runs the thread
    def run(self):
        self._running = True
        # set the RGB LED color
        self._rgb[0].value = False if self._color == "R" else True
        self._rgb[1].value = False if self._color == "G" else True
        self._rgb[2].value = False if self._color == "B" else True
        while (self._running):
            # get the pushbutton's state
            self._value = self._component.value
            # it is pressed
            if (self._value):
                # note it
                self._pressed = True
            # it is released
            else:
                # was it previously pressed?
                if (self._pressed):
                    # check the release parameters
                    # for R, nothing else is needed
                    # for G or B, a specific digit must be in the timer (sec) when released
                    if (not self._target or self._target in self._timer._sec):
                        self._defused = True
                    else:
                        self._failed = True
                    # note that the pushbutton was released
                    self._pressed = False
            sleep(0.1)

    # returns the pushbutton's state as a string
    def __str__(self):
        if (self._defused):
            return "DEFUSED"
        else:
            return str("Pressed" if self._value else "Released")

# the toggle switches phase
class Toggles(PhaseThread):
    def __init__(self, component, target, name="Toggles"):
        super().__init__(name, component, target)

    # runs the thread
    def run(self):
        self._running = True
        while (self._running):
            # Toggles act as a 4-bit binary number
            current_value = 0
            for i, pin in enumerate(self._component):
                if (pin.value):
                    # MSB is index 0
                    current_value |= (1 << (3 - i))
            
            self._value = current_value
            
            # The toggles phase is defused when the switches match the target decimal number
            if (self._value == self._target):
                self._defused = True
                
            sleep(0.1)

    # returns the toggle switches state as a string
    def __str__(self):
        if (self._defused):
            return "DEFUSED"
        else:
            return str(self._value)
        

# This is a test comment
# Second Test
