class Error(Exception):
    def __init__(self, message=None, *args, **kwargs):
        self.message = message
        super(Error, self).__init__(*args, **kwargs)
