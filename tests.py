from copy import deepcopy
from unittest import TestCase
from unittest.mock import patch, Mock, ANY
from generate_ticket import generate_ticket
from pony.orm import db_session, rollback
from vk_api.bot_longpoll import VkBotMessageEvent, VkBotEvent
from bot import Bot
import settings


def isolate_db(test_func):
    def wrapper(*args, **kwargs):
        with db_session as session:
            test_func(*args, **kwargs)
            rollback()

    return wrapper()


class Test1(TestCase):
    RAW_EVENT = {'group_id': 226178386,
                 'type': 'message_new',
                 'event_id': 'd19c88fddb2b18134cd345aff6a0f45cdbf3d111',
                 'v': '5.199',
                 'object': {
                     'message': {'date': 1718004277, 'from_id': 838672463, 'id': 114, 'out': 0, 'version': 10000268,
                                 'attachments': [], 'conversation_message_id': 108, 'fwd_messages': [],
                                 'important': False, 'is_hidden': False, 'peer_id': 838672463, 'random_id': 0,
                                 'text': 'авапвпва'},
                     'client_info': {
                         'button_actions': ['text', 'vkpay', 'open_app', 'location', 'open_link', 'callback',
                                            'intent_subscribe', 'intent_unsubscribe'],
                         'keyboard': True, 'inline_keyboard': True, 'carousel': True, 'lang_id': 0}}}

    def test_run(self):
        count = 5
        obj = {'a': 1}
        events = [{'a': 1}] * count
        long_poller_mock = Mock(return_value=events)
        long_poller_listen_mock = Mock()
        long_poller_listen_mock.listen = long_poller_mock
        with patch('bot.vk_api.VkApi'):
            with patch('bot.VkBotLongPoll', return_value=long_poller_listen_mock):
                bot = Bot('', '')
                bot.on_event = Mock()
                bot.run()
                bot.on_event.assert_called()
                bot.on_event.assert_called_with(obj)
                assert bot.on_event.call_count == count

    INPUTS = [
        'Привет',
        'А когда?',
        'Где будет конференция?',
        'Зарегистрируй меня',
        'Венеамин',
        'мой адрес email@email',
        'email@email.ru'
    ]
    EXPECTED_OUTPUTS = [
        settings.DEFAULT_ANSWER,
        settings.INTENTS[0]['answer'],
        settings.INTENTS[1]['answer'],
        settings.SCENARIOS['registration']['steps']['step1']['text'],
        settings.SCENARIOS['registration']['steps']['step2']['text'],
        settings.SCENARIOS['registration']['steps']['step2']['failure_text'],
        settings.SCENARIOS['registration']['steps']['step3']['text'].format(name='Венеамин', email='email@email.ru')
    ]

    @isolate_db
    def test_run_ok(self):
        send_mock = Mock()
        api_mock = Mock()
        api_mock.messages.send = send_mock

        events = []
        for input_text in self.INPUTS:
            event = deepcopy(self.RAW_EVENT)
            event['object']['message']['text'] = input_text
            events.append(VkBotEvent(event))

        long_poller_mock = Mock()
        long_poller_mock.listen = Mock(return_value=events)

        with patch('bot.VkBotLongPoll', return_value=long_poller_mock):
            bot = Bot('', '')
            bot.api = api_mock
            bot.run()
        assert send_mock.call_count == len(self.INPUTS)

        real_outputs = []
        for call in send_mock.call_args_list:
            args, kwargs = call
            real_outputs.append(kwargs['message'])
        assert real_outputs == self.EXPECTED_OUTPUTS

    def test_image_generation(self):
        with open('files/ticket-example.jpg', 'rb') as avatar_file:
            avatar_mock = Mock()
            avatar_mock.content = avatar_file.read()
        with patch('requests.get', return_value=avatar_mock):
            ticket_file = generate_ticket('Qwe', 'Asd')
        with open('files/ticket-example.png', 'rb') as excpected_file:
            excpected_bytes = excpected_file.read()
        assert ticket_file.read() == excpected_bytes
