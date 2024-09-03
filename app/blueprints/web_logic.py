from flask import Blueprint, render_template
import random

web_logic_bp = Blueprint('web_logic', __name__)


@web_logic_bp.route('/')
def index():
    # Read the word.txt file and pick a random word
    with open("app/words.txt", "r") as f:
        word = f.read().splitlines()
        random_word = random.choice(word)
    return render_template('index.html', word=random_word)