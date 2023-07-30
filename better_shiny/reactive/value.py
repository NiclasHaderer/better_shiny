class Value:
    # TODO bind a reactive value to a websocket connection, so if the websocket connectition
    #  is closed, the value is destroyed and no re-renders are triggered
    # TODO: track where the value is used, and re-render on update. Also make sure that the
    #  value is only used in a function that is decorated with @dynamic

    def __init__(self, value):
        self._value = value

    def __call__(self):
        return self._value

    def set(self, value):
        self._value = value

    def __repr__(self):
        return self._value.__repr__()
