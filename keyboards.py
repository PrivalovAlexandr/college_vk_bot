from vkbottle import Keyboard, EMPTY_KEYBOARD, KeyboardButtonColor, Text
from config import *

color = KeyboardButtonColor.PRIMARY

kb_menu = (
    Keyboard()
    .add (Text(menu_key[0]), color)
    .add (Text(menu_key[1]), color)
    .row()
    .add (Text(menu_key[2]), color)
    .add (Text(menu_key[3]), color)
    .get_json()
)

kb_role = (
    Keyboard()
    .add(Text(role[0]), color)
    .add(Text(role[1]), color)
    .get_json()
)

kb_corpus = (
    Keyboard()
    .add(Text(corpus[0]), color)
    .add(Text(corpus[1]), color)
    .get_json()
)

kb_course = (
    Keyboard()
    .add(Text(course[0]), color)
    .add(Text(course[1]), color)
    .add(Text(course[2]), color)
    .add(Text(course[3]), color)
    .get_json()
)

kb_proof = (
    Keyboard()
    .add(Text('Да'), color)
    .add(Text('Нет'), color)
    .get_json()
)