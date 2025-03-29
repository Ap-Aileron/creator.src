import customtkinter as ctk
import keyboard
import time
import sys
from pynput import mouse
import random
import string
from threading import Event, Thread
import psutil
import json
import os
from colorama import init, Fore, Style

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AccountGeneratorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window setup
        self.title("Account Generator")
        self.geometry("800x600")

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Title
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="Account Generator",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.grid(row=0, column=0, pady=(20, 30))

        # Settings Frame
        self.settings_frame = ctk.CTkFrame(self.main_frame)
        self.settings_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")

        # Settings
        self.instant_start_var = ctk.BooleanVar()
        self.instant_start_checkbox = ctk.CTkCheckBox(
            self.settings_frame,
            text="Instant Start",
            variable=self.instant_start_var
        )
        self.instant_start_checkbox.grid(row=0, column=0, padx=20, pady=10)

        self.close_settings_var = ctk.BooleanVar(value=True)
        self.close_settings_checkbox = ctk.CTkCheckBox(
            self.settings_frame,
            text="Close Settings on Start",
            variable=self.close_settings_var
        )
        self.close_settings_checkbox.grid(row=0, column=1, padx=20, pady=10)

        # Status Display
        self.status_text = ctk.CTkTextbox(
            self.main_frame,
            height=200,
            wrap="word"
        )
        self.status_text.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")

        # Account List
        self.account_list = ctk.CTkTextbox(
            self.main_frame,
            height=150,
            wrap="none"
        )
        self.account_list.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")

        # Buttons Frame
        self.button_frame = ctk.CTkFrame(self.main_frame)
        self.button_frame.grid(row=4, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.button_frame.grid_columnconfigure((0, 1), weight=1)

        # Start Button
        self.start_button = ctk.CTkButton(
            self.button_frame,
            text="Start Generation",
            command=self.start_generation
        )
        self.start_button.grid(row=0, column=0, padx=10, pady=10)

        # Stop Button
        self.stop_button = ctk.CTkButton(
            self.button_frame,
            text="Stop",
            command=self.stop_generation,
            state="disabled",
            fg_color="#DB4437",
            hover_color="#B33225"
        )
        self.stop_button.grid(row=0, column=1, padx=10, pady=10)

        self.is_running = False
        self.load_config()
        self.load_accounts()

    def load_config(self):
        config = self.get_config()
        self.instant_start_var.set(config.get("instantStart", False))
        self.close_settings_var.set(config.get("closeSettingsOnStart", True))

    def get_config(self):
        config_path = self.get_resource_path('config.json')
        default_config = {
            "instantStart": False,
            "defaultWaitTime": 0.1,
            "closeSettingsOnStart": True
        }
        
        if not os.path.exists(config_path):
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=4)
            return default_config
        
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except:
            return default_config

    def get_resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def load_accounts(self):
        accounts_file = self.get_resource_path('accounts.json')
        if os.path.exists(accounts_file):
            try:
                with open(accounts_file, 'r') as f:
                    accounts = json.load(f)
                    self.update_account_list(accounts)
            except json.JSONDecodeError:
                self.log_message("Warning: Could not parse accounts.json", "yellow")

    def update_account_list(self, accounts):
        self.account_list.delete("1.0", "end")
        if not accounts:
            self.account_list.insert("1.0", "No accounts generated yet")
            return

        header = "Email | Password | First Name | Last Name\n" + "-" * 50 + "\n"
        self.account_list.insert("1.0", header)
        
        for account in accounts:
            account_str = f"{account['email']} | {account['password']} | {account['first_name']} | {account['last_name']}\n"
            self.account_list.insert("end", account_str)

    def log_message(self, message, color="white"):
        color_map = {
            "white": "#FFFFFF",
            "green": "#4CAF50",
            "yellow": "#FFC107",
            "red": "#F44336",
            "cyan": "#00BCD4"
        }
        
        self.status_text.insert("end", message + "\n")
        self.status_text.see("end")
        self.update()

    def start_generation(self):
        if self.is_running:
            return

        self.is_running = True
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        
        self.generation_thread = Thread(target=self.generation_process)
        self.generation_thread.start()

    def stop_generation(self):
        self.is_running = False
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")

    def generation_process(self):
        while self.is_running:
            try:
                if self.close_settings_var.get():
                    self.close_settings_app()
                    time.sleep(1)

                if not self.instant_start_var.get():
                    self.log_message("Starting now.", "green")

                self.execute_keystrokes(self.get_resource_path('strokes.txt'))
                
                if not self.is_running:
                    break

                self.log_message("Account Created. Starting next account in 3 seconds...", "green")
                time.sleep(3)

            except Exception as e:
                self.log_message(f"Error: {str(e)}", "red")
                break

        self.stop_generation()

    def close_settings_app(self):
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'].lower() == 'systemsettings.exe':
                    proc.terminate()
                    proc.wait(timeout=3)
                    self.log_message("Settings app closed successfully", "green")
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                continue
        return False

    def generate_random_characters(self, length=8):
        first_char = random.choice(string.ascii_letters)
        rest = ''.join(random.choices(string.ascii_letters + string.digits, k=length-1))
        return first_char + rest

    def save_account_info(self, email, password, first_name, last_name):
        accounts_file = self.get_resource_path('accounts.json')
        accounts = []
        
        if os.path.exists(accounts_file):
            try:
                with open(accounts_file, 'r') as f:
                    accounts = json.load(f)
            except json.JSONDecodeError:
                self.log_message("Warning: Could not parse accounts.json", "yellow")
        
        account = {
            'email': f'{email}@outlook.com',
            'password': password,
            'first_name': first_name,
            'last_name': last_name
        }
        accounts.append(account)
        
        with open(accounts_file, 'w') as f:
            json.dump(accounts, f, indent=4)
        
        self.update_account_list(accounts)

    def execute_keystrokes(self, file_path):
        account_info = {'email': '', 'password': '', 'first_name': '', 'last_name': ''}
        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()
                i = 0
                while i < len(lines) and self.is_running:
                    line = lines[i].strip()
                    if not line:  
                        i += 1
                        continue
                    
                    if line.startswith('###'):
                        i += 1
                        continue
                    
                    if not line.startswith('Key pressed: '):
                        i += 1
                        continue
                    
                    wait_time = '0'
                    key_parts = line.split('Wait:')
                    if len(key_parts) > 1:
                        key_line = key_parts[0].strip()
                        wait_time = key_parts[1].strip()
                    else:
                        next_line = lines[i + 1].strip() if i + 1 < len(lines) else ''
                        if next_line.startswith('Wait:'):
                            wait_time = next_line.replace('Wait:', '').strip()
                            i += 1  
                        key_line = line
                    
                    key = key_line.replace('Key pressed: ', '').strip()
                        
                    if key == 'windows':
                        keyboard.press('win')
                        time.sleep(0.1)
                        keyboard.release('win')
                        if wait_time:
                            try:
                                wait_seconds = float(wait_time)
                                self.log_message(f"Waiting {wait_seconds} seconds after Windows key", "cyan")
                                time.sleep(wait_seconds)
                            except ValueError:
                                self.log_message(f"Invalid wait time: {wait_time}, continuing...", "yellow")
                    elif 'randomCharacters' in key:
                        length = 8  
                        if ':' in key:
                            try:
                                length = int(key.split(':')[1].strip())
                            except ValueError:
                                pass
                        random_text = self.generate_random_characters(length)
                        keyboard.write(random_text)
                        self.log_message(f"Typed random characters: {random_text}", "green")

                        if account_info['email'] == '':
                            account_info['email'] = random_text
                        elif account_info['password'] == '':
                            account_info['password'] = random_text
                        elif account_info['first_name'] == '':
                            account_info['first_name'] = random_text
                        elif account_info['last_name'] == '':
                            account_info['last_name'] = random_text
                            self.save_account_info(account_info['email'], account_info['password'],
                                            account_info['first_name'], account_info['last_name'])
                    else:
                        keyboard.press_and_release(key)
                        self.log_message(f"Pressed {key}", "cyan")
                    
                    if wait_time.lower() == 'click':
                        self.log_message("Please click your mouse when the loading screen has finished.", "yellow")
                        click_event = Event()
                        def on_click(x, y, button, pressed):
                            if pressed:
                                click_event.set()
                                return False
                        with mouse.Listener(on_click=on_click) as listener:
                            click_event.wait()
                            listener.join()
                        self.log_message("Click detected, continuing...", "green")
                    elif wait_time:
                        try:
                            wait_seconds = float(wait_time)
                            self.log_message(f"Waiting {wait_seconds} seconds", "cyan")
                            time.sleep(wait_seconds)
                        except ValueError:
                            self.log_message(f"Invalid wait time: {wait_time}, continuing...", "yellow")
                    
                    i += 1 
        except FileNotFoundError:
            self.log_message(f"Error: File {file_path} not found", "red")
            self.stop_generation()
        except Exception as e:
            if 'is not a valid key' in str(e):
                self.log_message(f"Error: Unsupported key - {e}", "red")
            else:
                self.log_message(f"An error occurred: {e}", "red")
            self.stop_generation()

if __name__ == '__main__':
    app = AccountGeneratorApp()
    app.mainloop()