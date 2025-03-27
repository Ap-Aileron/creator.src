# Nice! You know how to decompile this! Nice. You probably did this because you're anxious it's a virus or you want to send me my own src code. You wont find anything malicious in it.
import keyboard
import time
import sys
from pynput import mouse
import random
import string
from threading import Event
import psutil
import json
import os

def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def load_config():
    config_path = get_resource_path('config.json')
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

def generate_random_characters(length=8):
    first_char = random.choice(string.ascii_letters)
    rest = ''.join(random.choices(string.ascii_letters + string.digits, k=length-1))
    return first_char + rest

def save_account_info(email, password, first_name, last_name):
    accounts_file = get_resource_path('accounts.json')
    accounts = []
    
    if os.path.exists(accounts_file):
        try:
            with open(accounts_file, 'r') as f:
                accounts = json.load(f)
        except json.JSONDecodeError:
            sys.stdout.write(f'Warning: Could not parse {accounts_file}, creating new file\n')
            sys.stdout.flush()
    
    account = {
        'email': f'{email}@outlook.com',
        'password': password,
        'first_name': first_name,
        'last_name': last_name
    }
    accounts.append(account)
    
    # Save updated accounts
    with open(accounts_file, 'w') as f:
        json.dump(accounts, f, indent=4)

def execute_keystrokes(file_path):
    account_info = {'email': '', 'password': '', 'first_name': '', 'last_name': ''}
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            i = 0
            while i < len(lines):
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
                            print(f'Waiting {wait_seconds} seconds after Windows key')
                            time.sleep(wait_seconds)
                        except ValueError:
                            print(f'Invalid wait time: {wait_time}, continuing...')
                elif 'randomCharacters' in key:
                    length = 8  
                    if ':' in key:
                        try:
                            length = int(key.split(':')[1].strip())
                        except ValueError:
                            pass
                    random_text = generate_random_characters(length)
                    keyboard.write(random_text)
                    print(f'Typed random characters: {random_text}')

                    if account_info['email'] == '':
                        account_info['email'] = random_text
                    elif account_info['password'] == '':
                        account_info['password'] = random_text
                    elif account_info['first_name'] == '':
                        account_info['first_name'] = random_text
                    elif account_info['last_name'] == '':
                        account_info['last_name'] = random_text
                        save_account_info(account_info['email'], account_info['password'],
                                        account_info['first_name'], account_info['last_name'])
                else:
                    keyboard.press_and_release(key)
                    print(f'Pressed {key}')
                
                if wait_time.lower() == 'click':
                    print('Please click your mouse when the loading screen has finished.')
                    click_event = Event()
                    def on_click(x, y, button, pressed):
                        if pressed:
                            click_event.set()
                            return False
                    with mouse.Listener(on_click=on_click) as listener:
                        click_event.wait()
                        listener.join()
                    print('Click detected, continuing...')
                elif wait_time:
                    try:
                        wait_seconds = float(wait_time)
                        print(f'Waiting {wait_seconds} seconds')
                        time.sleep(wait_seconds)
                    except ValueError:
                        print(f'Invalid wait time: {wait_time}, continuing...')
                
                i += 1 
    except FileNotFoundError:
        sys.stdout.write(f'Error: File {file_path} not found\n')
        sys.stdout.flush()
        sys.exit(1)
    except Exception as e:
        if 'is not a valid key' in str(e):
            print(f'Error: Unsupported key - {e}')
            sys.exit(1)
    except Exception as e:
        print(f'An error occurred: {e}')
        sys.exit(1)

def close_settings_app():
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'].lower() == 'systemsettings.exe':
                proc.terminate()
                proc.wait(timeout=3)
                sys.stdout.write('Settings app closed successfully\n')
                sys.stdout.flush()
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
            continue
    return False

def main():             
    config = load_config()
    strokes_file = get_resource_path('strokes.txt')
    sys.stdout.write(f'Executing keystrokes from {strokes_file}...\n')
    sys.stdout.flush()
    if config.get('closeSettingsOnStart', True) and close_settings_app():
        time.sleep(1)  
    
    if not config.get('instantStart', False):
        sys.stdout.write('Starting now.\n')
        sys.stdout.flush()     
    
    execute_keystrokes(strokes_file)
    sys.stdout.write('Finished executing keystrokes. Proceed with CAPTCHA or other actions.\n')
    sys.stdout.flush()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.stdout.write('\nProgram interrupted by user\n')
        sys.stdout.flush()