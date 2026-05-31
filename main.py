
import kivy
kivy.require('2.1.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.utils import platform
from kivy.uix.screenmanager import ScreenManager, Screen

import threading
import queue
import json
import os


# ---------------------------
# ABOUT + DEVELOPERS POPUP
# ---------------------------
class AboutPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.title = "About Application"
        self.size_hint = (0.9, 0.9)

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        scroll = ScrollView()

        content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)
        content.bind(minimum_height=content.setter('height'))

        content.add_widget(Label(
            text="🌐 OFFLINE LANGUAGE TRANSLATOR\n"
                 "Final Year Project\n\n"
                 "Features:\n"
                 "✔ Offline text translation (demo engine)\n"
                 "✔ Simple UI optimized for Android\n"
                 "✔ Speech-ready architecture\n"
                 "✔ Lightweight Kivy application\n",
            size_hint_y=None,
            height=200
        ))

        content.add_widget(Label(
            text="🛠 TECHNOLOGY STACK\n"
                 "- Python 3\n"
                 "- Kivy 2.1\n"
                 "- Buildozer (Android)\n"
                 "- JSON-based translation engine\n",
            size_hint_y=None,
            height=150
        ))

        content.add_widget(Label(
            text="👨‍💻 DEVELOPERS\n\n"
                 "Lead Developer:\n"
                 "Your Name Here\n\n"
                 "Supervisor:\n"
                 "Lecturer Name\n\n"
                 "Institution:\n"
                 "Your University",
            size_hint_y=None,
            height=200
        ))

        scroll.add_widget(content)
        layout.add_widget(scroll)

        btn = Button(text="Close", size_hint_y=None, height=50)
        btn.bind(on_press=self.dismiss)
        layout.add_widget(btn)

        self.content = layout


# ---------------------------
# MAIN APPLICATION SCREEN
# ---------------------------
class TranslatorScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        main = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # HEADER
        header = BoxLayout(size_hint_y=None, height=50)

        title = Label(text="🌐 Offline Translator", bold=True)

        about_btn = Button(text="About", size_hint_x=None, width=100)
        about_btn.bind(on_press=self.show_about)

        header.add_widget(title)
        header.add_widget(about_btn)
        main.add_widget(header)

        # INPUT
        self.input_text = TextInput(
            hint_text="Enter text...",
            size_hint_y=0.3
        )
        main.add_widget(self.input_text)

        # OUTPUT
        self.output = Label(
            text="Translation will appear here",
            size_hint_y=0.3
        )
        main.add_widget(self.output)

        # BUTTONS
        btns = BoxLayout(size_hint_y=None, height=60, spacing=10)

        translate_btn = Button(text="Translate")
        translate_btn.bind(on_press=self.translate)

        clear_btn = Button(text="Clear")
        clear_btn.bind(on_press=self.clear)

        btns.add_widget(translate_btn)
        btns.add_widget(clear_btn)

        main.add_widget(btns)

        self.add_widget(main)

    def show_about(self, instance):
        AboutPopup().open()

    def translate(self, instance):
        text = self.input_text.text.strip()

        if not text:
            self.output.text = "Enter text first"
            return

        # SIMPLE OFFLINE TRANSLATION MAP (FINAL YEAR SAFE)
        translations = {
            "hello": "hola",
            "how are you": "cómo estás",
            "good morning": "buenos días",
            "thank you": "gracias",
            "welcome": "bienvenido"
        }

        result = translations.get(text.lower(), f"[ES] {text}")
        self.output.text = result

    def clear(self, instance):
        self.input_text.text = ""
        self.output.text = ""


# ---------------------------
# APP CLASS
# ---------------------------
class TranslatorApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(TranslatorScreen(name="main"))
        return sm


if __name__ == "__main__":
    TranslatorApp().run()

