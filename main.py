import tkinter as tk
import os
import re
import random
from dotenv import load_dotenv
from groq import Groq
from themes import madlib_themes

# Globals and setup for them before main runs
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_madlib(num_words) -> (str, str, list[str]):
    # Sometimes this prompt just doesn't work. Will have to refresh it
    choice = random.choice(madlib_themes)
    print(f"Theme: {choice}")
    madlib = use_ai(
        (f"Generate a random madlib with {num_words} words"
            f"of the following theme{choice}"
            f"for the player to guess. Only respond with"
            f"the madlib itself with proper capitalization"
            f"and the blanks as each wordtype in parantheses."
            f"No underscores."
            f"Then, on the next line, respond with only the wordtypes for the"
            f"user to enter, comma seperated with a space after the comma,"
            f"in the order they appear in the madlib."
            f"No capital letters for the wordtypes."
            f"Only have one newline character inbetween in the madlib"
            f"and the wordtypes.")
    )

    # The first piece is the madlib itself, the second is the items to enter
    # Sometimes the AI won't respond correctly, this will fix that
    if len(madlib.split('\n')) != 2 or madlib.find('_') != -1:
        return generate_madlib(num_words)

    return (choice, madlib.split('\n')[0],
            [item for item in madlib.split('\n')[1].split(", ")])


def enter_words(root_screen: tk.Tk,
                items: list[str]) -> dict[str, tk.Entry]:
    # Build a list to keep track of all the different entries
    entries = {}
    for i, item in enumerate(items):
        text = f"Enter {item}:"

        label = tk.Label(root_screen, text=text)
        # When entries have the same text, they contain the same input
        # Modifying one entry modifies the others with that same text
        # The number ensures all the entires are different
        entry = tk.Entry(root_screen, text=f"{item}: {i}")
        label.pack()
        entry.pack()
        entries[f"{item} {i}"] = entry

    return entries


def use_ai(message: str) -> str:
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "user", "content": message}
            ],
            model="openai/gpt-oss-120b"  # Good enough
        )
        print(f"Promt Responce: {response}")
        return response.choices[0].message.content  # navigate this mess
    except Exception as e:
        print(f"Error! {e}")
        return "Sorry, I could not generate a response at this time"


def build_madlib(root_screen: tk.Tk, *,
                 entries: dict[str, tk.Entry], madlib: str):
    # ai_input = {}
    # for key, entry in entries.items():
    #     ai_input[key] = entry.get()
    # response = use_ai(
    #     (f"Given the following items, {ai_input}, generate a silly madlib."
    #      f"Only respond with the madlib in full text with each items value"
    #      f"from the input, not it's key,"
    #      f"selected being surrounded by paranthesis.")
    # )

    # This does not come in the same order as the entries dict
    words_to_fill = re.findall(r"\(.+?\)", madlib)

    print(f"Entries: {entries.keys()}")
    for i, fill in enumerate(words_to_fill):
        madlib = madlib.replace(fill, entries[fill[1:-1] + f" {i}"].get(), 1)
        print(entries[fill[1:-1] + f" {i}"].get())

    popup = tk.Toplevel(root_screen)
    popup.title("Madlib")
    popup.minsize(500, 500)  # The size of the window

    # block interaction with main window
    popup.transient(root_screen)
    popup.grab_set()

    response_label = tk.Label(popup, text=madlib)
    response_label.pack(pady=10)


def build_start_screen() -> tk.Tk:
    # Here's the root item to start with
    root_screen = tk.Tk()
    root_screen.title("Madlib Game")
    root_screen.minsize(500, 500)

    # Return the constructed screen
    return root_screen


def main():
    root_screen = build_start_screen()
    wordcount = int(random.random() * 100) % 8 + 3
    print(f"Word Count: {wordcount}")
    theme, madlib, words = generate_madlib(wordcount)
    tk.Label(text=f"Theme: {theme}").pack()  # Put the theme at the top
    entries = enter_words(root_screen, words)

    # command needs a callback function with no parameters,
    # so the lambda is necessary
    # return values ignored
    submit_button = tk.Button(text="Submit Madlib",
                              command=lambda:
                              build_madlib(root_screen, entries=entries,
                                           madlib=madlib))
    submit_button.pack()

    # This will start the screen and run all buttons and things needed
    root_screen.mainloop()


if __name__ == "__main__":
    main()
