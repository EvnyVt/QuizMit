from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
from kivy.uix.screenmanager import SlideTransition
from kivy.core.audio import SoundLoader
from kivy.resources import resource_find
import random
import json

Window.size = (450, 650)

class QuizApp(App):
    score = 0

    def on_start(self):
        # Carregar os áudios antecipadamente durante a inicialização da aplicação
        self.correct_sound = SoundLoader.load(resource_find('data/correct_sound.mp3'))
        self.incorrect_sound = SoundLoader.load(resource_find('data/incorrect_sound.mp3'))
        self.time_up_sound = SoundLoader.load(resource_find('data/time_up_sound.mp3'))

    def restart_quiz(self):
        self.current_question = 0
        self.score = 0
        self.sm.switch_to(StartScreen(name='start'))

    def build(self):
        with open("quiz_quest.json", "r", encoding="utf-8") as file:
            self.quiz_data = json.load(file)

        combined_data = list(zip(self.quiz_data["questions"], self.quiz_data["options"], self.quiz_data["correct_answers"]))
        random.shuffle(combined_data)

        combined_data = combined_data[:10]

        self.quiz_data["questions"], self.quiz_data["options"], correct_answers = zip(*combined_data)
        self.quiz_data["correct_answers"] = list(correct_answers)

        self.sm = ScreenManager()
        self.start_screen = StartScreen(name="start")
        self.sm.add_widget(self.start_screen)

        self.current_question = 0

        return self.sm

    def stop_and_show_results(self):
        self.sm.switch_to(ResultScreen(name='result'))

class StartScreen(Screen):
    def start_quiz(self):
        if len(quiz_app.quiz_data["questions"]) >= 10:
            quiz_app.current_question = 0
            quiz_app.score = 0
            quiz_app.sm.switch_to(QuestionScreen(name='question'))



class QuestionScreen(Screen):
    timer_duration = 30  

    def on_enter(self):
        self.start_timer()
        self.update_timer(0) 


    def start_timer(self):
        self.timer_seconds = self.timer_duration
        Clock.schedule_interval(self.update_timer, 1)

    def update_timer(self, dt):
        self.ids.timer_label.text = f'Tempo restante: {self.timer_seconds}s'
        self.timer_seconds -= 1

        if self.timer_seconds < 0:
            Clock.unschedule(self.update_timer)
            self.on_timer_end()

        # Add this line to force the screen to update immediately
        self.ids.timer_label.canvas.ask_update()

    def on_timer_end(self):
        # Handle the case when the timer runs out
        quiz_app.current_question += 1
        if quiz_app.time_up_sound:
            quiz_app.time_up_sound.play()

        if quiz_app.current_question < len(quiz_app.quiz_data["questions"]):
            # Move to the next question
            quiz_app.sm.switch_to(QuestionScreen(name='question'))
        else:
            # If there are no more questions, show the results
            quiz_app.stop_and_show_results()

    def check_answer(self, instance, selected_answer):
        correct_answer = quiz_app.quiz_data["correct_answers"][quiz_app.current_question]

        if selected_answer == correct_answer:
            instance.background_color = (0, 74/255, 59/255, 1)  # Verde para resposta correta
            quiz_app.score += 1  # Incrementar a pontuação
            if quiz_app.correct_sound:
                quiz_app.correct_sound.play()
        else:
            instance.background_color = (74/255, 0, 19/255, 1)  # Vermelho para resposta errada
            if quiz_app.incorrect_sound:
                quiz_app.incorrect_sound.play()

        Clock.unschedule(self.update_timer)  
        self.ids.timer_label.text = ''  

        # Agendar a próxima pergunta após um atraso de 0,5 segundos
        Clock.schedule_once(self.show_next_question, 1)

    def show_next_question(self, dt=None):
        if quiz_app.current_question < len(quiz_app.quiz_data["questions"]) - 1:
            quiz_app.current_question += 1
            quiz_app.sm.transition = SlideTransition(direction='left')
            quiz_app.sm.switch_to(QuestionScreen(name='question'))
        else:
            quiz_app.stop_and_show_results()
    def show_previous_question(self, dt=None):
        if quiz_app.current_question > 0:
            quiz_app.current_question -= 1
            quiz_app.sm.transition = SlideTransition(direction='right')
            quiz_app.sm.switch_to(QuestionScreen(name='question'))
        else:
            quiz_app.sm.switch_to(StartScreen(name='start'))
        

class ResultScreen(Screen):
    def on_pre_enter(self):
        self.ids.score_label.text = f'Sua pontuação: {quiz_app.score}/{len(quiz_app.quiz_data["questions"])}'

class ButtonMenu(ButtonBehavior, Label):
    pass

if __name__ == '__main__':
    quiz_app = QuizApp()
    quiz_app.run()
