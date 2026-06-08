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
from kivy.graphics import Color, RoundedRectangle
from kivy.utils import get_color_from_hex

import json
import os
import re

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
        self.font_size = '16sp'
        self.radius = radius
        
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


class RoundedTextInput(TextInput):
    def __init__(self, bg_color_hex="#1E293B", border_color_hex="#334155", radius=8, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_active = ''
        self.background_color = (0, 0, 0, 0)
        self.cursor_color = get_color_from_hex("#0EA5E9")  # Sky Blue cursor
        self.foreground_color = get_color_from_hex("#F8FAFC")  # slate-50
        self.hint_text_color = get_color_from_hex("#64748B")  # slate-500
        self.padding = [14, 12, 14, 12]
        self.font_size = '16sp'
        self.radius = radius
        
        self.normal_border_color = get_color_from_hex(border_color_hex)
        self.active_border_color = get_color_from_hex("#6366F1")  # Indigo-500 focus border
        self.bg_color = get_color_from_hex(bg_color_hex)
        
        with self.canvas.before:
            self.border_paint = Color(*self.normal_border_color)
            self.border_rect = RoundedRectangle(pos=(self.x - 1, self.y - 1), size=(self.width + 2, self.height + 2), radius=[self.radius])
            self.bg_paint = Color(*self.bg_color)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
            
        self.bind(pos=self.update_rect, size=self.update_rect)
        
    def update_rect(self, *args):
        self.border_rect.pos = (self.x - 1, self.y - 1)
        self.border_rect.size = (self.width + 2, self.height + 2)
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
        self.radius = radius
        
        with self.canvas.before:
            if border_color_hex:
                self.border_color = get_color_from_hex(border_color_hex)
                self.border_paint = Color(*self.border_color)
                self.border_rect = RoundedRectangle(pos=(self.x - 1, self.y - 1), size=(self.width + 2, self.height + 2), radius=[self.radius])
                
            self.bg_paint = Color(*self.bg_color)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
            
        self.bind(pos=self.update_rect, size=self.update_rect)
        
    def update_rect(self, *args):
        if hasattr(self, 'border_rect'):
            self.border_rect.pos = (self.x - 1, self.y - 1)
            self.border_rect.size = (self.width + 2, self.height + 2)
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
        self.height = 44


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
        self.radius = radius
        
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
        
        card = StyledCard(orientation='vertical', padding=15, spacing=12, bg_color_hex="#0F172A", border_color_hex="#334155")
        
        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=15)
        content.bind(minimum_height=content.setter('height'))
        
        def create_section(section_title, section_text):
            lbl_title = Label(text=section_title, bold=True, color=get_color_from_hex("#38BDF8"), size_hint_y=None, height=30, font_size='16sp', halign='left')
            lbl_title.bind(width=lambda s, w: s.setter('text_size')(s, (w, None)))
            
            lbl_text = Label(text=section_text, color=get_color_from_hex("#CBD5E1"), size_hint_y=None, font_size='14sp', halign='left')
            lbl_text.bind(width=lambda s, w: s.setter('text_size')(s, (w, None)))
            lbl_text.bind(texture_size=lambda s, t: s.setter('height')(s, t[1]))
            
            content.add_widget(lbl_title)
            content.add_widget(lbl_text)
            
        create_section(
            "🌐 OFFLINE LANGUAGE TRANSLATOR",
            "Final Year Project\n\n"
            "This application provides lightweight, secure, and fully offline translation between English and multiple languages.\n\n"
            "Features:\n"
            "✔ Heuristic phrase & word-by-word local translation\n"
            "✔ Zero internet connection required\n"
            "✔ Persistent local translation history\n"
            "✔ One-tap copy to clipboard"
        )
        
        create_section(
            "🛠 TECHNOLOGY STACK",
            "- Python 3\n"
            "- Kivy UI Framework\n"
            "- Local JSON Translation Database"
        )
        
        create_section(
            "👨‍💻 DEVELOPERS",
            "Lead Developer:\nYour Name Here\n\nSupervisor:\nLecturer Name\n\nInstitution:\nYour University"
        )
        
        scroll.add_widget(content)
        card.add_widget(scroll)
        
        btn = RoundedButton(text="Close", bg_color_hex="#475569", size_hint_y=None, height=45)
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
        
        self.card = StyledCard(orientation='vertical', padding=15, spacing=12, bg_color_hex="#0F172A", border_color_hex="#334155")
        
        self.scroll = ScrollView()
        self.list_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))
        
        self.populate_list(history_list)
        
        self.scroll.add_widget(self.list_layout)
        self.card.add_widget(self.scroll)
        
        btn_box = BoxLayout(size_hint_y=None, height=45, spacing=10)
        
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
            lbl = Label(text="No translation history yet", color=get_color_from_hex("#64748B"), size_hint_y=None, height=50)
            self.list_layout.add_widget(lbl)
            return
            
        for item in history_list:
            item_box = StyledCard(orientation='vertical', padding=10, spacing=4, size_hint_y=None, height=85, bg_color_hex="#1E293B", radius=6)
            
            lang_label = Label(text=f"English ➔ {item['lang'].title()}", bold=True, color=get_color_from_hex("#38BDF8"), font_size='12sp', size_hint_y=None, height=15, halign='left')
            lang_label.bind(width=lambda s, w: s.setter('text_size')(s, (w, None)))
            
            src_label = Label(text=f"In: {item['source']}", color=get_color_from_hex("#94A3B8"), font_size='13sp', size_hint_y=None, height=20, halign='left', short_overflow=True)
            src_label.bind(width=lambda s, w: s.setter('text_size')(s, (w, None)))
            
            tgt_label = Label(text=f"Out: {item['target']}", color=get_color_from_hex("#F1F5F9"), font_size='14sp', size_hint_y=None, height=25, halign='left', bold=True)
            tgt_label.bind(width=lambda s, w: s.setter('text_size')(s, (w, None)))
            
            item_box.add_widget(lang_label)
            item_box.add_widget(src_label)
            item_box.add_widget(tgt_label)
            self.list_layout.add_widget(item_box)
            
    def clear_history(self, instance):
        self.clear_callback()
        self.populate_list([])

# -----------------------------------------------------------------------------
# TRANSLATOR SCREEN
# -----------------------------------------------------------------------------

class TranslatorScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        main_layout = BoxLayout(orientation='vertical', padding=15, spacing=12)
        
        # 1. HEADER
        header = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        title = Label(
            text="🌐 Offline Translator",
            bold=True,
            font_size='20sp',
            color=get_color_from_hex("#F8FAFC"),
            halign='left'
        )
        title.bind(width=lambda s, w: s.setter('text_size')(s, (w, None)))
        
        hist_btn = RoundedButton(text="History", bg_color_hex="#0EA5E9", size_hint_x=None, width=80)
        hist_btn.bind(on_press=self.show_history)
        
        about_btn = RoundedButton(text="About", bg_color_hex="#475569", size_hint_x=None, width=70)
        about_btn.bind(on_press=self.show_about)
        
        header.add_widget(title)
        header.add_widget(hist_btn)
        header.add_widget(about_btn)
        main_layout.add_widget(header)
        
        # 2. LANGUAGE SELECTOR ROW
        lang_row = BoxLayout(size_hint_y=None, height=50, spacing=10)
        lang_label = Label(text="Translate English to:", bold=True, font_size='16sp', color=get_color_from_hex("#94A3B8"), size_hint_x=0.5, halign='left')
        lang_label.bind(width=lambda s, w: s.setter('text_size')(s, (w, None)))
        
        self.lang_spinner = StyledSpinner(
            text="Spanish",
            values=("Spanish", "French", "German"),
            size_hint_x=0.5
        )
        self.lang_spinner.bind(text=self.on_lang_change)
        
        lang_row.add_widget(lang_label)
        lang_row.add_widget(self.lang_spinner)
        main_layout.add_widget(lang_row)
        
        # 3. INPUT CARD
        input_card = StyledCard(orientation='vertical', padding=10, spacing=6, size_hint_y=0.35, bg_color_hex="#1E293B")
        input_title = Label(text="Input Text (English):", bold=True, font_size='14sp', color=get_color_from_hex("#38BDF8"), size_hint_y=None, height=20, halign='left')
        input_title.bind(width=lambda s, w: s.setter('text_size')(s, (w, None)))
        
        self.input_text = RoundedTextInput(
            hint_text="Type English text here...",
            multiline=True
        )
        input_card.add_widget(input_title)
        input_card.add_widget(self.input_text)
        main_layout.add_widget(input_card)
        
        # 4. ACTION BUTTONS ROW
        actions_row = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        translate_btn = RoundedButton(text="Translate", bg_color_hex="#6366F1")
        translate_btn.bind(on_press=self.translate)
        
        self.copy_btn = RoundedButton(text="Copy", bg_color_hex="#10B981", size_hint_x=0.3)
        self.copy_btn.bind(on_press=self.copy_to_clipboard)
        
        clear_btn = RoundedButton(text="Clear", bg_color_hex="#475569", size_hint_x=0.3)
        clear_btn.bind(on_press=self.clear)
        
        actions_row.add_widget(translate_btn)
        actions_row.add_widget(self.copy_btn)
        actions_row.add_widget(clear_btn)
        main_layout.add_widget(actions_row)
        
        # 5. OUTPUT CARD
        output_card = StyledCard(orientation='vertical', padding=10, spacing=6, size_hint_y=0.35, bg_color_hex="#1E293B")
        output_title = Label(text="Translation:", bold=True, font_size='14sp', color=get_color_from_hex("#38BDF8"), size_hint_y=None, height=20, halign='left')
        output_title.bind(width=lambda s, w: s.setter('text_size')(s, (w, None)))
        
        scroll = ScrollView()
        self.output_label = Label(
            text="Translation will appear here...",
            color=get_color_from_hex("#CBD5E1"),
            font_size='16sp',
            valign='top',
            halign='left',
            size_hint_y=None
        )
        self.output_label.bind(width=lambda s, w: s.setter('text_size')(s, (w, None)))
        self.output_label.bind(texture_size=lambda s, t: s.setter('height')(s, t[1]))
        
        scroll.add_widget(self.output_label)
        output_card.add_widget(output_title)
        output_card.add_widget(scroll)
        main_layout.add_widget(output_card)
        
        self.add_widget(main_layout)
        
    def show_about(self, instance):
        AboutPopup().open()
        
    def show_history(self, instance):
        app = App.get_running_app()
        HistoryPopup(app.history, app.clear_history).open()
        
    def on_lang_change(self, spinner, text):
        if self.input_text.text.strip():
            self.translate(None)
            
    def translate(self, instance):
        text = self.input_text.text.strip()
        if not text:
            self.output_label.markup = True
            self.output_label.text = "[color=#EF4444]Please enter text to translate.[/color]"
            return
            
        target_lang = self.lang_spinner.text
        app = App.get_running_app()
        
        result = app.perform_translation(text, target_lang)
        self.output_label.markup = False
        self.output_label.text = result
        
        app.add_history(text, target_lang, result)
        
    def clear(self, instance):
        self.input_text.text = ""
        self.output_label.text = "Translation will appear here..."
        
    def copy_to_clipboard(self, instance):
        text = self.output_label.text
        if text and text != "Translation will appear here..." and not text.startswith("[color="):
            Clipboard.copy(text)
            self.copy_btn.text = "Copied!"
            self.copy_btn.bg_color = get_color_from_hex("#059669")
            self.copy_btn.paint_color.rgba = self.copy_btn.bg_color
            
            def reset_btn(dt):
                self.copy_btn.text = "Copy"
                self.copy_btn.bg_color = get_color_from_hex("#10B981")
                self.copy_btn.paint_color.rgba = self.copy_btn.bg_color
                
            from kivy.clock import Clock
            Clock.schedule_once(reset_btn, 1.5)

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
                "house": "casa"
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
                "house": "maison"
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
                "house": "haus"
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
                
    def add_history(self, source, lang, target):
        if self.history and self.history[0]["source"] == source and self.history[0]["lang"] == lang and self.history[0]["target"] == target:
            return
            
        self.history.insert(0, {
            "source": source,
            "lang": lang,
            "target": target
        })
        if len(self.history) > 50:
            self.history = self.history[:50]
        self.save_history()

    def perform_translation(self, text, target_lang):
        text_clean = text.strip()
        if not text_clean:
            return ""
            
        target_lang = target_lang.lower()
        if target_lang not in self.translations:
            return f"[Language not supported: {target_lang}]"
            
        lang_dict = self.translations[target_lang]
        
        # 1. Try exact phrase match (case-insensitive, strip common ending punctuation for lookup)
        phrase_key = text_clean.lower().strip("?.!,")
        if phrase_key in lang_dict:
            return lang_dict[phrase_key]
            
        # 2. Heuristic word-by-word translation
        words = re.findall(r"\b[a-zA-Z']+\b|[^\w\s]", text_clean)
        if not words:
            return f"[{target_lang.upper()}] {text_clean}"
            
        translated_words = []
        translated_any = False
        
        for word in words:
            word_lower = word.lower()
            if word_lower in lang_dict:
                trans = lang_dict[word_lower]
                if word.istitle():
                    trans = trans.title()
                elif word.isupper():
                    trans = trans.upper()
                translated_words.append(trans)
                translated_any = True
            else:
                translated_words.append(word)
                
        if translated_any:
            res = ""
            for idx, w in enumerate(translated_words):
                if idx > 0:
                    prev_w = translated_words[idx - 1]
                    if re.match(r"^[a-zA-ZÀ-ÿ]", w) and re.match(r"^[a-zA-ZÀ-ÿ0-9]$|\b", prev_w):
                        if prev_w in ["'", "\"", "(", "¿", "¡"]:
                            res += w
                        else:
                            res += " " + w
                    else:
                        res += w
                else:
                    res += w
            return res
            
        # 3. Fallback
        return f"[{target_lang.upper()}] {text_clean}"


if __name__ == "__main__":
    TranslatorApp().run()
