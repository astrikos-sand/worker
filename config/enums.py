from strenum import StrEnum


class SUBMIT_TASK_TYPE(StrEnum):
    NORMAL = "NORMAL"
    TRIGGERED = "TRIGGERED"


class SLOT_ATTACHMENT_TYPE(StrEnum):
    INPUT = "IN"
    OUTPUT = "OUT"


class SLOT_SPECIALITY(StrEnum):
    DATABASE = "DB"
    API = "API"
    BACKEND = "BACKEND"
    NODE_ID = "NODE_ID"
    SIGNAL = "SIG"
    TB = "TB"
    TB_QUEUE = "TBQ"
    DB_CONNECTOR = "DB_CONNECTOR"
    NONE = "NONE"


class DATA_TYPE(StrEnum):
    INTEGER = ("INT",)
    STRING = ("STR",)
    BOOLEAN = ("BOOL",)
    FLOAT = ("FLOAT",)
    LIST = ("LIST",)
    SET = ("SET",)
    TUPLE = ("TUPLE",)
    DICTIONARY = "DICT"
    NONE = "NONE"


class NODE_ENUM(StrEnum):
    DATA_NODE = "DataNode"
    GENERIC_NODE = "GenericNode"


class NODE_CLASS_ENUM(StrEnum):
    GENERIC_NODE_CLASS = "GenericNodeClass"
    TRIGGER_NODE_CLASS = "TriggerNodeClass"
