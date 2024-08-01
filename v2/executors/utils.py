from ast import literal_eval

from v2.mappings import DATA_TYPE


def get_data(data_type, value):
    match data_type:
        case DATA_TYPE.INTEGER.value:
            return int(value)

        case DATA_TYPE.STRING.value:
            return str(value)

        case DATA_TYPE.BOOLEAN.value:
            if value.lower() == "true":
                return True
            return False

        case DATA_TYPE.FLOAT.value:
            return float(value)

        case DATA_TYPE.LIST.value:
            value = literal_eval(value)
            if type(value) is not list:
                raise f"Invalid type of data node, given list but got {type(value)}"
            return value

        case DATA_TYPE.SET.value:
            value = literal_eval(value)
            if type(value) is not set:
                raise f"Invalid type of data node, given set but got {type(value)}"
            return value

        case DATA_TYPE.TUPLE.value:
            value = literal_eval(value)
            if type(value) is not tuple:
                raise f"Invalid type of data node, given tuple but got {type(value)}"
            return value

        case DATA_TYPE.DICTIONARY.value:
            value = literal_eval(value)
            if type(value) is not dict:
                raise f"Invalid type of data node, given dict but got {type(value)}"
            return value

        case DATA_TYPE.NONE.value:
            return None

        case DATA_TYPE.ANY.value:
            return value
