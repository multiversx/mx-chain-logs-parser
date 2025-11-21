from multiversx_cross_shard_analysis.decode_reserved import decode_reserved_field


mentioned_headers = {
    "origin_shard_proposed_headers": "20ec12",
    "origin_shard_commited_headers": "20ec12",
    "dest_shard_proposed_headers_1": "1002208112",
    "dest_shard_proposed_headers_2": "18821220ec12",
    "dest_shard_commited_headers_1": "1002208112",
    "dest_shard_commited_headers_2": "18821220ec12",
    "meta_origin_shard_proposed_headers": "08011002208112",
    "meta_dest_shard_proposed_headers": "08011002180a208112",
    "meta_dest_shard_commited_headers": "",
}

expected = {
    "origin_shard_proposed_headers": {
        "ExecutionType": "Normal",
        "State": "Final",
        "IndexOfFirstTxProcessed": 0,
        "IndexOfLastTxProcessed": 2412
    },
    "origin_shard_commited_headers": {
        "ExecutionType": "Normal",
        "State": "Final",
        "IndexOfFirstTxProcessed": 0,
        "IndexOfLastTxProcessed": 2412
    },
    "dest_shard_proposed_headers_1": {
        "ExecutionType": "Normal",
        "State": "PartialExecuted",
        "IndexOfFirstTxProcessed": 0,
        "IndexOfLastTxProcessed": 2305
    },
    "dest_shard_proposed_headers_2": {
        "ExecutionType": "Normal",
        "State": "Final",
        "IndexOfFirstTxProcessed": 2306,
        "IndexOfLastTxProcessed": 2412
    },
    "dest_shard_commited_headers_1": {
        "ExecutionType": "Normal",
        "State": "PartialExecuted",
        "IndexOfFirstTxProcessed": 0,
        "IndexOfLastTxProcessed": 2305
    },
    "dest_shard_commited_headers_2": {
        "ExecutionType": "Normal",
        "State": "Final",
        "IndexOfFirstTxProcessed": 2306,
        "IndexOfLastTxProcessed": 2412
    },
    "meta_origin_shard_proposed_headers": {
        "ExecutionType": "Scheduled",
        "State": "PartialExecuted",
        "IndexOfFirstTxProcessed": 0,
        "IndexOfLastTxProcessed": 2305
    },
    "meta_dest_shard_proposed_headers": {
        "ExecutionType": "Scheduled",
        "State": "PartialExecuted",
        "IndexOfFirstTxProcessed": 10,
        "IndexOfLastTxProcessed": 2305
    },
    "meta_dest_shard_commited_headers": {
        "ExecutionType": "Normal",
        "State": "Final",
        "IndexOfFirstTxProcessed": 0,
        "IndexOfLastTxProcessed": 2412
    }
}


class TestMiniBlockHeader:
    def test_get_processing_type1(self):
        for name, hex_str in mentioned_headers.items():
            assert decode_reserved_field(hex_str, 2413) == expected[name], f"Decoding failed for {name}"
