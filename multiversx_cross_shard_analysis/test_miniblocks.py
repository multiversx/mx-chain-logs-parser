from enum import Enum
import json
from multiversx_cross_shard_analysis.header_structures import Header, HeaderData, ShardData

from multiversx_cross_shard_analysis.miniblock_data import MiniblockData

header = {
    "blockBodyType": 0,
    "chainID": "31",
    "epoch": 2,
    "epochStartMetaHash": "",
    "executionResults": [
        {
            "accumulatedFees": "0",
            "baseExecutionResult": {
                "gasUsed": 0,
                "headerEpoch": 2,
                "headerHash": "be0081efbafed4be3738cdd02ab358a20e8e16f83bfe4b4d7858cfb868366f6b",
                "headerNonce": 1647,
                "headerRound": 1647,
                "rootHash": "a55990c083e7868a6f567bfa3fa6ec9fa017f5eda34ee2b667ef7e55290d8259"
            },
            "developerFees": "0",
            "executedTxCount": 0,
            "miniBlockHeaders": [],
            "receiptsHash": "0e5751c026e543b2e8ab2eb06099daa1d1e5df47778f7787faab45cdf12fe3a8"
        }
    ],
    "gasLimit": 0,
    "lastExecutionResult": {
        "executionResult": {
            "gasUsed": 0,
            "headerEpoch": 0,
            "headerHash": "be0081efbafed4be3738cdd02ab358a20e8e16f83bfe4b4d7858cfb868366f6b",
            "headerNonce": 1647,
            "headerRound": 1647,
            "rootHash": "a55990c083e7868a6f567bfa3fa6ec9fa017f5eda34ee2b667ef7e55290d8259"
        },
        "notarizedInRound": 1648
    },
    "leaderSignature": "f25f5ffa015cb16b4173a17742142e6e7435999b3477cec0320c8892c92e72015453331a8c9c707a03d922f3514c7f0a",
    "metaBlockHashes": [
        "ff0c0da960b7a41b7e3b4c6f702b427bcb493fb963dcce35074fa8ecb1391608"
    ],
    "miniBlockHeaders": [
        {
            "hash": "52af8b3c899198e823ef94c80fc12cc4ba301e005d8e67f615ba872226a4963c",
            "receiverShardID": 0,
            "reserved": "1001",
                        "senderShardID": 0,
                        "txCount": 809,
                        "type": 0
        }
    ],
    "nonce": 1648,
    "peerChanges": [],
    "prevHash": "be0081efbafed4be3738cdd02ab358a20e8e16f83bfe4b4d7858cfb868366f6b",
    "prevRandSeed": "b6e86481e0751eaf68c6505382ba783c028b837dbcb7c76db19ef14ec7df3d4a6268d161e7fe743c71473ccb89095691",
    "randSeed": "018187ce3f41e8f126f8f2f3c336e98417faac23fc96a0d856ab04db20d4fcc58c632f94a6d8ff349eef42de47b82792",
    "receiptsHash": "",
    "reserved": "",
    "round": 1648,
    "shardID": 0,
    "softwareVersion": "33",
    "timestampMs": 1765297076800,
    "txCount": 809
}

header_exec_result = {
    "blockBodyType": 0,
    "chainID": "31",
    "epoch": 2,
    "epochStartMetaHash": "",
    "executionResults": [
        {
            "accumulatedFees": "46517500000000000",
            "baseExecutionResult": {
                "gasUsed": 46517500,
                "headerEpoch": 2,
                "headerHash": "afbd732a8d4842a2bd6fc1edd466b1f8d8b67cbf8737301c83d9cde03f0e7cf0",
                "headerNonce": 1648,
                "headerRound": 1648,
                "rootHash": "ca61fd6e23ff56a5c58016afd83d810b0fa77b1e39b945b2432696c73458ebf3"
            },
            "developerFees": "0",
            "executedTxCount": 809,
            "miniBlockHeaders": [
                {
                    "hash": "4df428a4f8c34e62382d7bdbec08749188049959131c2acbd514edff1890b28e",
                    "receiverShardID": 1,
                    "reserved": "20a806",
                    "senderShardID": 0,
                    "txCount": 809,
                    "type": 0
                }
            ],
            "receiptsHash": "0e5751c026e543b2e8ab2eb06099daa1d1e5df47778f7787faab45cdf12fe3a8"
        }
    ],
    "gasLimit": 0,
    "lastExecutionResult": {
        "executionResult": {
            "gasUsed": 46517500,
            "headerEpoch": 0,
            "headerHash": "afbd732a8d4842a2bd6fc1edd466b1f8d8b67cbf8737301c83d9cde03f0e7cf0",
            "headerNonce": 1648,
            "headerRound": 1648,
            "rootHash": "ca61fd6e23ff56a5c58016afd83d810b0fa77b1e39b945b2432696c73458ebf3"
        },
        "notarizedInRound": 1649
    },
    "leaderSignature": "929e5b34dd6ae016deeab2667b67b41baccda435c01d5ad89c9b56b92db6fc526fe3f7d30ba043878ab091bfe7836392",
    "metaBlockHashes": [
        "b782177d39d7495558992faed007536df77f576ed790d7117162a732ebcabd6a"
    ],
    "miniBlockHeaders": [
        {
            "hash": "994ceb37eb426a123501928c8c5b67e59f607557fb5f332d5e55fd297ab5d870",
            "receiverShardID": 0,
            "reserved": "1001",
                        "senderShardID": 0,
                        "txCount": 1610,
                        "type": 0
        }
    ],
    "nonce": 1649,
    "peerChanges": [],
    "prevHash": "afbd732a8d4842a2bd6fc1edd466b1f8d8b67cbf8737301c83d9cde03f0e7cf0",
    "prevRandSeed": "018187ce3f41e8f126f8f2f3c336e98417faac23fc96a0d856ab04db20d4fcc58c632f94a6d8ff349eef42de47b82792",
    "randSeed": "1cefd79bab2fafda3ad83f665fd9aef5840b0736d3cf61dc2e5bc227dec81d3122b847ccf13289484bb15a2141e1ff08",
    "receiptsHash": "",
    "reserved": "",
    "round": 1649,
    "shardID": 0,
    "softwareVersion": "33",
    "timestampMs": 1765297077400,
    "txCount": 1610
}


class TestMiniBlockHeader:
    def test_header_data(self):
        header_data = HeaderData()
        header_data.add_commited_header(header_exec_result)
        assert header_data.header_dictionary['commited_headers'][0] == header_exec_result

        header_data.add_proposed_header(header_exec_result)
        assert header_data.header_dictionary['proposed_headers'][0] == header_exec_result

    def test_header(self):
        header_instance = Header(header_exec_result, 'commited')
        assert header_instance.metadata['epoch'] == 2
        assert header_instance.metadata['round'] == 1649
        assert header_instance.metadata['shard_id'] == 0
        assert header_instance.metadata['nonce'] == 1649
        assert header_instance.isHeaderV3(header_exec_result) is True
        assert len(header_instance.miniblocks) == 2

        for mention_type, miniblock, metadata in header_instance.miniblocks:
            assert mention_type in ["origin_shard_commited", "origin_shard_commited_exec"]
            if mention_type == "origin_shard_commited":
                assert miniblock['hash'] == "994ceb37eb426a123501928c8c5b67e59f607557fb5f332d5e55fd297ab5d870"
                assert metadata['nonce'] == 1649
            elif mention_type == "origin_shard_commited_exec":
                assert miniblock['hash'] == "4df428a4f8c34e62382d7bdbec08749188049959131c2acbd514edff1890b28e"
                assert metadata['nonce'] == 1648

    def test_shard_data(self):
        header_data = HeaderData()
        header_data.add_commited_header(header_exec_result)
        header_data.add_proposed_header(header_exec_result)
        shard_data = ShardData()
        shard_data.add_node(header_data)
        assert shard_data.parsed_headers[0].header_dictionary['commited_headers'][0] == header_exec_result
        assert shard_data.parsed_headers[0].header_dictionary['proposed_headers'][0] == header_exec_result
        assert len(shard_data.miniblocks) == 2  # two miniblocks in the header

    def test_nonce_timeline(self):
        header_data = HeaderData()

        header_data.add_commited_header(header)
        header_data.add_proposed_header(header)

        header_data.add_commited_header(header_exec_result)
        header_data.add_proposed_header(header_exec_result)

        shard_data = ShardData()
        shard_data.add_node(header_data)

        print("Miniblocks data:")
        print(json.dumps(shard_data.miniblocks, indent=4))

        timeline = shard_data.get_data_for_header_horizontal_report()
        assert len(timeline) == 1  # one epoch

        print("Timeline data:")
        print(json.dumps(timeline, indent=4, default=lambda o: o.name if isinstance(o, Enum) else str(o)))

    def test_nonce_timeline_new(self):
        header_data = HeaderData()

        header_data.add_commited_header(header)
        header_data.add_proposed_header(header)

        header_data.add_commited_header(header_exec_result)
        header_data.add_proposed_header(header_exec_result)

        shard_data = ShardData()
        shard_data.add_node(header_data)

        miniblock_data = MiniblockData(shard_data.miniblocks)
        print("Miniblocks data:")
        print(json.dumps(miniblock_data.miniblocks, indent=4))

        timeline = miniblock_data.get_data_for_header_report()

        print("Timeline data:")
        print(json.dumps(timeline, indent=4, default=lambda o: o.name if isinstance(o, Enum) else str(o)))

    def test_miniblock_data_verify(self):
        header_data = HeaderData()

        header_data.add_commited_header(header)
        header_data.add_proposed_header(header)

        header_data.add_commited_header(header_exec_result)
        header_data.add_proposed_header(header_exec_result)

        shard_data = ShardData()
        shard_data.add_node(header_data)

        miniblock_data = MiniblockData(shard_data.miniblocks)
        print("Miniblocks data:")
        print(json.dumps(miniblock_data.miniblocks, indent=4))
