
class Person(object):
    """Contains annotation details for a person"""

    def __init__(self, name="", pid=0):
        super(Person, self).__init__()
        self.name = name
        self.id = pid

    def toDict(self):
        return dict(name=self.name,  id=self.id)

    @staticmethod
    def fromDict(person_data):
        # Here we could discriminate how the dict is read, depending
        # on the message's version used.
        if not person_data.has_key("version") or float(person_data["version"]) > 0:
            # name : str
            # id : int
            return Person(person_data["aldebaran:name"] if person_data.has_key("aldebaran:name") else "",
                int(person_data["aldebaran:id"]) if person_data.has_key("aldebaran:id") else 0)

    @property
    def version(self):
        return 0.1
