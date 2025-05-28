import os
from kivy.app import App
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock


# 0) 창 배경을 흰색으로
Window.clearcolor = (1, 1, 1, 1)

# 1) 한글 폰트 등록
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
assets = os.path.join(THIS_DIR, 'assets')
LabelBase.register('GangwonEdu', os.path.join(assets, '강원교육새음.ttf'))

# 2) Screen 클래스 정의 (KV에서 사용할 이름과 일치)
class MainScreen(Screen): pass
class PomodoroScreen(Screen): pass
class CharacterDetailScreen(Screen): pass

class TodoApp(App):
    def build(self):
        kv_path = os.path.join(THIS_DIR, 'todo.kv')
        self.remaining_time = 25 * 60
        self.timer_event = None
        return Builder.load_file(kv_path)

    def _update_timer_label(self):
        scr = self.root.ids.sm.get_screen('pomodoro')
        lbl = scr.ids.timer_label
        m, s = divmod(self.remaining_time, 60)
        lbl.text = f'{m:02d}:{s:02d}'

    def _tick(self, dt):
        if self.remaining_time <= 0:
            self.stop_timer()
            return
        self.remaining_time -= 1
        self._update_timer_label()

    def start_timer(self):
        if not self.timer_event:
            # 1초마다 _tick 호출
            self.timer_event = Clock.schedule_interval(self._tick, 1)

    def stop_timer(self):
        if self.timer_event:
            self.timer_event.cancel()
            self.timer_event = None

    def reset_timer(self):
        self.stop_timer()
        self.remaining_time = 25 * 60
        self._update_timer_label()

    def add_task(self, text):
        text = text.strip()
        if not text:
            return
        sm = self.root.ids.sm
        main = sm.get_screen('main')
        box = main.ids.todo_box

        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.checkbox import CheckBox
        from kivy.uix.label import Label
        from kivy.uix.button import Button

        line = BoxLayout(size_hint_y=None, height='30dp', spacing=5)
        chk = CheckBox(size_hint_x=None, width='30dp')
        lbl = Label(
            text=text,
            font_name='GangwonEdu',
            halign='left',
            valign='middle',
            color=(0, 0, 0, 1),
        )
        lbl.bind(size=lbl.setter('text_size'))
        btn = Button(
            text='삭제',
            size_hint_x=None,
            width='60dp',
            font_name='GangwonEdu'
        )
        btn.bind(on_press=lambda inst: box.remove_widget(line))

        line.add_widget(chk)
        line.add_widget(lbl)
        line.add_widget(btn)
        box.add_widget(line)

        main.ids.task_input.text = ''

if __name__ == '__main__':
    TodoApp().run()