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
    "origin_exec_proposed",
    "origin_exec_committed",

    # miniblock is mentioned in an execution result, either on origin or destination shard
    "dest_exec_proposed",
    "dest_exec_committed",

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

# type names
TYPE_NAMES = {
    0: "TxBlock",
    30: "StateBlock",
    60: "PeerBlock",
    90: "SCResultBlock",
    120: "InvalidBlock",
    150: "ReceiptBlock",
    255: "RewardsBlock",
}

Colors = Enum("Colors", [
    "origin_proposed",
    "origin_partial_executed",
    "origin_final",
    "dest_proposed",
    "dest_partial_executed",
    "dest_final",
    "meta_origin_committed",
    "meta_dest_committed",
])

COLORS_MAPPING = {
    Colors.origin_proposed: colors.lightyellow,
    Colors.origin_partial_executed: colors.orange,
    Colors.origin_final: colors.yellow,
    Colors.dest_proposed: colors.mistyrose,
    Colors.dest_partial_executed: colors.palevioletred,
    Colors.dest_final: colors.pink,
    Colors.meta_origin_committed: colors.lightgreen,
    Colors.meta_dest_committed: colors.lightblue,
}
