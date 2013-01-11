class Docx2HtmlException(Exception):
    pass


class InvalidFileExtension(Docx2HtmlException):
    pass


class ConversionFailed(Docx2HtmlException):
    pass
