from enum import Enum


class SignatureTypeEnum(Enum):
    """
    Enum representing different types of electronic signatures.
    """
    SIMPLE = "Simple"
    ADVANCED = "Advanced"
    QUALIFIED = "Qualified"