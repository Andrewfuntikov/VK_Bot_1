from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import vk_api
import random
import logging

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


class Bot:
    """
    Echo bot для vk.com.

    Use: python 3.12.3
    """

    def __init__(self, token, group_id):
        """
        :param token: group_id из группы vk
        :param group_id: секретный токен
        """
        self.group_id = group_id
        self.token = token
        self.vk = vk_api.VkApi(token=token)
        self.long_poller = VkBotLongPoll(self.vk, self.group_id)
        self.api = self.vk.get_api()

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
        if event.type == VkBotEventType.MESSAGE_NEW:
            log.debug("Отправляем сообщение назад")
            self.api.messages.send(
                message=event.message.text,
                random_id=random.randint(0, 2 ** 20),
                peer_id=event.message.peer_id
            )
        else:
            log.info(f'Мы пока не умеем обрабатывать события такого типа {event.type}')


if __name__ == "__main__":
    configure_logging()
    bot = Bot(settings.GROUP_ID, settings.TOKEN)
    bot.run()
