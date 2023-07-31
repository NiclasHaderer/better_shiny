class Value:
    # TODO bind a reactive value to a websocket connection, so if the websocket connectition
    #  is closed, the value is destroyed and no re-renders are triggered
    # TODO: track where the value is used, and re-render on update. Also make sure that the
    #  value is only used in a function that is decorated with @dynamic

    def __init__(self, value):
        self._value = value
        self._assert_correct_call_site()

    @staticmethod
    def _assert_correct_call_site() -> None:
        """
        This makes sure that the value constructor is only called in a function that is decorated with @dynamic
        """
        import inspect

        # We know that the call site is 3 frames up the stack
        frame = inspect.currentframe().f_back.f_back.f_back
        # Check that the name is inner_function_executor_0_0_
        if frame.f_code.co_name != "inner_function_executor_0_0_":
            raise ValueError(
                "Value constructor can only be called in a function that is decorated with @dynamic"
            )

    def __call__(self):
        return self._value

    def set(self, value):
        self._value = value

    def __repr__(self):
        return self._value.__repr__()
