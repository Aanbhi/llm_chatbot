class ChatMemory:
    def __init__(self):
        self.history = []

    def add_message(self, role, content):
        self.history.append({"role": role, "content": content})

    def clear(self):
        self.history = []

    def get_history(self):
        return self.history