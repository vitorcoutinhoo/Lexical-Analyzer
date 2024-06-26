# pylint: disable = C0114, C0301, C0206, C0200, C0303

# Author: Vítor Coutinho
# This file contains the function to recognize the
# tokens of the language.

# import the functions to get the automaton and the reserved words
from codes.reserved_words_and_automaton import (
    get_automaton,
    get_reserved_words,
    get_final_states,
    get_back_states,
)

from codes.reader_pointer import ReaderPointer

# valid chars for the reserved words, just lowercase and underscore
valid_chars = set("abcdefghijklmnopqrstuvwxyz_")

# invalid chars for fist char of the identifier, just uppercase
invalid_chars = set("GHIJKLMNOPQRSTUVWXYZ")

# list of reserved words, final states, back states and automaton dataframe
reserved_words = get_reserved_words()  # get the reserved words
final_states = get_final_states()  # get the final states of the automaton
back_states = get_back_states()  # get the back states of the automaton
automaton = get_automaton()  # get the automaton


# get token function
def get_token(reader: ReaderPointer):
    """
    Function to get the next token in the input code

    Args:
        reader (ReaderPointer): The pointer to read the input code

    Returns:
        token (str): The token recognized
        pointer (list): The pointer position
    """
    initial_state = "0"  # initial state of the automaton
    flag = 0

    # get the first char of the input code
    char = verify_char_is_digit(reader.get_char(reader.pointer)[0])

    # create the lexema with the first char
    lexema = str(char)
    while char in (" ", "\n", "\t"):
        lexema = lexema[
            :-1
        ]  # remove from lexema if the first char it is a space, tab or newline

        char = verify_char_is_digit(reader.get_char(reader.pointer)[0])
        lexema += str(char)

    # if the fist char is None, return end of file
    if char is None:
        return (
            "END OF FILE",
            lexema,
            [reader.pointer[0] + 1, reader.pointer[1] - len(lexema) + 1],
            0,
        )

    if char in invalid_chars:
        while char not in (" ", "\n", "\t"):
            char = verify_char_is_digit(reader.get_char(reader.pointer)[0])
            lexema += str(char)

        return (
            "ERROR",
            lexema,
            [reader.pointer[0] + 1, reader.pointer[1] - len(lexema) + 1],
            31,
        )

    # verify if a cadeia is open an not closed
    if char == '"':
        flag += 1

        while flag < 2:
            char = verify_char_is_digit(reader.get_char(reader.pointer)[0])
            lexema += str(char)

            if char == "\n" or char is None:
                lexema = lexema[:-1]
                reader.pointer[1] -= 1

                return (
                    "ERROR",
                    lexema,
                    [reader.pointer[0] + 1, reader.pointer[1] - len(lexema) + 1],
                    27,
                )

            if char == '"':
                flag += 1

        if flag != 2:
            lexema = lexema[:-1]
            reader.pointer[1] -= 1

            return (
                "ERROR",
                lexema,
                [reader.pointer[0] + 1, reader.pointer[1] - len(lexema) + 1],
                27,
            )

        return (
            "TK_CADEIA",
            lexema,
            [reader.pointer[0] + 1, reader.pointer[1] - len(lexema) + 1],
            0,
        )

    # get the transition from the initial state to the next state
    anterior_state = initial_state
    state = automaton.loc[initial_state, char]

    # if the state is not recognized, return the token not recognized
    if state == "-":
        return (
            "ERROR",
            lexema,
            [reader.pointer[0] + 1, reader.pointer[1] - len(lexema) + 1],
            state,
        )

    # while the char is not None
    while char is not None:

        # if the lexema is a reserved word
        if lexema in reserved_words:
            return (
                f"TK_{lexema}",
                lexema,
                [reader.pointer[0] + 1, reader.pointer[1] - len(lexema) + 1],
                state,
            )  # return the reserved word

        # if the state is a final state, return the token recognized
        if state in final_states:
            if state in back_states:
                if reader.pointer[1] > 0:
                    reader.pointer[1] -= 1  # return the pointer to the last char
                lexema = lexema[:-1]
            return (
                final_states[state],
                lexema,
                [reader.pointer[0] + 1, reader.pointer[1] - len(lexema) + 1],
                state,
            )  # return the token recognized

        # get the next char
        char = verify_char_is_digit(reader.get_char(reader.pointer)[0])
        if char == '"':
            flag += 1

        # if the char is None, return end of file
        if char is None:
            return "END OF FILE", lexema, reader.pointer, 0

        # add the char to the lexema
        lexema += str(char)

        # if the state is 34 and the char is not a valid char, return the error
        if state == "34" and char not in valid_chars:
            lexema = lexema[:-1]
            reader.pointer[1] -= 1

            return (
                "ERROR",
                lexema,
                [reader.pointer[0] + 1, reader.pointer[1] - len(lexema) + 1],
                state,
            )

        # get the next state
        anterior_state = state
        state = automaton.loc[state, char]

        # if the state is not recognized, return the token not recognized
        if state == "-":
            if anterior_state in ("16", "17", "18", "19", "20", "24", "25"):
                lexema = lexema[:-1]
                reader.pointer[1] -= 1

                return (
                    "ERROR",
                    lexema,
                    [reader.pointer[0] + 1, reader.pointer[1] - len(lexema) + 1],
                    20,
                )

            lexema = lexema[:-1]
            reader.pointer[1] -= 1

            return (
                "ERROR",
                lexema,
                [reader.pointer[0] + 1, reader.pointer[1] - len(lexema) + 1],
                state,
            )

    return (
        "ERROR",
        lexema,
        [reader.pointer[0] + 1, reader.pointer[1] - len(lexema) + 1],
        state,
    )  # return if the token is not recognized


def verify_char_is_digit(char: str):
    """
    Function to verify if a char is a digit

    Args:
        char (str): The char to verify

    Returns:
        char (str): if the char is not a digit
        char (int): if the char is a digit (0-9)
    """

    if char is not None and str(char).isdigit():
        char = int(char)

    return char
