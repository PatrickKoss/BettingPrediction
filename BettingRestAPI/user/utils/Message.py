class Message:
    def __init__(self, messageType, message):
        self.messageType = messageType
        self.message = message
        if self.messageType != "success" and self.messageType != "error":
            self.messageType = "success"

    def repr_json(self):
        return dict(messageType=self.messageType, message=self.message)
