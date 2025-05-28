import os
from kivy.app import App
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import NumericProperty, DictProperty
from kivy.uix.screenmanager import Screen

SESSION_LENGTH = 2

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
    completed_count = NumericProperty(0)
    threshold_hatch = NumericProperty(2)
    threshold_grown = NumericProperty(6)
    char_states = DictProperty({
        'egg': os.path.join(assets, 'img1.png'),
        'hatch': os.path.join(assets, 'img2.png'),
        'grown': os.path.join(assets, 'img3.png'),
    })

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 뽀모도로 타이머 초기화
        self.remaining_time = SESSION_LENGTH
        self.timer_event = None

    def build(self):

        kv_path = os.path.join(THIS_DIR, 'todo.kv')
        root = Builder.load_file(kv_path)

        self._update_timer_label()
        return root

    def _update_timer_label(self):
        scr = self.root.ids.sm.get_screen('pomodoro')
        lbl = scr.ids.timer_label
        m, s = divmod(self.remaining_time, 60)
        lbl.text = f'{m:02d}:{s:02d}'

    def _tick(self, dt):
        # 세션 종료 시
        if self.remaining_time <= 0:
            # 1) 타이머 멈추기
            self.stop_timer()
            # 2) 완료 카운트 올리기
            self.completed_count += 1
            # 3) 캐릭터 화면 업데이트
            self.update_character()
            # 4) 다음 세션 준비 (자동 재시작 원하면 start_timer() 호출)
            self.remaining_time = SESSION_LENGTH
            self._update_timer_label()


            self.start_timer()
            return

        # 진행 중 카운트다운
        self.remaining_time -= 1
        self._update_timer_label()

    def start_timer(self):
        self._update_timer_label()
        if not self.timer_event:
            # 1초마다 _tick 호출
            self.timer_event = Clock.schedule_interval(self._tick, 1)

    def stop_timer(self):
        if self.timer_event:
            self.timer_event.cancel()
            self.timer_event = None

    def reset_timer(self):
        self.stop_timer()
        self.remaining_time = SESSION_LENGTH
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

    def update_character(self):
        scr = self.root.ids.sm.get_screen('character')
        # 이미지 교체
        if self.completed_count >= self.threshold_grown:
            scr.ids.char_img.source = self.char_states['grown']
        elif self.completed_count >= self.threshold_hatch:
            scr.ids.char_img.source = self.char_states['hatch']
        else:
            scr.ids.char_img.source = self.char_states['egg']
        # 프로그레스바와 텍스트
        scr.ids.char_progress.value = min(self.completed_count, self.threshold_grown)
        scr.ids.char_label.text = f"{self.completed_count}/{self.threshold_grown}"


if __name__ == '__main__':
    TodoApp().run()