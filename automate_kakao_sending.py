import tkinter as tk
from tkinter import scrolledtext
from threading import Thread, Event
import pyautogui
import time
import pyperclip
import gspread
import random

from pynput.keyboard import Key, Controller

class MacKakaoClicker:
    def __init__(self):
        self.keyboard = Controller()
        self.gc = gspread.service_account(filename="/Applications/mac_kakao_json_key_file.json")
        self.bible_spreadsheet = self.gc.open_by_key('1Feik07nL_R6RFmnnZcp3w5gRFGQKyXFjLs_7yQNAKEQ')
        self.bible_worksheet = self.bible_spreadsheet.get_worksheet_by_id(0)
        self.friends_worksheet = self.bible_spreadsheet.get_worksheet_by_id(1300541554)
        self.bible_data = self.bible_worksheet.get_all_records()
        self.friends_data = self.friends_worksheet.get_all_records()
        self.counter = 1

    def get_friends_list(self): 
        """ 
        `bible_friends` 워크시트에서 `친구` column에서 전체적인 친구 리스트를 들고오는 함수 
        """ 
        friends = [f['친구'] for f in self.friends_data if f['친구'] != '']
        return friends

    def get_random_text_from_bible_sheets(self):
        """ 
        `bible_texts` 워크시트의 `말씀` column에서 랜덤하게 말씀을 들고오는 함수  
        """
        selected_bible_words = random.choice([d for d in self.bible_data if d['한글말씀'] != ''])['한글말씀']
        return selected_bible_words


    def find_image_and_click(self, img_name, delta_x, delta_y):
        """
        해당 카카오톡에 있는 이미지 아이콘을 찾고 클릭하는 함수, 
        잘 못 찾으면, error을 뱉는 함수 
        """
        try:
            # Locate the image on the screen
            img_icon = f'/Users/sty8470/Desktop/auto_kakao_messages/img/{img_name}.png'
            x, y = pyautogui.locateCenterOnScreen(img_icon, grayscale=True, confidence=0.7)  # Adjust confidence as needed
            if x and y:
                # Find the center of the found image
                time.sleep(1)
                delta_x = delta_x if delta_x is not None else 0
                delta_y = delta_y if delta_y is not None else 0
                pyautogui.click((x+delta_x)//2, (y+delta_y)//2)
                print(f"Clicked on {img_name}")
            else:
                print(f"Image not found: {img_name}")
        except Exception as e:
            print(f"An error occurred: {e}")
    
    def search_friend_room(self, friend):
        """
        카카오톡의 검색창에 특정 flag을 보내는 함수 
        """
        # 단축키 cmd + k로 한번 다시 커서를 입히는 과정 
        # Command + V를 눌러 붙여넣기
        with self.keyboard.pressed(Key.cmd):
            self.keyboard.press('f')
            self.keyboard.release('f')
        
        time.sleep(0.3)  # 붙여넣기 후 잠시 기다립니다

        time.sleep(0.3)
        pyperclip.copy(friend)
        time.sleep(1.5)  # 클립보드에 메시지가 복사되는 데 충분한 시간을 제공

        # Command + V를 눌러 붙여넣기
        with self.keyboard.pressed(Key.cmd):
            self.keyboard.press('v')
            self.keyboard.release('v')
        
        time.sleep(0.3)  # 붙여넣기 후 잠시 기다립니다

    def enter_friend_room(self):
        """
        카카오톡의 검색창에 특정 flag 입력 이후에, 첫 번째 사람에게 access하기 위해서, 지나치게 하는 메소드 
        """
        pyautogui.keyDown('down')
        time.sleep(0.5)
        pyautogui.keyDown('down')
        time.sleep(0.5)
        pyautogui.keyDown('enter')
        time.sleep(0.5)
    
    def copy_and_paste_verse(self, text):
        """ 
        카카오톡에 메세지를 보낼 부분을 특별히 복사하고 붙여넣는 메소드
        """
        pyperclip.copy(text)
        time.sleep(1.5)  # 클립보드에 메시지가 복사되는 데 충분한 시간을 제공

        # Command + V를 눌러 붙여넣기
        with self.keyboard.pressed(Key.cmd):
            self.keyboard.press('v')
            self.keyboard.release('v')
        
        time.sleep(0.3)  # 붙여넣기 후 잠시 기다립니다

        # Enter 키를 눌러 메시지 전송
        self.keyboard.press(Key.enter)
        self.keyboard.release(Key.enter)
    
    def exit_friend_room(self):
        """ 
        카카오톡방에서 종료하고 나오는 메소드 
        """
        time.sleep(0.3)
        pyautogui.keyDown('esc')
        time.sleep(0.3)
    
    def click_group_chat_icon(self):
        """ 
        그룹챗 아이콘을 cmd + 2의 단축키를 눌러서 클릭한다.
        """
        time.sleep(0.3)
        # Command + V를 눌러 붙여넣기
        with self.keyboard.pressed(Key.cmd):
            self.keyboard.press('2')
            self.keyboard.release('2')
        
        time.sleep(0.3)  # 붙여넣기 후 잠시 기다립니다

        # Enter 키를 눌러 메시지 전송
        self.keyboard.press(Key.enter)
        self.keyboard.release(Key.enter) 

    def run(self, stop_event, log_callback):
        try:
            friends = self.get_friends_list()
            self.find_image_and_click(img_name="person_icon", delta_x=None, delta_y=None)
            self.click_group_chat_icon()
            self.find_image_and_click(img_name="search_icon", delta_x=None, delta_y=None)

            for i, friend in enumerate(friends):
                if stop_event.is_set():
                    log_callback("Clicker stopped by user.")
                    break
                text = self.get_random_text_from_bible_sheets()
                self.search_friend_room(friend)
                self.enter_friend_room()
                self.copy_and_paste_verse(text)
                self.exit_friend_room()
                log_callback(f"Message sent to: {friend} - {self.counter}")
                self.counter += 1

            self.find_image_and_click(img_name="search_icon", delta_x=None, delta_y=None)
            self.find_image_and_click(img_name="person_icon", delta_x=None, delta_y=None)

            log_callback("Kakao Clicker process completed.")
        except Exception as e:
            log_callback(f"An error occurred: {e}")

class MacKakaoClickerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Mac Kakao Clicker")
        
        # Define the main components
        self.start_button = tk.Button(root, text="Start", command=self.start_clicker, width=10)
        self.start_button.grid(row=0, column=0, padx=10, pady=10)
        
        self.stop_button = tk.Button(root, text="Stop", command=self.stop_clicker, width=10, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=10, pady=10)
        
        self.log_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=20)
        self.log_area.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
        
        # Initialize the clicker and thread management
        self.clicker = MacKakaoClicker()
        self.thread = None
        self.stop_event = Event()

    def log(self, message):
        """Add a message to the log area."""
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)

    def start_clicker(self):
        """Start the clicker process in a separate thread."""
        self.log("Starting Kakao Clicker...")
        self.stop_event.clear()
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        self.thread = Thread(target=self.run_clicker)
        self.thread.start()

    def stop_clicker(self):
        """Stop the clicker process."""
        self.log("Stopping Kakao Clicker...")
        self.stop_event.set()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def run_clicker(self):
        """Run the clicker process and check for stop events."""
        self.clicker.run(self.stop_event, self.log)

if __name__ == "__main__":
    root = tk.Tk()
    app = MacKakaoClickerGUI(root)
    root.mainloop()