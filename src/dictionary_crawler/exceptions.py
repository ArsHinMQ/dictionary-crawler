class DictionaryException(Exception):
    pass


class DictionaryFetchException(DictionaryException):
    def __init__(self, message: str = "", url: str = "", status_code: int | None = None):
        self.url = url
        self.status_code = status_code
        super().__init__(message or f"Fetch failed (status={status_code}) for {url}")


class DictionaryWordNotFoundException(DictionaryException):
    def __init__(self, word: str):
        self.word = word
        super().__init__(f"Word not found: {word!r}")


class DictionaryParseException(DictionaryException):
    def __init__(self, message: str = "", word: str = "", detail: str = ""):
        self.word = word
        self.detail = detail
        super().__init__(message or f"Parsing failed for {word!r}: {detail}")


class CambridgeException(DictionaryException):
    pass


class CambridgeFetchException(DictionaryFetchException, CambridgeException):
    pass


class CambridgeWordNotFoundException(DictionaryWordNotFoundException, CambridgeException):
    pass


class CambridgeParseException(DictionaryParseException, CambridgeException):
    pass
