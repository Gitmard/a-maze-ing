class InvalidConfigException(ValueError):
    def __init__(self, message: str) -> None:
        super().__init__(f"Invalid Config: {message}")
