from enum import Enum


class FLOW_STATUS(Enum):
    PENDING = "pending"
    SUCCESS = "success"
    ERROR = "error"


class DATA_TYPE(Enum):
    INTEGER = "INT"
    STRING = "STR"
    BOOLEAN = "BOOL"
    FLOAT = "FLOAT"
    LIST = "LIST"
    SET = "SET"
    TUPLE = "TUPLE"
    DICTIONARY = "DICT"
    ANY = "ANY"
    NONE = "NONE"
