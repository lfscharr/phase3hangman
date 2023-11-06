import random
from words import word_list
from sqlalchemy import create_engine, Column, Integer, String, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

# Create a SQLite database using SQLAlchemy
engine = create_engine("sqlite:///hangman_scores.db")
Base = declarative_base()

# Define a HighScore table to store high scores
class HighScore(Base):
    __tablename__ = "high_scores"
    id = Column(Integer, primary_key=True)
    player_name = Column(String, nullable=False)
    score = Column(Integer, nullable=False)
    date = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

Base.metadata.create_all(engine)

def get_word():
    word = random.choice(word_list)
    return word.upper()

def play(word, player_name):
    total = 0
    word_completion = "_" * len(word)
    guessed = False
    guessed_letters = []
    guessed_words = []
    tries = 6
    print("Let's play Hangman!")
    print(display_hangman(tries))
    print(word_completion)
    print("\n")
    while not guessed and tries > 0:
        guess = input("Please guess a letter or word: ").upper()
        if len(guess) == 1 and guess.isalpha():
            if guess in guessed_letters:
                print("You already guessed the letter", guess)
            elif guess not in word:
                print(guess, "is not in the word.")
                tries -= 1
                guessed_letters.append(guess)
            else:
                print("Good job,", guess, "is in the word!")
                total = 1
                guessed_letters.append(guess)
                word_as_list = list(word_completion)
                indices = [i for i, letter in enumerate(word) if letter == guess]
                for index in indices:
                    word_as_list[index] = guess
                word_completion = "".join(word_as_list)
                if "_" not in word_completion:
                    guessed = True
        elif len(guess) == len(word) and guess.isalpha():
            if guess in guessed_words:
                print("You already guessed the word", guess)
            elif guess != word:
                print(guess, "is not the word.")
                tries -= 1
                guessed_words.append(guess)
            else:
                guessed = True
                word_completion = word
        else:
            print("Not a valid guess.")
        print(display_hangman(tries))
        print(word_completion)
        print("\n")
    if guessed:
        print("Congrats, you guessed the word! You win!")

        # Store the high score in the database using SQLAlchemy
        Session = sessionmaker(bind=engine)
        session = Session()
        high_score = HighScore(player_name=player_name, score=total)
        session.add(high_score)
        session.commit()

        print("High score saved.")
    else:
        print("Sorry, you ran out of tries. The word was " + word + ". Maybe next time!")

def display_hangman(tries):
    stages = [  
                """
                   --------
                   |      |
                   |      O
                   |     \\|/
                   |      |
                   |     / \\
                   -
                """,
                
                """
                   --------
                   |      |
                   |      O
                   |     \\|/
                   |      |
                   |     / 
                   -
                """,
                
                """
                   --------
                   |      |
                   |      O
                   |     \\|/
                   |      |
                   |      
                   -
                """,
                
                """
                   --------
                   |      |
                   |      O
                   |     \\|
                   |      |
                   |     
                   -
                """,
                
                """
                   --------
                   |      |
                   |      O
                   |      |
                   |      |
                   |     
                   -
                """,
                
                """
                   --------
                   |      |
                   |      O
                   |    
                   |      
                   |     
                   -
                """,
                
                """
                   --------
                   |      |
                   |      
                   |    
                   |      
                   |     
                   -
                """
    ]
    return stages[tries]

# def main():
#     player_name = input("Enter your name: ")
#     word = get_word()
#     play(word, player_name)
#     while input("Play Again? (Y/N) ").upper() == "Y":
#         word = get_word()
#         play(word, player_name)
        
def delete_player_scores(player_name):
    Session = sessionmaker(bind=engine)
    session = Session()
    session.query(HighScore).filter_by(player_name=player_name).delete()
    session.commit()

def main():
    player_name = input("Enter your name: ")
    word = get_word()
    play(word, player_name)
    while True:
        choice = input("Play Again? (P) / Delete Scores? (D) / Quit? (Q): ").upper()
        
        if choice == "P":
            word = get_word()
            play(word, player_name)
        elif choice == "D":
            # Allow the user to delete their own scores
            delete_player_scores(player_name)
            print("Your scores have been deleted.")
        elif choice == "Q":
            break
        else:
            print("Invalid choice. Please choose 'P', 'D', or 'Q'.")

if __name__ == "__main__":
    main()
