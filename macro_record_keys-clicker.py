import tkinter as tk
import threading
import time
import ctypes
from pynput import mouse, keyboard

try:
    # Tell Windows that this program is DPI Aware
    ctypes.windll.shcore.SetProcessDpiAwareness(2) 
except AttributeError:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

class PlaybackMacro:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Macro (Record & Playback)")
        self.root.geometry("400x280")
        self.root.attributes("-topmost", True)
        self.root.resizable(False, False)

        self.events = [] 
        self.is_recording = False
        self.is_playing = False
        self.start_time = 0

        self.mouse_ctrl = mouse.Controller()
        self.kb_ctrl = keyboard.Controller()

        self.mouse_listener = None
        self.kb_listener = None

        # GUI
        tk.Label(self.root, text="Macro Recorder", font=("Arial", 10, "bold"), fg="darkblue").pack(pady=10)
        
        self.record_mode = tk.IntVar(value=0)
        mode_frame = tk.Frame(self.root)
        mode_frame.pack(pady=5)
        tk.Radiobutton(mode_frame, text="Mouse + Keyboard", variable=self.record_mode, value=0).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(mode_frame, text="Mouse Only", variable=self.record_mode, value=1).pack(side=tk.LEFT, padx=5)

        self.status_label = tk.Label(self.root, text="Status: Ready", fg="gray", font=("Arial", 10))
        self.status_label.pack(pady=10)

        self.info_label = tk.Label(self.root, text="F8 = Record | F9 = Stop | F10 = Play", fg="black")
        self.info_label.pack(pady=5)

        self.count_label = tk.Label(self.root, text="Recorded Events: 0", fg="blue")
        self.count_label.pack(pady=5)

        # Hotkey listener runs separately to always listen for F8, F9, F10
        self.hotkey_listener = keyboard.Listener(on_press=self.on_hotkey)
        self.hotkey_listener.start()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_hotkey(self, key):
        if key == keyboard.Key.f8 and not self.is_recording and not self.is_playing:
            self.start_recording()
        elif key == keyboard.Key.f9:
            if self.is_recording:
                self.stop_recording()
            elif self.is_playing:
                self.stop_playing()
        elif key == keyboard.Key.f10 and not self.is_recording and not self.is_playing:
            self.start_playing()

    def start_recording(self):
        self.events.clear()
        self.is_recording = True
        self.start_time = time.perf_counter() 
        self.update_status("Recording...", "red")

        # Always record mouse
        self.mouse_listener = mouse.Listener(on_move=self.on_mouse_move, on_click=self.on_mouse_click)
        self.mouse_listener.start()

        if self.record_mode.get() == 0:
            self.kb_listener = keyboard.Listener(on_press=self.on_key_press, on_release=self.on_key_release)
            self.kb_listener.start()
        else:
            self.kb_listener = None

    def stop_recording(self):
        self.is_recording = False
        if self.mouse_listener: self.mouse_listener.stop()
        if self.kb_listener: self.kb_listener.stop()
        self.update_status("Recording Stopped", "gray")
        self.count_label.config(text=f"Recorded Events: {len(self.events)}")

    def on_mouse_move(self, x, y):
        self.events.append(('move', x, y, time.perf_counter() - self.start_time))

    def on_mouse_click(self, x, y, button, pressed):
        self.events.append(('click', x, y, button, pressed, time.perf_counter() - self.start_time))

    def on_key_press(self, key):
        if key in [keyboard.Key.f8, keyboard.Key.f9, keyboard.Key.f10]: return
        self.events.append(('press', key, time.perf_counter() - self.start_time))

    def on_key_release(self, key):
        if key in [keyboard.Key.f8, keyboard.Key.f9, keyboard.Key.f10]: return
        self.events.append(('release', key, time.perf_counter() - self.start_time))

    def start_playing(self):
        if not self.events: return
        self.is_playing = True
        self.update_status("Playing...", "green")
        threading.Thread(target=self.playback_loop, daemon=True).start()

    def stop_playing(self):
        self.is_playing = False
        self.update_status("Playback Stopped", "gray")
        
    def _move_mouse_hardware(self, x, y):
        # Use Windows API to move the mouse cursor with high precision
        user32 = ctypes.windll.user32
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)
        normalized_x = int(x * 65535 / screen_width)
        normalized_y = int(y * 65535 / screen_height)
        user32.mouse_event(0x0001 | 0x8000, normalized_x, normalized_y, 0, 0)
        

    def playback_loop(self):
        while self.is_playing:
            playback_start_time = time.perf_counter()

            for event in self.events:
                if not self.is_playing: 
                    break 

                target_time = playback_start_time + event[-1]
                
                # Precision Delay
                while True:
                    now = time.perf_counter()
                    if now >= target_time:
                        break 
                    
                    if target_time - now > 0.005:
                        time.sleep(0.001)

                action = event[0]
                try:
                    if action == 'move':
                        x, y = event[1], event[2]
                        self._move_mouse_hardware(x, y)
                    elif action == 'click':
                        x, y, button, pressed = event[1], event[2], event[3], event[4]
                        self._move_mouse_hardware(x, y)
                        if pressed:
                            self.mouse_ctrl.press(button)
                        else:
                            self.mouse_ctrl.release(button)
                    elif action == 'press':
                        key = event[1]
                        self.kb_ctrl.press(key)
                    elif action == 'release':
                        key = event[1]
                        self.kb_ctrl.release(key)
                except Exception:
                    pass 

        self.root.after(0, lambda: self.update_status("Playback Stopped", "gray"))

    def update_status(self, text, color):
        self.status_label.config(text=f"Status: {text}", fg=color)

    def on_closing(self):
        self.stop_recording()
        self.stop_playing()
        self.hotkey_listener.stop()
        self.root.destroy()

if __name__ == "__main__":
    app = PlaybackMacro()