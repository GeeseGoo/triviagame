# 2 player trivia game using trivia api
# Charles Huang 11/27/2022
import requests
import pygame_menu
from pygame_menu.examples import create_example_window
from pygame import mixer
from random import shuffle
import pygame
from time import sleep

surface = create_example_window('Trivia', (1920, 1080)) # Create window

# Play music in background
mixer.init()
mixer.music.load('./music.mp3')
mixer.music.play(-1)

# Map input to letters
player1_input = {
        pygame.K_a: 'A',
        pygame.K_o: 'B',
        pygame.K_e: 'C',
        pygame.K_u: 'D'
    }
player2_input = {
    pygame.K_h: 'A',
    pygame.K_t: 'B',
    pygame.K_n: 'C',
    pygame.K_s: 'D'
}

# Assign point values
points = {
    'easy': 10,
    'medium': 30,
    'hard': 100
}


# Player class to keep track of score
class Player:
    def __init__(self, name):
        self.name = name
        self.score = 0

    def get_name(self):
        return self.name

    def get_score(self):
        return self.score

    def add_points(self, points):
        self.score += points

    def __str__(self):
        return f'{self.name} has {self.score} points'


# Wait for both players to answer question
def wait_for_input(mymenu):
    sleep(0.5)
    pygame.event.clear()    # Clear event queue so player's can't pre answer
    output = [None, None]   # [player1, player2]
    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.KEYDOWN:
                output = [player1_input.get(event.key, output[0]), player2_input.get(event.key, output[1])]  # Map input to letter
                if output[0] and output[1]:  # If both players have answered
                    return output

        # Update menu
        if mymenu.is_enabled():
            mymenu.update(events)
            mymenu.draw(surface)
        pygame.display.update()


def game_loop(player1, player2):
    question_letters = ['A', 'B', 'C', 'D']
    # Get questions
    questions = requests.get(f'https://the-trivia-api.com/api/questions?categories={category}&limit=10&region=CA)').json()

    # Loop through each question
    for count, i in enumerate(questions):
        question_menu = pygame_menu.Menu(
            height=1080,
            theme=pygame_menu.themes.THEME_DARK,
            title='Question: ' + str(count + 1) + ' Difficulty: ' + i['difficulty'],
            width=1920,
        )
        # Add avatars
        question_menu.add.image('./avatar1.png', scale=(0.3, 0.3)).translate(-800, 400).set_float(True)
        question_menu.add.image('./avatar2.png', scale=(0.4, 0.4)).translate(800, 400).set_float(True).flip(True, False)

        # Display scores
        question_menu.add.label(f"{player1.name}: {player1.get_score()}", font_size=30).translate(-800, 600).set_float(True)
        question_menu.add.label(f"{player2.get_name()}: {player2.get_score()}", font_size=30).translate(800, 600).set_float(True)
        size = 60
        question = i['question']
        if len(question) > 50:  # If question is too long, make font smaller
            size = int(60 / len(question) * 60)
        # Randomize answers
        answers = ([i['correctAnswer']] + i['incorrectAnswers'])
        shuffle(answers)

        # Find correct answer
        correct_answer = question_letters[answers.index(i['correctAnswer'])]

        # Display question
        question_menu.add.label(i['question']).add_underline((231, 246, 242), 3, 2).update_font({'size': size})

        # Display answers
        mc_answers = []
        for count, j in enumerate(answers):
            mc_answers.append(question_menu.add.label(question_letters[count] + '. ' + j).set_padding((15, 0)))

        # Display correct answer
        inputs = wait_for_input(question_menu)
        mc_answers[question_letters.index(correct_answer)].update_font({'color': (0, 255, 0)})

        # Display what each user answered
        question_menu.add.image('./speech_bubble.png', scale=(0.12, 0.12)).set_float(True).translate(-550, -50)
        question_menu.add.image('./speech_bubble.png', scale=(0.12, 0.12)).set_float(True).flip(True, False).translate(550, -50)
        question_menu.add.label(inputs[0]).translate(-550, -20).set_float(True).update_font({'size': 50, 'color': (255, 0, 0) if inputs[0] != correct_answer else (0, 255, 0)})
        question_menu.add.label(inputs[1]).translate(550, -20).set_float(True).update_font({'size': 50, 'color': (255, 0, 0) if inputs[1] != correct_answer else (0, 255, 0)})

        question_menu.draw(surface)
        pygame.display.update()
        sleep(1.5)
        # Total scores
        if inputs[0] == correct_answer:
            player1.add_points(points[i['difficulty']])
        if inputs[1] == correct_answer:
            player2.add_points(points[i['difficulty']])

    # Display final scores on game finish
    final_menu = pygame_menu.Menu(
        height=1080,
        theme=pygame_menu.themes.THEME_DARK,
        title='amongus',
        width=1920,
    )
    if player1.get_score() == player2.get_score():
        final_menu.add.label('Tie!')
    else:
        final_menu.add.label(f'{player1.get_name()} wins!' if player1.get_score() > player2.get_score() else f'{player2.get_name()} wins!', font_size=50)
    final_menu.add.label(f"{player1.name}: {player1.get_score()}", font_size=30)  # Individual scores
    final_menu.add.label(f"{player2.get_name()}: {player2.get_score()}", font_size=30)
    wait_for_input(final_menu)


menu = pygame_menu.Menu(
    height=1080,
    theme=pygame_menu.themes.THEME_DARK,
    title='Mihir VS Jack Fortnite 1v1 Build Battle',
    width=1920
)
category = 'General Knowledge'
def change_category(key, value):
    global category
    value = value.replace(' ', '_').replace('&', 'and').lower()  # Format category for api call
    category = value
def change_name(player, value):
    player.name = value


categories = list(requests.get('https://the-trivia-api.com/api/categories').json().keys())  # Get json of categories from api, getting rid of the subcategories
categories = [(i, i) for i in categories]  # Widget argument format is (text, value)

# Main menu buttons
player1 = Player(menu.add.text_input('Player1 Name: ', default='That_Yak', maxchar=15, onchange=lambda a : change_name(player1, a)).get_value())
player2 = Player(menu.add.text_input('Player2 Name: ', default='Mehere120', maxchar=15, onchange=lambda a : change_name(player2, a)).get_value())
menu.add.selector('Category: ', categories, onchange=change_category, default=3)
menu.add.button('Play', lambda: game_loop(player1, player2))
menu.add.button('Quit', pygame_menu.events.EXIT)

if __name__ == '__main__':  # Start the game
    menu.mainloop(surface)
