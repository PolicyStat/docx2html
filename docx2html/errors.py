class Docx2HtmlException(Exception):
    pass


class InvalidFileExtension(Docx2HtmlException):
    pass


class ConversionFailed(Docx2HtmlException):
    pass


class MissingConverter(Docx2HtmlException):
    pass
