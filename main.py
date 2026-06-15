import kivy
kivy.require('2.1.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.core.clipboard import Clipboard
from kivy.graphics import Color, RoundedRectangle, Line, Ellipse
from kivy.utils import get_color_from_hex, platform
from kivy.clock import mainthread
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.widget import Widget

import json
import os
import re

# -----------------------------------------------------------------------------
# NATIVE ANDROID SPEECH WRAPPER SETUP
# -----------------------------------------------------------------------------
is_android = platform == 'android'

if is_android:
    try:
        from jnius import autoclass
        from android import activity
        
        Intent = autoclass('android.content.Intent')
        RecognizerIntent = autoclass('android.speech.RecognizerIntent')
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        TextToSpeech = autoclass('android.speech.tts.TextToSpeech')
        Locale = autoclass('java.util.Locale')
    except Exception as e:
        print(f"JNI Speech Import Error: {e}")
        is_android = False

# -----------------------------------------------------------------------------
# CUSTOM STYLED WIDGETS FOR PREMIUM DARK SLATE & INDIGO UI
# -----------------------------------------------------------------------------

class RoundedButton(Button):
    def __init__(self, bg_color_hex="#6366F1", radius=8, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)
        self.color = (1, 1, 1, 1)  # White text
        self.bold = True
        self.font_size = '15sp'
        self.radius = dp(radius)
        
        self.bg_color = get_color_from_hex(bg_color_hex)
        # Calculate pressed color (darker version of the button color)
        self.pressed_color = [c * 0.8 for c in self.bg_color[:3]] + [self.bg_color[3]]
        
        with self.canvas.before:
            self.paint_color = Color(*self.bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
            
        self.bind(pos=self.update_rect, size=self.update_rect)
        
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        
    def on_state(self, instance, value):
        if value == 'down':
            self.paint_color.rgba = self.pressed_color
        else:
            self.paint_color.rgba = self.bg_color


def check_icon(filename):
    base_dir = os.path.dirname(__file__)
    path = os.path.join(base_dir, "data", filename)
    if os.path.exists(path):
        return path
    if os.path.exists(os.path.join("data", filename)):
        return os.path.join("data", filename)
    return None


class ClockIconWidget(Widget):
    def __init__(self, size_hint=(None, None), size=(dp(20), dp(20)), **kwargs):
        super().__init__(**kwargs)
        self.size_hint = size_hint
        self.size = size
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(1, 1, 1, 1)
            Line(ellipse=(self.x + dp(2), self.y + dp(2), self.width - dp(4), self.height - dp(4)), width=dp(1.5))
            Line(points=[self.x + self.width/2, self.y + self.height/2, self.x + self.width/2, self.y + self.height/2 + dp(6)], width=dp(1.5))
            Line(points=[self.x + self.width/2, self.y + self.height/2, self.x + self.width/2 + dp(4), self.y + self.height/2], width=dp(1.5))


class InfoIconWidget(Widget):
    def __init__(self, size_hint=(None, None), size=(dp(20), dp(20)), **kwargs):
        super().__init__(**kwargs)
        self.size_hint = size_hint
        self.size = size
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(1, 1, 1, 1)
            Line(ellipse=(self.x + dp(2), self.y + dp(2), self.width - dp(4), self.height - dp(4)), width=dp(1.5))
            Ellipse(pos=(self.x + self.width/2 - dp(1.5), self.y + self.height/2 + dp(3)), size=(dp(3), dp(3)))
            Line(points=[self.x + self.width/2, self.y + self.height/2 + dp(1), self.x + self.width/2, self.y + self.height/2 - dp(4)], width=dp(1.5))


class RoundedIconButton(ButtonBehavior, BoxLayout):
    def __init__(self, text="", icon_source=None, bg_color_hex="#6366F1", radius=8, icon_size=dp(20), font_size='15sp', text_color_hex="#FFFFFF", **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.padding = [dp(12), dp(8)]
        self.spacing = dp(8)
        self.radius = dp(radius)
        
        self.bg_color = get_color_from_hex(bg_color_hex)
        self.pressed_color = [c * 0.8 for c in self.bg_color[:3]] + [self.bg_color[3]]
        
        with self.canvas.before:
            self.paint_color = Color(*self.bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
            
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        if icon_source:
            if icon_source == "history.png":
                self.icon_widget = ClockIconWidget(size=(icon_size, icon_size), pos_hint={'center_y': 0.5})
                self.add_widget(self.icon_widget)
            elif icon_source == "about.png":
                self.icon_widget = InfoIconWidget(size=(icon_size, icon_size), pos_hint={'center_y': 0.5})
                self.add_widget(self.icon_widget)
            else:
                icon_path = check_icon(icon_source)
                if icon_path:
                    self.icon_widget = Image(source=icon_path, size_hint=(None, None), size=(icon_size, icon_size), pos_hint={'center_y': 0.5})
                    self.add_widget(self.icon_widget)
            
        if text:
            self.label = Label(text=text, bold=True, color=get_color_from_hex(text_color_hex), font_size=font_size, size_hint_x=1, halign='center', valign='middle')
            self.label.bind(size=self.label.setter('text_size'))
            self.add_widget(self.label)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        
    def on_state(self, instance, value):
        if value == 'down':
            self.paint_color.rgba = self.pressed_color
        else:
            self.paint_color.rgba = self.bg_color


class RoundedTextInput(TextInput):
    def __init__(self, bg_color_hex="#1E293B", border_color_hex="#334155", radius=8, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_active = ''
        self.background_color = (0, 0, 0, 0)
        self.cursor_color = get_color_from_hex("#0EA5E9")  # Sky Blue cursor
        self.foreground_color = get_color_from_hex("#F8FAFC")  # slate-50
        self.hint_text_color = get_color_from_hex("#64748B")  # slate-500
        self.padding = [dp(14), dp(12), dp(14), dp(12)]
        self.font_size = '16sp'
        self.radius = dp(radius)
        
        self.normal_border_color = get_color_from_hex(border_color_hex)
        self.active_border_color = get_color_from_hex("#6366F1")  # Indigo-500 focus border
        self.bg_color = get_color_from_hex(bg_color_hex)
        
        with self.canvas.before:
            self.border_paint = Color(*self.normal_border_color)
            self.border_rect = RoundedRectangle(pos=(self.x - dp(1), self.y - dp(1)), size=(self.width + dp(2), self.height + dp(2)), radius=[self.radius])
            self.bg_paint = Color(*self.bg_color)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
            
        self.bind(pos=self.update_rect, size=self.update_rect)
        
    def update_rect(self, *args):
        self.border_rect.pos = (self.x - dp(1), self.y - dp(1))
        self.border_rect.size = (self.width + dp(2), self.height + dp(2))
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        
    def on_focus(self, instance, value):
        if value:
            self.border_paint.rgba = self.active_border_color
        else:
            self.border_paint.rgba = self.normal_border_color


class StyledCard(BoxLayout):
    def __init__(self, bg_color_hex="#1E293B", border_color_hex=None, radius=12, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = get_color_from_hex(bg_color_hex)
        self.radius = dp(radius)
        
        with self.canvas.before:
            if border_color_hex:
                self.border_color = get_color_from_hex(border_color_hex)
                self.border_paint = Color(*self.border_color)
                self.border_rect = RoundedRectangle(pos=(self.x - dp(1), self.y - dp(1)), size=(self.width + dp(2), self.height + dp(2)), radius=[self.radius])
                
            self.bg_paint = Color(*self.bg_color)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
            
        self.bind(pos=self.update_rect, size=self.update_rect)
        
    def update_rect(self, *args):
        if hasattr(self, 'border_rect'):
            self.border_rect.pos = (self.x - dp(1), self.y - dp(1))
            self.border_rect.size = (self.width + dp(2), self.height + dp(2))
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size


class StyledSpinnerOption(SpinnerOption):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = get_color_from_hex("#1E293B")
        self.color = get_color_from_hex("#F8FAFC")
        self.bold = True
        self.height = dp(44)


class StyledSpinner(Spinner):
    def __init__(self, bg_color_hex="#6366F1", radius=8, **kwargs):
        kwargs['option_cls'] = StyledSpinnerOption
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)
        self.color = (1, 1, 1, 1)
        self.bold = True
        self.font_size = '15sp'
        self.radius = dp(radius)
        
        self.bg_color = get_color_from_hex(bg_color_hex)
        self.pressed_color = [c * 0.8 for c in self.bg_color[:3]] + [self.bg_color[3]]
        
        with self.canvas.before:
            self.paint_color = Color(*self.bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
            
        self.bind(pos=self.update_rect, size=self.update_rect)
        
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        
    def on_state(self, instance, value):
        if value == 'down':
            self.paint_color.rgba = self.pressed_color
        else:
            self.paint_color.rgba = self.bg_color

# -----------------------------------------------------------------------------
# POPUPS
# -----------------------------------------------------------------------------

class AboutPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "About Application"
        self.title_size = '18sp'
        self.size_hint = (0.9, 0.8)
        self.background = ""
        self.background_color = (0, 0, 0, 0)
        
        card = StyledCard(orientation='vertical', padding=dp(15), spacing=dp(12), bg_color_hex="#0F172A", border_color_hex="#334155")
        
        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(15))
        content.bind(minimum_height=content.setter('height'))
        
        def create_section(section_title, section_text):
            lbl_title = Label(text=section_title, bold=True, color=get_color_from_hex("#38BDF8"), size_hint_y=None, height=dp(30), font_size='16sp', halign='left')
            lbl_title.bind(width=lambda s, w: s.setter('text_size')(s, (w, None)))
            
            lbl_text = Label(text=section_text, color=get_color_from_hex("#CBD5E1"), size_hint_y=None, font_size='14sp', halign='left')
            lbl_text.bind(width=lambda s, w: s.setter('text_size')(s, (w, None)))
            lbl_text.bind(texture_size=lambda s, t: s.setter('height')(s, t[1]))
            
            content.add_widget(lbl_title)
            content.add_widget(lbl_text)
            
        create_section(
            "🌐 OFFLINE LANGUAGE TRANSLATOR",
            "Final Year Project - Enhanced Edition\n\n"
            "This application provides lightweight, secure, and fully offline translation between English and multiple languages.\n\n"
            "Features:\n"
            "✔ Heuristic phrase & word-by-word local translation\n"
            "✔ Native Speech-to-Text Voice Input\n"
            "✔ Native Text-to-Speech Voice Synthesis\n"
            "✔ Zero internet connection required\n"
            "✔ Persistent local translation history\n"
            "✔ One-tap copy to clipboard"
        )
        
        create_section(
            "🛠 TECHNOLOGY STACK",
            "- Python 3\n"
            "- Kivy UI Framework\n"
            "- Native Android SDK APIs via PyJNIus\n"
            "- Local JSON Translation Database"
        )
        
        create_section(
            "👨‍💻 DEVELOPERS",
            "Developers:\nSANYU PATIENCE\nNALULE SHIRAH MUTEEBI\nKAYAGA CATHERINE\n\nSupervisor:\nDR ALI NAGIB\n\nInstitution:\nMUTEESA I ROYAL UNIVERSITY"
        )
        
        scroll.add_widget(content)
        card.add_widget(scroll)
        
        btn = RoundedButton(text="Close", bg_color_hex="#475569", size_hint_y=None, height=dp(45))
        btn.bind(on_press=self.dismiss)
        card.add_widget(btn)
        
        self.content = card


class HistoryPopup(Popup):
    def __init__(self, history_list, clear_callback, **kwargs):
        super().__init__(**kwargs)
        self.title = "Translation History"
        self.title_size = '18sp'
        self.size_hint = (0.9, 0.8)
        self.background = ""
        self.background_color = (0, 0, 0, 0)
        self.clear_callback = clear_callback
        
        self.card = StyledCard(orientation='vertical', padding=dp(15), spacing=dp(12), bg_color_hex="#0F172A", border_color_hex="#334155")
        
        self.scroll = ScrollView()
        self.list_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(10))
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))
        
        self.populate_list(history_list)
        
        self.scroll.add_widget(self.list_layout)
        self.card.add_widget(self.scroll)
        
        btn_box = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))
        
        clear_btn = RoundedButton(text="Clear History", bg_color_hex="#EF4444", size_hint_x=0.5)
        clear_btn.bind(on_press=self.clear_history)
        
        close_btn = RoundedButton(text="Close", bg_color_hex="#475569", size_hint_x=0.5)
        close_btn.bind(on_press=self.dismiss)
        
        btn_box.add_widget(clear_btn)
        btn_box.add_widget(close_btn)
        self.card.add_widget(btn_box)
        
        self.content = self.card
        
    def populate_list(self, history_list):
        self.list_layout.clear_widgets()
        if not history_list:
            lbl = Label(text="No translation history yet", color=get_color_from_hex("#64748B"), size_hint_y=None, height=dp(50))
            self.list_layout.add_widget(lbl)
            return
            
        for item in history_list:
            item_box = StyledCard(orientation='vertical', padding=dp(10), spacing=dp(4), size_hint_y=None, height=dp(85), bg_color_hex="#1E293B", radius=6)
            
            lang_label = Label(text=f"English ➔ {item['lang'].title()}", bold=True, color=get_color_from_hex("#38BDF8"), font_size='12sp', size_hint_y=None, height=dp(15), halign='left')
            lang_label.bind(width=lambda s, w: s.setter('text_size')(s, (w, None)))
            
            src_label = Label(text=f"In: {item['source']}", color=get_color_from_hex("#94A3B8"), font_size='13sp', size_hint_y=None, height=dp(20), halign='left')
            src_label.bind(width=lambda s, w: s.setter('text_size')(s, (w, None)))
            
            tgt_label = Label(text=f"Out: {item['target']}", color=get_color_from_hex("#F1F5F9"), font_size='14sp', size_hint_y=None, height=dp(25), halign='left', bold=True)
            tgt_label.bind(width=lambda s, w: s.setter('text_size')(s, (w, None)))
            
            item_box.add_widget(lang_label)
            item_box.add_widget(src_label)
            item_box.add_widget(tgt_label)
            self.list_layout.add_widget(item_box)
            
    def clear_history(self, instance):
        self.clear_callback()
        self.populate_list([])


class InfoPopup(Popup):
    def __init__(self, title_text, msg_text, **kwargs):
        super().__init__(**kwargs)
        self.title = title_text
        self.title_size = '18sp'
        self.size_hint = (0.85, 0.35)
        self.background = ""
        self.background_color = (0, 0, 0, 0)
        
        card = StyledCard(orientation='vertical', padding=dp(15), spacing=dp(15), bg_color_hex="#0F172A", border_color_hex="#334155")
        
        lbl = Label(text=msg_text, markup=True, font_size='15sp', halign='center', color=get_color_from_hex("#CBD5E1"))
        lbl.bind(width=lambda s, w: s.setter('text_size')(s, (w, None)))
        
        btn = RoundedButton(text="OK", bg_color_hex="#6366F1", size_hint_y=None, height=dp(45))
        btn.bind(on_press=self.dismiss)
        
        card.add_widget(lbl)
        card.add_widget(btn)
        self.content = card


class VoiceSimulatorPopup(Popup):
    def __init__(self, select_callback, **kwargs):
        super().__init__(**kwargs)
        self.title = "🎙 Voice Input Simulator (Desktop)"
        self.title_size = '18sp'
        self.size_hint = (0.9, 0.75)
        self.background = ""
        self.background_color = (0, 0, 0, 0)
        self.select_callback = select_callback
        
        card = StyledCard(orientation='vertical', padding=dp(15), spacing=dp(12), bg_color_hex="#0F172A", border_color_hex="#334155")
        
        lbl = Label(
            text="[color=#38BDF8][b]Desktop Demo Mode[/b][/color]\nVoice input is only available natively on Android. Select a simulated speech phrase below to feed into the translator:",
            markup=True,
            font_size='14sp',
            size_hint_y=None,
            height=dp(60),
            halign='center'
        )
        lbl.bind(width=lambda s, w: s.setter('text_size')(s, (w, None)))
        card.add_widget(lbl)
        
        scroll = ScrollView()
        list_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(8))
        list_layout.bind(minimum_height=list_layout.setter('height'))
        
        phrases = [
            "Hello, how are you?",
            "Good morning, where is the toilet?",
            "Thank you for the delicious food.",
            "Excuse me, how much is this?",
            "I need a doctor, please help.",
            "Where is the hotel or hospital?",
            "I love my family and my house."
        ]
        
        for phrase in phrases:
            btn = RoundedButton(text=phrase, bg_color_hex="#1E293B", size_hint_y=None, height=dp(45))
            btn.bind(on_press=lambda inst, p=phrase: self.select_phrase(p))
            list_layout.add_widget(btn)
            
        scroll.add_widget(list_layout)
        card.add_widget(scroll)
        
        close_btn = RoundedButton(text="Cancel", bg_color_hex="#475569", size_hint_y=None, height=dp(45))
        close_btn.bind(on_press=self.dismiss)
        card.add_widget(close_btn)
        
        self.content = card
        
    def select_phrase(self, phrase):
        self.select_callback(phrase)
        self.dismiss()

# -----------------------------------------------------------------------------
# TRANSLATOR SCREEN
# -----------------------------------------------------------------------------

class TranslatorScreen(Screen):
    VOICE_INPUT_REQUEST_CODE = 4444

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Initialize TTS engine if on Android
        self.tts_engine = None
        if is_android:
            try:
                self.tts_engine = TextToSpeech(PythonActivity.mActivity, None)
            except Exception as e:
                print(f"Failed to initialize TTS engine: {e}")
                
            # Bind to activity results to handle speech recognition return
            try:
                activity.bind(on_activity_result=self.on_activity_result)
            except Exception as e:
                print(f"Failed to bind activity results: {e}")
        
        # 1. ROOT LAYOUT
        root_layout = BoxLayout(orientation='vertical')
        
        # 2. HEADER (Fixed height, remains at top of screen)
        header = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(10), padding=[dp(15), dp(5), dp(15), dp(5)])
        
        with header.canvas.before:
            Color(*get_color_from_hex("#0F172A"))
            self.header_bg = RoundedRectangle(pos=header.pos, size=header.size)
            
        header.bind(pos=self.update_header_bg, size=self.update_header_bg)
            
        # Title with Logo
        title_layout = BoxLayout(orientation='horizontal', spacing=dp(8), size_hint_x=0.5)
        logo_path = check_icon("logo.png")
        if logo_path:
            title_logo = Image(source=logo_path, size_hint=(None, None), size=(dp(30), dp(30)), pos_hint={'center_y': 0.5})
            title_layout.add_widget(title_logo)
        title_lbl = Label(text="Offline Translator", bold=True, font_size='18sp', color=get_color_from_hex("#F8FAFC"), valign='middle')
        title_lbl.bind(width=lambda s, w: s.setter('text_size')(s, (w, s.height)))
        title_layout.add_widget(title_lbl)
        
        hist_btn = RoundedIconButton(text="History", icon_source="history.png", bg_color_hex="#0EA5E9", size_hint_x=None, width=dp(100))
        hist_btn.bind(on_press=self.show_history)
        
        about_btn = RoundedIconButton(text="About", icon_source="about.png", bg_color_hex="#475569", size_hint_x=None, width=dp(90))
        about_btn.bind(on_press=self.show_about)
        
        header.add_widget(title_layout)
        header.add_widget(hist_btn)
        header.add_widget(about_btn)
        root_layout.add_widget(header)
        
        # 3. SCROLLABLE CONTAINER
        scroll = ScrollView()
        scroll_content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(14), padding=[dp(15), dp(12), dp(15), dp(15)])
        scroll_content.bind(minimum_height=scroll_content.setter('height'))
        
        # 4. LANGUAGE SELECTOR CARD (Bidirectional spinners + swap button)
        lang_card = StyledCard(orientation='horizontal', padding=[dp(12), dp(10)], spacing=dp(10), size_hint_y=None, height=dp(60), bg_color_hex="#1E293B")
        
        self.src_lang_spinner = StyledSpinner(
            text="English",
            values=("English", "Spanish", "French", "German", "Italian", "Portuguese", "Swahili", "Luganda"),
            size_hint_x=0.42
        )
        self.src_lang_spinner.bind(text=self.on_lang_change)
        
        swap_btn = RoundedIconButton(
            icon_source="swap.png",
            bg_color_hex="#475569",
            size_hint_x=None,
            width=dp(45),
            radius=22.5
        )
        swap_btn.bind(on_press=self.swap_languages)
        
        self.tgt_lang_spinner = StyledSpinner(
            text="Spanish",
            values=("English", "Spanish", "French", "German", "Italian", "Portuguese", "Swahili", "Luganda"),
            size_hint_x=0.42
        )
        self.tgt_lang_spinner.bind(text=self.on_lang_change)
        
        lang_card.add_widget(self.src_lang_spinner)
        lang_card.add_widget(swap_btn)
        lang_card.add_widget(self.tgt_lang_spinner)
        scroll_content.add_widget(lang_card)
        
        # 5. INPUT CARD
        input_card = StyledCard(orientation='vertical', padding=dp(12), spacing=dp(8), size_hint_y=None, height=dp(200), bg_color_hex="#1E293B")
        
        input_header = BoxLayout(size_hint_y=None, height=dp(35), spacing=dp(10))
        self.input_title = Label(text="Input Text (English):", bold=True, font_size='14sp', color=get_color_from_hex("#38BDF8"), halign='left', valign='middle')
        self.input_title.bind(width=lambda s, w: s.setter('text_size')(s, (w, s.height)))
        
        mic_btn = RoundedIconButton(text="Record", icon_source="mic.png", bg_color_hex="#EF4444", size_hint_x=None, width=dp(105))
        mic_btn.bind(on_press=self.start_voice_input)
        
        input_header.add_widget(self.input_title)
        input_header.add_widget(mic_btn)
        input_card.add_widget(input_header)
        
        self.input_text = RoundedTextInput(
            hint_text="Type English text here or use voice record...",
            multiline=True
        )
        input_card.add_widget(self.input_text)
        scroll_content.add_widget(input_card)
        
        # 6. ACTION BUTTONS ROW
        actions_row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
        
        translate_btn = RoundedButton(text="Translate", bg_color_hex="#6366F1")
        translate_btn.bind(on_press=self.translate)
        
        self.copy_btn = RoundedIconButton(text="Copy", icon_source="copy.png", bg_color_hex="#10B981", size_hint_x=0.35)
        self.copy_btn.bind(on_press=self.copy_to_clipboard)
        
        clear_btn = RoundedIconButton(text="Clear", icon_source="clear.png", bg_color_hex="#475569", size_hint_x=0.35)
        clear_btn.bind(on_press=self.clear)
        
        actions_row.add_widget(translate_btn)
        actions_row.add_widget(self.copy_btn)
        actions_row.add_widget(clear_btn)
        scroll_content.add_widget(actions_row)
        
        # 7. OUTPUT CARD (Dual text visibility)
        output_card = StyledCard(orientation='vertical', padding=dp(12), spacing=dp(8), size_hint_y=None, height=dp(220), bg_color_hex="#1E293B")
        
        output_header = BoxLayout(size_hint_y=None, height=dp(35), spacing=dp(10))
        output_title = Label(text="Translation:", bold=True, font_size='14sp', color=get_color_from_hex("#38BDF8"), halign='left', valign='middle')
        output_title.bind(width=lambda s, w: s.setter('text_size')(s, (w, s.height)))
        
        self.speak_btn = RoundedIconButton(text="Speak", icon_source="speak.png", bg_color_hex="#10B981", size_hint_x=None, width=dp(100))
        self.speak_btn.bind(on_press=self.speak_translation)
        
        output_header.add_widget(output_title)
        output_header.add_widget(self.speak_btn)
        output_card.add_widget(output_header)
        
        output_scroll = ScrollView()
        output_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(8))
        output_layout.bind(minimum_height=output_layout.setter('height'))
        
        self.output_src_label = Label(
            text="",
            color=get_color_from_hex("#94A3B8"),
            font_size='14sp',
            valign='top',
            halign='left',
            size_hint_y=None,
            italic=True
        )
        self.output_src_label.bind(width=lambda s, w: s.setter('text_size')(s, (w, None)))
        self.output_src_label.bind(texture_size=lambda s, t: s.setter('height')(s, t[1]))
        
        self.output_label = Label(
            text="Translation will appear here...",
            color=get_color_from_hex("#F8FAFC"),
            font_size='16sp',
            valign='top',
            halign='left',
            size_hint_y=None,
            bold=True
        )
        self.output_label.bind(width=lambda s, w: s.setter('text_size')(s, (w, None)))
        self.output_label.bind(texture_size=lambda s, t: s.setter('height')(s, t[1]))
        
        output_layout.add_widget(self.output_src_label)
        output_layout.add_widget(self.output_label)
        output_scroll.add_widget(output_layout)
        output_card.add_widget(output_scroll)
        scroll_content.add_widget(output_card)
        
        # Add scroll content to scroll container, and container to root
        scroll.add_widget(scroll_content)
        root_layout.add_widget(scroll)
        
        self.add_widget(root_layout)
        
    def update_header_bg(self, instance, value):
        self.header_bg.pos = instance.pos
        self.header_bg.size = instance.size

    def show_about(self, instance):
        AboutPopup().open()
        
    def show_history(self, instance):
        app = App.get_running_app()
        HistoryPopup(app.history, app.clear_history).open()
        
    def on_lang_change(self, spinner, text):
        self.update_input_card_title()
        if self.input_text.text.strip():
            self.translate(None)
            
    def update_input_card_title(self):
        src_lang = self.src_lang_spinner.text
        self.input_title.text = f"Input Text ({src_lang}):"
        self.input_text.hint_text = f"Type {src_lang} text here or use voice record..."
            
    def swap_languages(self, instance):
        src = self.src_lang_spinner.text
        tgt = self.tgt_lang_spinner.text
        self.src_lang_spinner.text = tgt
        self.tgt_lang_spinner.text = src
        self.update_input_card_title()
        if self.input_text.text.strip():
            self.translate(None)
            
    def translate(self, instance):
        text = self.input_text.text.strip()
        if not text:
            self.output_label.markup = True
            self.output_label.text = "[color=#EF4444]Please enter text to translate.[/color]"
            self.output_src_label.text = ""
            return
            
        src_lang = self.src_lang_spinner.text
        target_lang = self.tgt_lang_spinner.text
        app = App.get_running_app()
        
        result = app.perform_translation(text, src_lang, target_lang)
        self.output_label.markup = False
        self.output_label.text = result
        self.output_src_label.text = f"{src_lang}: {text}"
        
        app.add_history(text, src_lang, target_lang, result)
        
    def clear(self, instance):
        self.input_text.text = ""
        self.output_label.text = "Translation will appear here..."
        self.output_src_label.text = ""
        
    def copy_to_clipboard(self, instance):
        text = self.output_label.text
        if text and text != "Translation will appear here..." and not text.startswith("[color="):
            Clipboard.copy(text)
            
            old_text = self.copy_btn.label.text if hasattr(self.copy_btn, 'label') else self.copy_btn.text
            if hasattr(self.copy_btn, 'label'):
                self.copy_btn.label.text = "Copied!"
            self.copy_btn.bg_color = get_color_from_hex("#059669")
            self.copy_btn.paint_color.rgba = self.copy_btn.bg_color
            
            def reset_btn(dt):
                if hasattr(self.copy_btn, 'label'):
                    self.copy_btn.label.text = old_text
                self.copy_btn.bg_color = get_color_from_hex("#10B981")
                self.copy_btn.paint_color.rgba = self.copy_btn.bg_color
                
            from kivy.clock import Clock
            Clock.schedule_once(reset_btn, 1.5)

    def show_info_popup(self, title, message):
        InfoPopup(title, message).open()

    def start_voice_input(self, instance):
        if is_android:
            try:
                from android.permissions import check_permission, request_permissions
                if not check_permission("android.permission.RECORD_AUDIO"):
                    request_permissions(["android.permission.RECORD_AUDIO"], self.on_permission_result)
                else:
                    self._do_start_voice_input()
            except Exception as e:
                print(f"Permission error: {e}")
                self._do_start_voice_input()
        else:
            # Show the desktop simulation popup
            VoiceSimulatorPopup(select_callback=self.simulated_voice_callback).open()

    @mainthread
    def on_permission_result(self, permissions, grant_results):
        if grant_results and grant_results[0]:
            self._do_start_voice_input()
        else:
            self.show_info_popup("Permission Denied", "Audio recording permission is required for voice input.")

    def _do_start_voice_input(self):
        try:
            src_lang = self.src_lang_spinner.text.lower()
            lang_codes = {
                "english": "en-US",
                "spanish": "es-ES",
                "french": "fr-FR",
                "german": "de-DE",
                "italian": "it-IT",
                "portuguese": "pt-PT",
                "swahili": "sw-KE",
                "luganda": "lg-UG"
            }
            lang_code = lang_codes.get(src_lang, "en-US")
            
            intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, lang_code)
            intent.putExtra(RecognizerIntent.EXTRA_PROMPT, f"Speak now in {self.src_lang_spinner.text}...")
            PythonActivity.mActivity.startActivityForResult(intent, self.VOICE_INPUT_REQUEST_CODE)
        except Exception as e:
            self.show_info_popup("Voice Input Error", f"Failed to start speech recognizer:\n{str(e)}")

    def simulated_voice_callback(self, phrase):
        self.input_text.text = phrase
        self.translate(None)
        self.show_info_popup("🎙 Speech Simulated", f"Simulated speech input received:\n[b]\"{phrase}\"[/b]")

    @mainthread
    def on_activity_result(self, request_code, result_code, intent_data):
        if request_code == self.VOICE_INPUT_REQUEST_CODE:
            # -1 is RESULT_OK in Android
            if result_code == -1 and intent_data is not None:
                try:
                    results = intent_data.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)
                    if results and results.size() > 0:
                        spoken_text = results.get(0)
                        self.input_text.text = spoken_text
                        self.translate(None)
                except Exception as e:
                    self.show_info_popup("Voice Input Error", f"Error parsing voice input results:\n{str(e)}")
            else:
                self.show_info_popup("Voice Input", "No voice input was captured.")

    def speak_translation(self, instance):
        text = self.output_label.text.strip()
        if not text or text == "Translation will appear here..." or text.startswith("[color="):
            self.show_info_popup("Voice Output", "No translation available to speak.")
            return

        target_lang = self.tgt_lang_spinner.text.lower()
        lang_codes = {
            "english": "en",
            "spanish": "es",
            "french": "fr",
            "german": "de",
            "italian": "it",
            "portuguese": "pt",
            "swahili": "sw",
            "luganda": "lg"
        }
        lang_code = lang_codes.get(target_lang, "en")

        if is_android and self.tts_engine is not None:
            try:
                # Set Locale
                locale_obj = Locale(lang_code)
                self.tts_engine.setLanguage(locale_obj)
                self.tts_engine.speak(text, TextToSpeech.QUEUE_FLUSH, None)
            except Exception as e:
                self.show_info_popup("Voice Output Error", f"Failed to run TTS engine:\n{str(e)}")
        else:
            # Desktop Simulation mode
            old_text = self.speak_btn.label.text if hasattr(self.speak_btn, 'label') else self.speak_btn.text
            if hasattr(self.speak_btn, 'label'):
                self.speak_btn.label.text = "Speaking..."
            self.speak_btn.bg_color = get_color_from_hex("#059669")
            self.speak_btn.paint_color.rgba = self.speak_btn.bg_color

            def reset_speak_btn(dt):
                if hasattr(self.speak_btn, 'label'):
                    self.speak_btn.label.text = old_text
                self.speak_btn.bg_color = get_color_from_hex("#10B981")
                self.speak_btn.paint_color.rgba = self.speak_btn.bg_color

            from kivy.clock import Clock
            Clock.schedule_once(reset_speak_btn, 2.0)
            
            # Print to stdout and show a simulated toast
            print(f"[TTS Desktop Simulation] Speaking [{target_lang.upper()}]: {text}")
            self.show_info_popup("🔊 Speech Simulated", f"Desktop simulation speaking translation ({target_lang.upper()}):\n\n[i]\"{text}\"[/i]")

# -----------------------------------------------------------------------------
# APPLICATION CLASS
# -----------------------------------------------------------------------------

class TranslatorApp(App):
    def build(self):
        self.title = "Offline Language Translator"
        self.history = []
        self.translations = {}
        
        self.load_history()
        self.load_translations()
        
        # Configure keyboard behavior to resize screen when keyboard opens on Android
        Window.softinput_mode = 'resize'
        Window.clearcolor = get_color_from_hex("#0F172A")  # Deep Navy-Slate background
        
        sm = ScreenManager()
        sm.add_widget(TranslatorScreen(name="main"))
        return sm
        
    def load_translations(self):
        # Fallback offline dictionary in python memory
        self.translations = {
            "spanish": {
                "hello": "hola",
                "how are you": "cómo estás",
                "good morning": "buenos días",
                "thank you": "gracias",
                "welcome": "bienvenido",
                "goodbye": "adiós",
                "please": "por favor",
                "yes": "sí",
                "no": "no",
                "water": "agua",
                "food": "comida",
                "friend": "amigo / amiga",
                "family": "familia",
                "house": "casa",
                "good night": "buenas noches",
                "excuse me": "disculpe",
                "sorry": "lo siento",
                "help": "ayuda",
                "where is the toilet": "¿dónde está el baño?",
                "how much is this": "¿cuánto cuesta esto?",
                "i love you": "te amo",
                "school": "escuela",
                "hospital": "hospital",
                "doctor": "médico / doctor",
                "money": "dinero",
                "market": "mercado",
                "bus": "autobús / bus",
                "hotel": "hotel",
                "phone": "teléfono"
            },
            "french": {
                "hello": "bonjour",
                "how are you": "comment ça va",
                "good morning": "bonjour",
                "thank you": "merci",
                "welcome": "bienvenue",
                "goodbye": "au revoir",
                "please": "s'il vous plaît",
                "yes": "oui",
                "no": "non",
                "water": "eau",
                "food": "nourriture",
                "friend": "ami / amie",
                "family": "famille",
                "house": "maison",
                "good night": "bonne nuit",
                "excuse me": "excusez-moi",
                "sorry": "désolé",
                "help": "aide",
                "where is the toilet": "où sont les toilettes?",
                "how much is this": "combien ça coûte?",
                "i love you": "je t'aime",
                "school": "école",
                "hospital": "hôpital",
                "doctor": "médecin / docteur",
                "money": "argent",
                "market": "marché",
                "bus": "bus / autobus",
                "hotel": "hôtel",
                "phone": "téléphone"
            },
            "german": {
                "hello": "hallo",
                "how are you": "wie geht es dir",
                "good morning": "guten morgen",
                "thank you": "danke",
                "welcome": "willkommen",
                "goodbye": "auf wiedersehen",
                "please": "bitte",
                "yes": "ja",
                "no": "nein",
                "water": "wasser",
                "food": "essen",
                "friend": "freund / freundin",
                "family": "familie",
                "house": "haus",
                "good night": "gute nacht",
                "excuse me": "entschuldigung",
                "sorry": "tut mir leid",
                "help": "hilfe",
                "where is the toilet": "wo ist die toilette?",
                "how much is this": "wie viel kostet das?",
                "i love you": "ich liebe dich",
                "school": "schule",
                "hospital": "krankenhaus",
                "doctor": "arzt / ärztin",
                "money": "geld",
                "market": "markt",
                "bus": "bus",
                "hotel": "hotel",
                "phone": "telefon"
            },
            "italian": {
                "hello": "ciao",
                "how are you": "come stai",
                "good morning": "buongiorno",
                "thank you": "grazie",
                "welcome": "benvenuto",
                "goodbye": "arrivederci",
                "please": "per favore",
                "yes": "sì",
                "no": "no",
                "water": "acqua",
                "food": "cibo",
                "friend": "amico / amica",
                "family": "famiglia",
                "house": "casa",
                "good night": "buonanotte",
                "excuse me": "scusi / scusa",
                "sorry": "mi dispiace",
                "help": "aiuto",
                "where is the toilet": "dov'è il bagno?",
                "how much is this": "quanto costa questo?",
                "i love you": "ti amo",
                "school": "scuola",
                "hospital": "ospedale",
                "doctor": "medico / dottore",
                "money": "soldi / denaro",
                "market": "mercato",
                "bus": "autobus / bus",
                "hotel": "hotel",
                "phone": "telefono"
            },
            "portuguese": {
                "hello": "olá",
                "how are you": "como vai",
                "good morning": "bom dia",
                "thank you": "obrigado / obrigada",
                "welcome": "bem-vindo",
                "goodbye": "adeus",
                "please": "por favor",
                "yes": "sim",
                "no": "não",
                "water": "água",
                "food": "comida",
                "friend": "amigo / amiga",
                "family": "família",
                "house": "casa",
                "good night": "boa noite",
                "excuse me": "com licença",
                "sorry": "desculpe",
                "help": "ajuda",
                "where is the toilet": "onde fica o banheiro?",
                "how much is this": "quanto custa isto?",
                "i love you": "eu te amo",
                "school": "escola",
                "hospital": "hospital",
                "doctor": "médico / doutor",
                "money": "dinheiro",
                "market": "mercado",
                "bus": "ônibus / autocarro",
                "hotel": "hotel",
                "phone": "telefone"
            },
            "swahili": {
                "hello": "jambo / habari",
                "how are you": "habari gani",
                "good morning": "habari za asubuhi",
                "thank you": "asante",
                "welcome": "karibu",
                "goodbye": "kwaheri",
                "please": "tafadhali",
                "yes": "ndiyo",
                "no": "hapana",
                "water": "maji",
                "food": "chakula",
                "friend": "rafiki",
                "family": "familia",
                "house": "nyumba",
                "good night": "lala salama / habari za usiku",
                "excuse me": "samahani",
                "sorry": "pole",
                "help": "msaidie / usaidizi",
                "where is the toilet": "choo kiko wapi?",
                "how much is this": "hii ni bei gani?",
                "i love you": "nakupenda",
                "school": "shule",
                "hospital": "hospitali",
                "doctor": "daktari",
                "money": "pesa",
                "market": "soko",
                "bus": "basi",
                "hotel": "hoteli",
                "phone": "simu"
            },
            "luganda": {
                "hello": "ki kati / musibye mutya",
                "how are you": "oli otya",
                "good morning": "wasuze otya",
                "thank you": "weebale",
                "welcome": "tukusanyukidde",
                "goodbye": "weeraba",
                "please": "mwattu",
                "yes": "yee",
                "no": "nedda",
                "water": "amazzi",
                "food": "emmere",
                "friend": "mukwano",
                "family": "amaka",
                "house": "enju / nnyumba",
                "good night": "sula bulungi",
                "excuse me": "nsonyiwa",
                "sorry": "kimpasudde / nsonyiwa",
                "help": "buyambi / nnyamba",
                "where is the toilet": "akabuyonjo kali wa?",
                "how much is this": "kino kyamugaso ki / mmeka?",
                "i love you": "nkwagala",
                "school": "essomero",
                "hospital": "eddwaliro",
                "doctor": "omusawo",
                "money": "ssente",
                "market": "akatale",
                "bus": "baasi",
                "hotel": "wooteri",
                "phone": "essimu"
            }
        }
        
        # Load translations database from translations.json
        try:
            # Look in the main script folder
            json_path = os.path.join(os.path.dirname(__file__), "translations.json")
            if not os.path.exists(json_path):
                json_path = "translations.json"
                
            if os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as f:
                    file_data = json.load(f)
                    for lang, data in file_data.items():
                        if lang in self.translations:
                            self.translations[lang].update(data)
                        else:
                            self.translations[lang] = data
                print("Translations loaded from translations.json successfully.")
        except Exception as e:
            print(f"Error loading translations.json: {e}")

    def load_history(self):
        try:
            history_path = os.path.join(os.path.dirname(__file__), "translation_history.json")
            if not os.path.exists(history_path):
                history_path = "translation_history.json"
                
            if os.path.exists(history_path):
                with open(history_path, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
        except Exception as e:
            print(f"Error loading history: {e}")
            self.history = []
            
        # Ensure older history items are compatible with new language names
        for item in self.history:
            if "lang" in item:
                item["lang"] = item["lang"].lower()
            
    def save_history(self):
        try:
            history_path = os.path.join(os.path.dirname(__file__), "translation_history.json")
            with open(history_path, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving history: {e}")
            
    def clear_history(self):
        self.history = []
        history_path = os.path.join(os.path.dirname(__file__), "translation_history.json")
        try:
            if os.path.exists(history_path):
                os.remove(history_path)
            elif os.path.exists("translation_history.json"):
                os.remove("translation_history.json")
        except Exception as e:
            print(f"Error removing history file: {e}")
                
    def add_history(self, source, src_lang, tgt_lang, target):
        if self.history and self.history[0]["source"] == source and self.history[0].get("src_lang", "English") == src_lang and self.history[0].get("lang", "Spanish") == tgt_lang and self.history[0]["target"] == target:
            return
            
        self.history.insert(0, {
            "source": source,
            "src_lang": src_lang,
            "lang": tgt_lang.lower(),
            "target": target
        })
        if len(self.history) > 50:
            self.history = self.history[:50]
        self.save_history()

    def get_reverse_translation_dict(self, lang):
        lang = lang.lower()
        if not hasattr(self, '_reverse_translations'):
            self._reverse_translations = {}
            
        if lang in self._reverse_translations:
            return self._reverse_translations[lang]
            
        reverse_dict = {}
        if lang in self.translations:
            for eng_phrase, lang_phrase in self.translations[lang].items():
                parts = [p.strip().lower() for p in re.split(r'[/,]', lang_phrase)]
                for part in parts:
                    if part:
                        cleaned_part = part.strip("?.!,¿¡ ")
                        if cleaned_part not in reverse_dict:
                            reverse_dict[cleaned_part] = eng_phrase
                        if part != cleaned_part and part not in reverse_dict:
                            reverse_dict[part] = eng_phrase
                            
        self._reverse_translations[lang] = reverse_dict
        return reverse_dict

    def perform_translation(self, text, src_lang, tgt_lang):
        text_clean = text.strip()
        if not text_clean:
            return ""
            
        src_lang = src_lang.lower()
        tgt_lang = tgt_lang.lower()
        
        if src_lang == tgt_lang:
            return text_clean
            
        if src_lang == "english":
            return self._translate_forward(text_clean, tgt_lang)
            
        if tgt_lang == "english":
            return self._translate_reverse(text_clean, src_lang)
            
        # Pivot translation: src_lang -> English -> tgt_lang
        english_pivot = self._translate_reverse(text_clean, src_lang)
        if english_pivot.startswith("[ENGLISH] "):
            english_pivot = english_pivot[10:]
        return self._translate_forward(english_pivot, tgt_lang)

    def _translate_forward(self, text_clean, target_lang):
        if target_lang not in self.translations:
            return f"[Language not supported: {target_lang}]"
            
        lang_dict = self.translations[target_lang]
        
        # 1. Exact phrase match
        phrase_key = text_clean.lower().strip("?.!,¿¡ ")
        if phrase_key in lang_dict:
            return lang_dict[phrase_key]
            
        # 2. Heuristic phrase & word translation
        phrases = [k for k in lang_dict.keys() if " " in k]
        phrases.sort(key=lambda x: len(x.split()), reverse=True)
        
        working_text = text_clean
        placeholders = {}
        placeholder_counter = 0
        
        for phrase in phrases:
            escaped_phrase = re.escape(phrase)
            pattern = re.compile(rf"\b{escaped_phrase}\b", re.IGNORECASE)
            
            matches = pattern.findall(working_text)
            if matches:
                for match in matches:
                    placeholder = f"__TOKEN_{placeholder_counter}__"
                    placeholders[placeholder] = {
                        "translation": lang_dict[phrase],
                        "original": match
                    }
                    working_text = pattern.sub(placeholder, working_text, count=1)
                    placeholder_counter += 1
                    
        tokens = re.findall(r"\b[a-zA-ZÀ-ÿ0-9_']+\b|[^\w\s]", working_text)
        if not tokens:
            return f"[{target_lang.upper()}] {text_clean}"
            
        translated_tokens = []
        translated_any = False
        
        for token in tokens:
            if token in placeholders:
                translated_tokens.append(placeholders[token]["translation"])
                translated_any = True
            else:
                token_lower = token.lower()
                if token_lower in lang_dict:
                    trans = lang_dict[token_lower]
                    if token.istitle():
                        trans = trans.title()
                    elif token.isupper():
                        trans = trans.upper()
                    translated_tokens.append(trans)
                    translated_any = True
                else:
                    translated_tokens.append(token)
                    
        if translated_any:
            res = ""
            no_space_before = [",", ".", "!", "?", ";", ":", ")", "]", "}", "\"", "'"]
            no_space_after = ["(", "[", "{", "¿", "¡", "\"", "'"]
            
            for idx, w in enumerate(translated_tokens):
                if idx > 0:
                    prev_w = translated_tokens[idx - 1]
                    if w in [",", ".", "!", "?", ";", ":"] and res.endswith(w):
                        continue
                    if w in no_space_before or prev_w in no_space_after:
                        res += w
                    else:
                        res += " " + w
                else:
                    res += w
            return res
            
        return f"[{target_lang.upper()}] {text_clean}"

    def _translate_reverse(self, text_clean, src_lang):
        if src_lang not in self.translations:
            return f"[Language not supported: {src_lang}]"
            
        lang_dict = self.get_reverse_translation_dict(src_lang)
        
        # 1. Exact phrase match
        phrase_key = text_clean.lower().strip("?.!,¿¡ ")
        if phrase_key in lang_dict:
            return lang_dict[phrase_key]
            
        # 2. Heuristic phrase & word translation
        phrases = [k for k in lang_dict.keys() if " " in k]
        phrases.sort(key=lambda x: len(x.split()), reverse=True)
        
        working_text = text_clean
        placeholders = {}
        placeholder_counter = 0
        
        for phrase in phrases:
            escaped_phrase = re.escape(phrase)
            pattern = re.compile(rf"\b{escaped_phrase}\b", re.IGNORECASE)
            
            matches = pattern.findall(working_text)
            if matches:
                for match in matches:
                    placeholder = f"__TOKEN_{placeholder_counter}__"
                    placeholders[placeholder] = {
                        "translation": lang_dict[phrase],
                        "original": match
                    }
                    working_text = pattern.sub(placeholder, working_text, count=1)
                    placeholder_counter += 1
                    
        tokens = re.findall(r"\b[a-zA-ZÀ-ÿ0-9_']+\b|[^\w\s]", working_text)
        if not tokens:
            return f"[ENGLISH] {text_clean}"
            
        translated_tokens = []
        translated_any = False
        
        for token in tokens:
            if token in placeholders:
                translated_tokens.append(placeholders[token]["translation"])
                translated_any = True
            else:
                token_lower = token.lower()
                if token_lower in lang_dict:
                    trans = lang_dict[token_lower]
                    if token.istitle():
                        trans = trans.title()
                    elif token.isupper():
                        trans = trans.upper()
                    translated_tokens.append(trans)
                    translated_any = True
                else:
                    translated_tokens.append(token)
                    
        if translated_any:
            res = ""
            no_space_before = [",", ".", "!", "?", ";", ":", ")", "]", "}", "\"", "'"]
            no_space_after = ["(", "[", "{", "¿", "¡", "\"", "'"]
            
            for idx, w in enumerate(translated_tokens):
                if idx > 0:
                    prev_w = translated_tokens[idx - 1]
                    if w in [",", ".", "!", "?", ";", ":"] and res.endswith(w):
                        continue
                    if w in no_space_before or prev_w in no_space_after:
                        res += w
                    else:
                        res += " " + w
                else:
                    res += w
            return res
            
        return f"[ENGLISH] {text_clean}"


if __name__ == "__main__":
    TranslatorApp().run()
