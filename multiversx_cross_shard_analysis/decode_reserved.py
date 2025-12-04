
from typing import Any

from multiversx_cross_shard_analysis.constants import (FIELD_NAME_MAPPING,
                                                       MINIBLOCK_STATE_MAPPING,
                                                       PROCESSING_TYPE_MAPPING)


def get_default_decoded_data(tx_count: int) -> dict[str, Any]:
    """
    Returns a dictionary with the default values for the MiniBlockHeaderReserved struct.
    """
    return {
        "ExecutionType": "Normal",
        "State": "Final",
        "IndexOfFirstTxProcessed": 0,
        "IndexOfLastTxProcessed": tx_count - 1 if tx_count > 0 else 0,
    }


def decode_reserved_field(hex_string: str, tx_count: int) -> dict[str, Any]:
    """
    Decodes the reserved field from a hex string into a human-readable dictionary,
    including default values for missing fields.
    """
    decoded_data = get_default_decoded_data(tx_count)

    if not hex_string:
        return {}

    byte_data = bytes.fromhex(hex_string)
    i = 0
    while i < len(byte_data):
        field_and_type = byte_data[i]
        field_number = field_and_type >> 3
        wire_type = field_and_type & 0x07
        i += 1

        if wire_type == 0:  # Varint
            value = 0
            shift = 0
            while True:
                if i >= len(byte_data):
                    decoded_data["error"] = "Incomplete varint data"
                    return decoded_data
                byte = byte_data[i]
                value |= (byte & 0x7F) << shift
                i += 1
                if not (byte & 0x80):
                    break
                shift += 7

            field_name = FIELD_NAME_MAPPING.get(field_number, f"UnknownField_{field_number}")

            if field_name == "ExecutionType":
                decoded_data[field_name] = PROCESSING_TYPE_MAPPING.get(value, f"UnknownProcessingType_{value}")
            elif field_name == "State":
                decoded_data[field_name] = MINIBLOCK_STATE_MAPPING.get(value, f"UnknownState_{value}")
            else:
                decoded_data[field_name] = value

        else:
            decoded_data["error"] = f"Unsupported wire type: {wire_type}"
            break

    return decoded_data
