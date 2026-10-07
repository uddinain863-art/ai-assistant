import threading
import webbrowser
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.utils import platform

if platform == 'android':
    from jnius import autoclass
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Intent = autoclass('android.content.Intent')
    Uri = autoclass('android.net.Uri')
    Settings = autoclass('android.provider.Settings')

class MustaraAssistant(App):
    def build(self):
        self.title = "Mustara AI Assistant"
        
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        self.scroll = ScrollView(size_hint=(1, 0.82), do_scroll_x=False)
        self.chat_display = Label(
            text="[Mustara]: Hello! I am your AI Assistant. How can I help you?\nCommands: time, date, youtube, google, whatsapp, settings, weather\n",
            markup=True,
            size_hint_y=None,
            valign='top',
            halign='left',
            color=(0.9, 0.9, 0.9, 1)
        )
        self.chat_display.bind(
            width=lambda *x: setattr(self.chat_display, 'text_size', (self.chat_display.width, None)),
            texture_size=lambda *x: setattr(self.chat_display, 'height', self.chat_display.texture_size[1])
        )
        self.scroll.add_widget(self.chat_display)
        main_layout.add_widget(self.scroll)
        
        input_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.12), spacing=8)
        self.user_input = TextInput(
            hint_text="Type command here...",
            multiline=False,
            size_hint_x=0.75,
            padding=[10, 12, 10, 10],
            background_color=(0.2, 0.2, 0.25, 1),
            foreground_color=(1, 1, 1, 1)
        )
        self.user_input.bind(on_text_validate=self.process_command)
        
        send_btn = Button(
            text="Send",
            size_hint_x=0.25,
            background_color=(0.1, 0.6, 0.9, 1)
        )
        send_btn.bind(on_press=self.process_command)
        
        input_layout.add_widget(self.user_input)
        input_layout.add_widget(send_btn)
        main_layout.add_widget(input_layout)
        
        return main_layout

    def open_android_url(self, url):
        try:
            if platform == 'android':
                current_activity = PythonActivity.mActivity
                intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
                current_activity.startActivity(intent)
            else:
                webbrowser.open(url)
        except Exception as e:
            self.append_message(f"[Mustara]: Error opening URL: {e}")

    def open_android_settings(self):
        try:
            if platform == 'android':
                current_activity = PythonActivity.mActivity
                intent = Intent(Settings.ACTION_SETTINGS)
                current_activity.startActivity(intent)
            else:
                self.append_message("[Mustara]: Settings is only available on Android.")
        except Exception as e:
            self.append_message(f"[Mustara]: Error opening settings: {e}")

    def open_whatsapp(self):
        try:
            if platform == 'android':
                current_activity = PythonActivity.mActivity
                pm = current_activity.getPackageManager()
                intent = pm.getLaunchIntentForPackage("com.whatsapp")
                if intent:
                    current_activity.startActivity(intent)
                else:
                    self.open_android_url("https://wa.me/")
            else:
                webbrowser.open("https://web.whatsapp.com")
        except Exception as e:
            self.append_message(f"[Mustara]: Error opening WhatsApp: {e}")

    def append_message(self, message):
        self.chat_display.text += f"\n{message}\n"
        Clock.schedule_once(lambda dt: setattr(self.scroll, 'scroll_y', 0))

    def process_command(self, instance):
        query = self.user_input.text.strip()
        if not query:
            return
        
        self.append_message(f"[You]: {query}")
        self.user_input.text = ""
        threading.Thread(target=self.handle_logic, args=(query,)).start()

    def handle_logic(self, query):
        q = query.lower()
        
        if "time" in q:
            now = datetime.now().strftime("%I:%M %p")
            reply = f"[Mustara]: Current time is {now}."
            Clock.schedule_once(lambda dt: self.append_message(reply))
            
        elif "date" in q:
            today = datetime.now().strftime("%d %B %Y")
            reply = f"[Mustara]: Today's date is {today}."
            Clock.schedule_once(lambda dt: self.append_message(reply))
            
        elif "whatsapp" in q:
            reply = "[Mustara]: Opening WhatsApp..."
            Clock.schedule_once(lambda dt: self.append_message(reply))
            Clock.schedule_once(lambda dt: self.open_whatsapp())

        elif "setting" in q:
            reply = "[Mustara]: Opening Android Settings..."
            Clock.schedule_once(lambda dt: self.append_message(reply))
            Clock.schedule_once(lambda dt: self.open_android_settings())

        elif "youtube" in q:
            search_term = q.replace("youtube", "").strip()
            if search_term:
                url = f"https://www.youtube.com/results?search_query={search_term}"
                reply = f"[Mustara]: Searching YouTube for '{search_term}'..."
            else:
                url = "https://www.youtube.com"
                reply = "[Mustara]: Opening YouTube..."
            Clock.schedule_once(lambda dt: self.append_message(reply))
            Clock.schedule_once(lambda dt: self.open_android_url(url))

        elif "google" in q or "search" in q:
            search_term = q.replace("google", "").replace("search", "").strip()
            url = f"https://www.google.com/search?q={search_term}"
            reply = f"[Mustara]: Searching Google for '{search_term}'..."
            Clock.schedule_once(lambda dt: self.append_message(reply))
            Clock.schedule_once(lambda dt: self.open_android_url(url))

        elif "weather" in q:
            url = "https://www.google.com/search?q=weather+today"
            reply = "[Mustara]: Checking today's weather..."
            Clock.schedule_once(lambda dt: self.append_message(reply))
            Clock.schedule_once(lambda dt: self.open_android_url(url))

        else:
            reply = f"[Mustara]: Command recognized: '{query}'. Try 'youtube', 'whatsapp', 'settings', or 'time'."
            Clock.schedule_once(lambda dt: self.append_message(reply))

if __name__ == '__main__':
    MustaraAssistant().run()
