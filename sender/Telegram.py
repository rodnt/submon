import requests
requests.packages.urllib3.disable_warnings()

class Telegram:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id

    def send(self, message):
        url = f'https://api.telegram.org/bot{self.token}/sendMessage'
        data = {'chat_id': self.chat_id, 'text': message}
        requests.post(url, data=data)

    def send_file(self, file_path):
        url = f'https://api.telegram.org/bot{self.token}/sendDocument'
        with open(file_path, 'rb') as file:
            files = {'document': file}
            data = {'chat_id': self.chat_id}
            requests.post(url, files=files, data=data)
