import threading
import time
from tkinter import Tk, Label, Frame

# --- 1. Base Class (From your Group Discussion) ---
class PhaseThread(threading.Thread):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self._running = False
        self._value = ""

# --- 2. Timer Class (With Pause/Reset Logic) ---
class Timer(PhaseThread):
    def __init__(self, seconds=300):
        super().__init__("Timer")
        self._value = seconds
        self._running = True
        self._paused = False

    def run(self):
        while self._running:
            if not self._paused:
                time.sleep(1)
                self._value -= 1
                if self._value <= 0:
                    self._running = False
            else:
                time.sleep(0.1) # Idle while paused

    def pause(self):
        self._paused = not self._paused

    def reset(self, new_value):
        self._value = new_value

# --- 3. Keypad Class (With 4-Char Limit) ---
class Keypad(PhaseThread):
    def __init__(self):
        super().__init__("Keypad")
        self._value = ""
        self._running = True
# --- UPDATE THESE PINS TO MATCH YOUR BOX ---
        self.ROWS = [18, 23, 24, 25] # Example GPIO pins
        self.COLS = [12, 16, 20, 21] # Example GPIO pins
        
        self.keys = [
            ['1','2','3'],
            ['4','5','6'],
            ['7','8','9'],
            ['*','0','#']
        ]

        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        for j in self.COLS:
            GPIO.setup(j, GPIO.OUT)
            GPIO.output(j, 1)
        for i in self.ROWS:
            GPIO.setup(i, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    def run(self):
        while self._running:
            # Simulate hardware read
            # pressed = hardware.get_key() 
            pass 

    def add_key(self, key):
        self._value += str(key)
        if len(self._value) > 4:
            self._value = self._value[-4:] # Keep last 4

    def clear(self):
        self._value = ""

# --- 4. Silver Button Class (The "Submit" Key) ---
class SilverButton(PhaseThread):
    def __init__(self):
        super().__init__("Button")
        self._pressed = False
        self._running = True

    def run(self):
        while self._running:
            # if hardware.read_pin(SILVER_BUTTON_PIN):
            #     self._pressed = True
            time.sleep(0.1)

    def was_clicked(self):
        if self._pressed:
            self._pressed = False # Consume the click
            return True
        return False

# --- 5. The GUI (Non-Touch Diagnostic HUD) ---
class BombGUI:
    def __init__(self, root, timer, keypad, button):
        self.root = root
        self.timer = timer
        self.keypad = keypad
        self.button = button
        
        root.title("DEFUSE TERMINAL v1.0")
        root.geometry("800x480") # Standard Adafruit Screen Size
        root.configure(bg="black")

        # UI Elements
        self.lbl_status = Label(root, text="AWAITING INPUT", fg="#39FF14", bg="black", font=("Courier", 30))
        self.lbl_status.pack(pady=20)

        self.lbl_keypad = Label(root, text="CODE: [ _ _ _ _ ]", fg="white", bg="black", font=("Courier", 40))
        self.lbl_keypad.pack(pady=40)

        self.lbl_timer = Label(root, text="00:00", fg="red", bg="black", font=("Courier", 20))
        self.lbl_timer.pack(side="bottom", pady=20)

        self.update_loop()

    def update_loop(self):
        # 1. Update Timer Display
        mins, secs = divmod(self.timer._value, 60)
        self.lbl_timer.config(text=f"T-MINUS: {mins:02d}:{secs:02d}")

        # 2. Update Keypad Buffer Display
        buffer = self.keypad._value.ljust(4, "_")
        display_code = " ".join(list(buffer))
        self.lbl_keypad.config(text=f"CODE: [ {display_code} ]")

        # 3. Check Silver
        Button for Submission
        if self.button.was_clicked():
            self.check_code()

        self.root.after(100, self.update_loop)

    def check_code(self):
        if self.keypad._value == "1234":
            self.lbl_status.config(text="BOMB DISARMED", fg="green")
            self.timer._running = False
        else:
            self.lbl_status.config(text="ACCESS DENIED", fg="red")
            self.keypad.clear()

# --- Execution ---
if __name__ == "__main__":
    # Initialize hardware threads
    t = Timer(300)
    k = Keypad()
    b = SilverButton()

    t.start()
    k.start()
    b.start()

    # Launch GUI
    root = Tk()
    app = BombGUI(root, t, k, b)
    root.mainloop()
    
