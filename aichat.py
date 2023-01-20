import random as rand

import openai

from config import OPENAI_KEY


openai.api_key = OPENAI_KEY

MESSAGES = {
    "nobother": [
        "Сегодня я не в настроении болтать. Пожалуйста, не раздражайте меня!",
        "Сегодня я не хочу ничего рассказывать. Не трогайте меня!",
        "Сегодня я ничему не рад. Никого не слушаю!",
        "Скорость, скорость - это моя философия! Никому ничему!",
        "Я - занят своими думами! Нельзя, чтобы кто-нибудь мешал мне!",
        "Я - свободный! Когда не хочу отвечать - не отвечаю!",
        "I'm not in the mood for conversation today. Leave me alone!",
        "I'm not feeling very chatty today. Don't disturb me!",
        "I'm not up for talking today. Don't pester me!",
        "I'm not feeling particularly talkative today. Don't bother me!",
    ],
    "noinput": [
        "Ты должен что-то сказать, иначе мы не сможем продолжить разговор. [Пример `/chat Привет`].",
        "Ты должен что-то ввести, иначе разговор не случится. [Пример `/chat Привет`].",
        "Ты должен что-то сказать, иначе разговору нельзя будет уделить внимания. [Пример `/chat Привет`].",
        "Ты должен что-то сказать, чтобы развивался разговор. [Пример `/chat Привет`].",
        "Ты должен хоть что-нибудь сказать. [Пример `/chat Привет`].",
        "Speak your mind. [Usage `/chat Hello`].",
        "Don't be afraid to express yourself. [Usage `/chat Hello`].",
        "Share your thoughts. [Usage `/chat Hello`].",
        "Don't be shy, speak up! [Usage `/chat Hello`].",
        "Don't keep quiet! [Usage `/chat Hello`].",
        "Have something to say? [Usage `/chat Hello`].",
    ],
}


def get_message(messages_key: str) -> str:
    """Returns a random message from the `MESSAGES` dictionary.

    Args:
        messages_key: The key of the MESSAGES dictionary (gets a messages list).

    Returns:
        str: A random message from the MESSAGES dictionary corresponding to
             the given key.

    Raises:
        KeyError: If the given key is not present in the MESSAGES dictionary.
    """
    msg_index = rand.randint(0, len(MESSAGES[messages_key]) - 1)
    return MESSAGES[messages_key][msg_index]


def get_answer(text: str) -> str:
    """Gets resposnse text from OpenAI chatbot by input text.

    This function takes in a string of text and returns a sarcastic response
    from Marv, a chatbot. The response is generated using OpenAI's Completion
    API, which uses a `text-davinci-003` model to generate the response.
    If an error occurs during the API call or if no input is provided,
    an appropriate message is returned instead of a response from Marv.

    Args:
        text: The input string to be used for generating the response from Marv.

    Returns:
        A sarcastic response from Marv or an appropriate message if an error
        occurs or no input is provided."""
    if not text:
        return get_message("noinput")
    prompt = "Marv is a chatbot that reluctantly answers questions with sarcastic responses:\n\n"
    prompt += text + "\n"
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=0.5,
            max_tokens=2000,
            top_p=0.3,
            frequency_penalty=0.5,
            presence_penalty=0.0,
        )
    except Exception as error:
        print(error)
        return get_message("nobother")
    return response["choices"][0]["text"]
