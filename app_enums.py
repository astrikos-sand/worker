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
    SIGNAL = "SIG"
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


class NODE_ENUM(StrEnum):
    DATA_NODE = "DataNode"
    GENERIC_NODE = "GenericNode"


class NODE_CLASS_ENUM(StrEnum):
    GENERIC_NODE_CLASS = "GenericNodeClass"
    TRIGGER_NODE_CLASS = "TriggerNodeClass"
