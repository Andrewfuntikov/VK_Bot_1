from _token import token, group_id
from vk_api.bot_longpoll import VkBotLongPoll
import vk_api
import random


class Bot:
    def __init__(self, token, group_id):
        self.group_id = group_id
        self.token = token
        self.vk = vk_api.VkApi(token=token)
        self.long_poller = vk_api.bot_longpoll.VkBotLongPoll(self.vk, self.group_id)
        self.api = self.vk.get_api()

    def run(self):
        for event in self.long_poller.listen():
            try:
                self.on_event(event)
            except Exception as err:
                print(err)

    def on_event(self, event):
        if event.type == vk_api.bot_longpoll.VkBotEventType.MESSAGE_NEW:
            # message = event.obj['message']
            # text = message['text']
            # Разобраться в ошибке
            self.api.messages.send(
                message=event.object.text,
                random_id=random.randint(0, 2 ** 20),
                peer_id=event.object.peer_id
            )
        else:
            print(f'Мы пока не умеем обрабатывать события такого типа {event.type}')



if __name__ == "__main__":
    bot = Bot(token, group_id)
    bot.run()
