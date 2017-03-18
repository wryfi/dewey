

class SecretAccessDecorator(object):
    """
    Decorator to check whether a user should be granted access to modify a
    secret. Assumes that 'name' and 'safe' will be passed as kwargs,
    referring to the name of the secret and name of its safe, respectively.
    """

    def __init__(self, view):
        self.view = view

    def __call__(self):
        pass
