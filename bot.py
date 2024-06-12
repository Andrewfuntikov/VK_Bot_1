from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import handlers
from settings import TOKEN, GROUP_ID
import vk_api
import random
import logging
import scenarios
try:
    import settings
except ImportError:
    exit('DO cp settings.py.default settings.py and set token!')
log = logging.getLogger("bot")


def configure_logging():
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    stream_handler.setLevel(logging.INFO)
    log.addHandler(stream_handler)

    file_handler = logging.FileHandler("bot.log", encoding='UTF-8')
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    file_handler.setLevel(logging.DEBUG)
    log.addHandler(file_handler)

    log.setLevel(logging.DEBUG)


class UserState:
    """Состояние пользователя внутри сценария."""

    def __init__(self, scenario_name, step_name, context=None):
        self.scenario_name = scenario_name
        self.step_name = step_name
        self.context = context or {}


class Bot:
    """
    Сценарий регистрации на конференцию "Skillbox Conf" через vk.com
    Use: python 3.12.3
    Поддерживает ответы на вопросы про дату, место проведения и сценарий регистрации:
    - спрашиваем имя
    - спрашиваем mail
    - говорим об успешной регистрации
    Если шаг не пройден, задаем уточняющий вопрос пока шаг не будет пройден.
    """

    def __init__(self, token, group_id):
        """
        :param token: group_id из группы vk
        :param group_id: секретный токен
        """
        self.group_id = GROUP_ID
        self.token = TOKEN
        self.vk = vk_api.VkApi(token=TOKEN)
        self.long_poller = VkBotLongPoll(self.vk, self.group_id)
        self.api = self.vk.get_api()
        self.user_states = dict()  # user_id -> UserState

    def run(self):
        """Запуск бота."""
        for event in self.long_poller.listen():
            try:
                self.on_event(event)
            except Exception as err:
                log.exception("Ошибка в обработке события")

    def on_event(self, event):
        """Отправляет сообщение назад, если это сообщение текст.

        :param event: VkBotMessageEvent object
        :return: None
        """
        if event.type != VkBotEventType.MESSAGE_NEW:
            log.info("мы пока не умеем обрабатывать событие такого типа %s", event.type)
            return
        user_id = event.message.peer_id
        text = event.message.text
        if user_id in self.user_states:
            text_to_send = self.continue_scenario(user_id, text)
        else:
            # search intent
            for intent in scenarios.INTENTS:
                log.debug(f'User gets {intent}')
                if any(token in text for token in intent['tokens']):
                    if intent['answer']:
                        text_to_send = intent['answer']
                    else:
                        text_to_send = self.start_scenario(user_id, intent['scenario'])
                    break
            else:
                text_to_send = scenarios.DEFAULT_ANSWER
        self.api.messages.send(
            message=text_to_send,
            random_id=random.randint(0, 2 ** 20),
            peer_id=user_id
        )

    def start_scenario(self, user_id, scenario_name):
        scenario = scenarios.SCENARIOS[scenario_name]
        first_step = scenario['first_step']
        step = scenario['steps'][first_step]
        text_to_send = step['text']
        self.user_states[user_id] = UserState(scenario_name=scenario_name, step_name=first_step)
        return text_to_send

    def continue_scenario(self, user_id, text):
        state = self.user_states[user_id]
        steps = scenarios.SCENARIOS[state.scenario_name]['steps']
        step = steps[state.step_name]
        handler = getattr(handlers, step['handler'])
        if handler(text=text, context=state.context):
            # next step
            next_step = steps[step['next_step']]
            text_to_send = next_step['text'].format(**state.context)
            if next_step['next_step']:
                # switch to next step
                state.step_name = step['next_step']
            else:
                # finish scenario
                log.info(f'Зарегистрирован: {text} {text}'.format(**state.context))
                self.user_states.pop(user_id)
        else:
            # retry current step
            text_to_send = step['failure_text'].format(**state.context)

        return text_to_send


if __name__ == "__main__":
    configure_logging()
    bot = Bot(GROUP_ID, TOKEN)
    bot.run()
