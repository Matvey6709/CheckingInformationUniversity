class Direction:
    def __init__(self, name, form, num_pr, Users=[]):
        self.name = name
        self.form = form
        self.num_pr = num_pr
        self.Users = Users

    def getInfo(self):
        return f'{self.name} {self.form} {self.num_pr}'

    def getNmberInThelist(self, id):
        i = 0
        for user in self.Users:
            if int(user.priority) == 1 and user.is_document:
                i += 1
            if int(user.id) == id:
                return i
        return -1
    def getUser(self, id):
        for user in self.Users:
            if int(user.id) == id:
                return user
        return -1