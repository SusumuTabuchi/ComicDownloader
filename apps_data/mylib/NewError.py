
class NewSizeError(Exception):
    def __init__(self):
        pass

    def __str__ (self, size):
        return ("New Size Error. size is [{0}].".format(size))
