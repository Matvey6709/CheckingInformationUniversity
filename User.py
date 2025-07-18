class User:
    def __init__(self, id, number_list, is_document, priority):
        self.id = id
        self.number_list = number_list
        self.is_document = is_document
        self.priority = priority
    def getInfo(self):
        return f'{self.number_list} {self.id} {self.is_document} {self.priority}'