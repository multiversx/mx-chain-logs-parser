from enum import Enum
from reportlab.lib import colors

origin_shard = "origin_shard"
dest_shard = "dest_shard"
meta = "meta"
proposed = "proposed"
committed = "committed"

MiniBlockTypes = Enum("MiniBlockType", [
    'MiniBlockHeaders',
    'ShardInfo',
    'ExecutionResults'
])

MentionType = Enum("MentionType", [
    # miniblock is mentioned in origin shard header
    "origin_shard_proposed",
    "origin_shard_committed",

    # notarization of shard miniblock when meta includes the shard header
    "meta_origin_shard_proposed",
    "meta_origin_shard_committed",

    # miniblock is mentioned in destination shard header
    "dest_shard_proposed",
    "dest_shard_committed",

    # notarization of shard miniblock when meta includes the shard header
    "meta_dest_shard_proposed",
    "meta_dest_shard_committed",

    # miniblock is mentioned in an execution result, either on origin or destination shard
    "exec_proposed",
    "exec_committed",

    # notarization of execution results when meta includes the header containing the execution result
    "meta_exec_proposed",
    "meta_exec_committed",
])

# Mappings from field number to field name for MiniBlockHeaderReserved
FIELD_NAME_MAPPING = {
    1: "ExecutionType",
    2: "State",
    3: "IndexOfFirstTxProcessed",
    4: "IndexOfLastTxProcessed",
}

# Mappings for enum values from block.proto
PROCESSING_TYPE_MAPPING = {
    0: "Normal",
    1: "Scheduled",
    2: "Processed",
}

# Mappings for miniblock state enum values from block.proto
MINIBLOCK_STATE_MAPPING = {
    0: "Final",
    1: "Proposed",
    2: "PartialExecuted",
}

COLORS_MAPPING = {
    "origin_proposed": colors.lightyellow,
    "origin_partial_executed": colors.orange,
    "origin_final": colors.yellow,
    "dest_proposed": colors.mistyrose,
    "dest_partial_executed": colors.palevioletred,
    "dest_final": colors.pink,
    "meta_origin_committed": colors.lightgreen,
    "meta_dest_committed": colors.lightblue,
}
