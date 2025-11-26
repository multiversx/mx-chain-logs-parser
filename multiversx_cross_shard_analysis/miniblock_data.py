import json
from typing import Any

from multiversx_cross_shard_analysis.constants import COLORS_MAPPING


class MiniblockData:

    def __init__(self, miniblocks: list[tuple[str, dict[str, Any]]]):
        self.miniblocks = miniblocks

    def get_data_for_round_report(self) -> dict[str, Any]:
        report = {}
        for mb_hash, mb_info in self.miniblocks:
            for mention_type, header in mb_info.get('mentioned', []):
                if "proposed" in mention_type:
                    continue

                epoch = header.get('epoch')
                if epoch not in report:
                    report[epoch] = {}
                round_number = header.get('round')
                if round_number not in report[epoch]:
                    report[epoch][round_number] = {}
                shard = header.get('shard_id')
                if shard not in report[epoch][round_number]:
                    report[epoch][round_number][shard] = []

                if header.get('reserved') == {}:
                    if "meta" in mention_type:
                        reserved = COLORS_MAPPING["meta_origin_committed"] if mention_type.startswith('meta_origin') else COLORS_MAPPING["meta_dest_committed"]
                    else:
                        reserved = COLORS_MAPPING["origin_final"] if mention_type.startswith('origin') else COLORS_MAPPING["dest_final"]
                else:
                    # execution_type = header.get('reserved', {}).get('ExecutionType', '')
                    state = header.get('reserved', {}).get('State', '')
                    if state == 'Proposed':
                        reserved = COLORS_MAPPING["origin_proposed"] if mention_type.startswith('origin') else COLORS_MAPPING["dest_proposed"]
                    elif state == 'PartialExecuted':
                        reserved = COLORS_MAPPING["origin_partial_executed"] if mention_type.startswith('origin') else COLORS_MAPPING["dest_partial_executed"]
                    else:
                        reserved = COLORS_MAPPING["origin_final"] if mention_type.startswith('origin') else COLORS_MAPPING["dest_final"]
                report[epoch][round_number][shard].append((mb_hash, reserved))
        return report

    def get_data_for_detailed_report(self) -> dict[str, Any]:
        report = {}

        for mb_hash, mb_info in self.miniblocks:
            if mb_info['senderShardID'] == mb_info['receiverShardID']:
                continue  # Skip same-shard miniblocks
            origin_epoch = None
            report_data = {
                'lanes': {
                    'origin': [],
                    'dest': [],
                    'meta': []
                }
            }
            for mention_type, header in mb_info.get('mentioned', []):
                lane = 'meta' if 'meta' in mention_type else ('origin' if 'origin' in mention_type else 'dest')
                report_data['lanes'][lane].append((mention_type, header.get('round')))
                if lane == 'origin':
                    origin_epoch = header.get('epoch')
            if not origin_epoch:
                print(f"Warning: origin_epoch not found for miniblock {mb_hash}")
                continue
            if origin_epoch not in report:
                report[origin_epoch] = {}
            report[origin_epoch][mb_hash] = report_data
        return report

    def get_data_for_detailed_report1(self) -> dict[str, Any]:
        report = {}

        for mb_hash, mb_info in self.miniblocks:
            if mb_info['senderShardID'] == mb_info['receiverShardID']:
                continue  # Skip same-shard miniblocks
            origin_epoch = None
            start_round = None
            end_round = None
            report_data = {
                'start_round': start_round,
                'end_round': end_round,
                'lanes': {
                    'origin': [],
                    'dest': [],
                    'meta': []
                }
            }
            for mention_type, header in mb_info.get('mentioned', []):
                lane = 'meta' if 'meta' in mention_type else ('origin' if 'origin' in mention_type else 'dest')
                report_data['lanes'][lane].append((mention_type, header.get('round')))
                if report_data['start_round'] is None or header.get('round') < report_data['start_round']:
                    report_data['start_round'] = header.get('round')
                if report_data['end_round'] is None or header.get('round') > report_data['end_round']:
                    report_data['end_round'] = header.get('round')
                if lane == 'origin':
                    origin_epoch = header.get('epoch')
            if not origin_epoch:
                print(f"Warning: origin_epoch not found for miniblock {mb_hash}")
                continue
            if origin_epoch not in report:
                report[origin_epoch] = {}

            report[origin_epoch][mb_hash] = report_data
        return report


if __name__ == "__main__":
    example = {"run_name": "cross-shard-execution-anal-9afe696daf", "miniblocks": {"01f7f0f3503c62b69ff0fe22a57b97eaa2f164ac9e4a0bb852bc66e3f5c12369": {"hash": "01f7f0f3503c62b69ff0fe22a57b97eaa2f164ac9e4a0bb852bc66e3f5c12369", "receiverShardID": 0, "reserved": "", "senderShardID": 1, "txCount": 1, "type": 0, "mentioned": [["dest_shard_proposed_headers", {"nonce": 207, "round": 207, "epoch": 1, "shard_id": 0}], ["dest_shard_commited_headers", {"nonce": 207, "round": 207, "epoch": 1, "shard_id": 0}], ["origin_shard_proposed_headers", {"nonce": 205, "round": 205, "epoch": 1, "shard_id": 1}], ["origin_shard_commited_headers", {"nonce": 205, "round": 205, "epoch": 1, "shard_id": 1}], ["meta_origin_shard_proposed_headers", {"nonce": 206, "round": 206, "epoch": 1, "shard_id": 4294967295}], ["meta_dest_shard_proposed_headers", {"nonce": 208, "round": 208, "epoch": 1, "shard_id": 4294967295}], ["meta_origin_shard_commited_headers", {"nonce": 206, "round": 206, "epoch": 1, "shard_id": 4294967295}], ["meta_dest_shard_commited_headers", {"nonce": 208, "round": 208, "epoch": 1, "shard_id": 4294967295}]]}, "3fce18121e1ce8e57a3d776c91468649699e8238fad7898f46b8ac88b8d2c1cb": {"hash": "3fce18121e1ce8e57a3d776c91468649699e8238fad7898f46b8ac88b8d2c1cb", "receiverShardID": 0, "reserved": "200b", "senderShardID": 0, "txCount": 12, "type": 0, "mentioned": [["origin_shard_proposed_headers", {"nonce": 210, "round": 210, "epoch": 1, "shard_id": 0}], ["origin_shard_commited_headers", {"nonce": 210, "round": 210, "epoch": 1, "shard_id": 0}], ["meta_origin_shard_proposed_headers", {"nonce": 211, "round": 211, "epoch": 1, "shard_id": 4294967295}], ["meta_origin_shard_commited_headers", {"nonce": 211, "round": 211, "epoch": 1, "shard_id": 4294967295}]]}, "cb2bbdf01dd1a44c813ceecb58ae7404ad9016073fc707dda1be52f7dc5735fc": {"hash": "cb2bbdf01dd1a44c813ceecb58ae7404ad9016073fc707dda1be52f7dc5735fc", "receiverShardID": 1, "reserved": "201c", "senderShardID": 0, "txCount": 29, "type": 0, "mentioned": [["origin_shard_proposed_headers", {"nonce": 210, "round": 210, "epoch": 1, "shard_id": 0}], ["origin_shard_commited_headers", {"nonce": 210, "round": 210, "epoch": 1, "shard_id": 0}], ["dest_shard_proposed_headers", {"nonce": 212, "round": 212, "epoch": 1, "shard_id": 1}], ["dest_shard_commited_headers", {"nonce": 212, "round": 212, "epoch": 1, "shard_id": 1}], ["meta_origin_shard_proposed_headers", {"nonce": 211, "round": 211, "epoch": 1, "shard_id": 4294967295}], ["meta_dest_shard_proposed_headers", {"nonce": 213, "round": 213, "epoch": 1, "shard_id": 4294967295}], ["meta_origin_shard_commited_headers", {"nonce": 211, "round": 211, "epoch": 1, "shard_id": 4294967295}], ["meta_dest_shard_commited_headers", {"nonce": 213, "round": 213, "epoch": 1, "shard_id": 4294967295}]]}, "01e7fc8132cd61f6aede3231bc9c9dc36dbe7d3ffcaca59fce7b46cca0e5884e": {"hash": "01e7fc8132cd61f6aede3231bc9c9dc36dbe7d3ffcaca59fce7b46cca0e5884e", "receiverShardID": 2, "reserved": "2008", "senderShardID": 0, "txCount": 9, "type": 0, "mentioned": [["origin_shard_proposed_headers", {"nonce": 210, "round": 210, "epoch": 1, "shard_id": 0}], ["origin_shard_commited_headers", {"nonce": 210, "round": 210, "epoch": 1, "shard_id": 0}], ["meta_origin_shard_proposed_headers", {"nonce": 211, "round": 211, "epoch": 1, "shard_id": 4294967295}], ["meta_dest_shard_proposed_headers", {"nonce": 213, "round": 213, "epoch": 1, "shard_id": 4294967295}], ["meta_origin_shard_commited_headers", {"nonce": 211, "round": 211, "epoch": 1, "shard_id": 4294967295}], ["meta_dest_shard_commited_headers", {"nonce": 213, "round": 213, "epoch": 1, "shard_id": 4294967295}], ["dest_shard_proposed_headers", {"nonce": 211, "round": 212, "epoch": 1, "shard_id": 2}], ["dest_shard_commited_headers", {"nonce": 211, "round": 212, "epoch": 1, "shard_id": 2}]]}, "f966a0d0370de9a7b0675ec153c03f61031e02864fe781ab49cca0f60439e590": {"hash": "f966a0d0370de9a7b0675ec153c03f61031e02864fe781ab49cca0f60439e590", "receiverShardID": 0, "reserved": "2012", "senderShardID": 2, "txCount": 19, "type": 0, "mentioned": [["dest_shard_proposed_headers", {"nonce": 212, "round": 212, "epoch": 1, "shard_id": 0}], ["dest_shard_commited_headers", {"nonce": 212, "round": 212, "epoch": 1, "shard_id": 0}], ["meta_origin_shard_proposed_headers", {"nonce": 211, "round": 211, "epoch": 1, "shard_id": 4294967295}], ["meta_dest_shard_proposed_headers", {"nonce": 213, "round": 213, "epoch": 1, "shard_id": 4294967295}], ["meta_origin_shard_commited_headers", {"nonce": 211, "round": 211, "epoch": 1, "shard_id": 4294967295}], ["meta_dest_shard_commited_headers", {"nonce": 213, "round": 213, "epoch": 1, "shard_id": 4294967295}], ["origin_shard_proposed_headers", {"nonce": 209, "round": 210, "epoch": 1, "shard_id": 2}], ["origin_shard_commited_headers", {"nonce": 209, "round": 210, "epoch": 1, "shard_id": 2}]]}, "cdac3609485d6813f79c717e48e5d6cf94b3ca6e25dd372a21f3511f0eb1e536": {"hash": "cdac3609485d6813f79c717e48e5d6cf94b3ca6e25dd372a21f3511f0eb1e536", "receiverShardID": 0, "reserved": "200e", "senderShardID": 1, "txCount": 15, "type": 0, "mentioned": [["dest_shard_proposed_headers", {"nonce": 212, "round": 212, "epoch": 1, "shard_id": 0}], ["dest_shard_commited_headers", {"nonce": 212, "round": 212, "epoch": 1, "shard_id": 0}], ["origin_shard_proposed_headers", {"nonce": 210, "round": 210, "epoch": 1, "shard_id": 1}], ["origin_shard_commited_headers", {"nonce": 210, "round": 210, "epoch": 1, "shard_id": 1}], ["meta_origin_shard_proposed_headers", {"nonce": 211, "round": 211, "epoch": 1, "shard_id": 4294967295}], ["meta_dest_shard_proposed_headers", {"nonce": 213, "round": 213, "epoch": 1, "shard_id": 4294967295}], ["meta_origin_shard_commited_headers", {"nonce": 211, "round": 211, "epoch": 1, "shard_id": 4294967295}], ["meta_dest_shard_commited_headers", {"nonce": 213, "round": 213, "epoch": 1, "shard_id": 4294967295}]]}}}
    mb_data = MiniblockData(list(example['miniblocks'].items()))
    print(json.dumps(mb_data.get_data_for_detailed_report(), indent=4))

'''
Class to hold data related to a miniblock and its appearances in headers.

For headers V1, miniblocks are directly in the header under "miniBlockHeaders".
For headers V2, miniblocks are under "header" -> "miniBlockHeaders".
For metaheaders V1, miniblocks are under "miniBlockHeaders" and also in "shardInfo"->"shardMiniBlockHeaders".
'''

'''
header: miniblocks
Example:
HV1
            {
                "accumulatedFees": "0",
                "blockBodyType": 0,
                "chainID": "31",
                "developerFees": "0",
                "epoch": 0,
                "epochStartMetaHash": "",
                "leaderSignature": "",
                "metaBlockHashes": [
                    "353b97d74521f37d6776c9b8070f928af210d9cca2f22531f635d2ed207d0a44"
                ],
                "miniBlockHeaders": [],
                "nonce": 6,
                "peerChanges": [],
                "prevHash": "5fef2a316b7046470de021f37a5443854699950138ded925cc0d10a1c4cdc383",
                "prevRandSeed": "0e4d1c5112aef96495f851ea8a285fab7aa7a28723d9930f8f280f1e158de7b64f95f301160794da4f551cd789176714",
                "pubKeysBitmap": "",
                "randSeed": "22400b5e348375592be8537cc797da3f80fc5a385feb18922c060c7b9b7e53698bc3ffa7da4e28bee2a0fd2ddb5ea419",
                "receiptsHash": "0e5751c026e543b2e8ab2eb06099daa1d1e5df47778f7787faab45cdf12fe3a8",
                "reserved": "",
                "rootHash": "34f5b60441c630fbd7327835070a64429eb40627b0b638c062d15aa1de2f7208",
                "round": 6,
                "shardID": 1,
                "signature": "",
                "softwareVersion": "64656661756c74",
                "timeStamp": 1762937897,
                "txCount": 0
            },


HV2
            {
                "header": {
                    "accumulatedFees": "0",
                    "blockBodyType": 0,
                    "chainID": "31",
                    "developerFees": "0",
                    "epoch": 2,
                    "epochStartMetaHash": "e43e0e37766f6e59bb5bc586b244427e0385ea720292a0c17b0272952b4afbf5",
                    "leaderSignature": "05bbf615de4e0d1271df5fd4eb6a057a6d89fd945499b24a50dbc080d4b87dd8c5823105fceacbdf214653621bc3f10f",
                    "metaBlockHashes": [
                        "e43e0e37766f6e59bb5bc586b244427e0385ea720292a0c17b0272952b4afbf5"
                    ],
                    "miniBlockHeaders": [
                        {
                            "hash": "d3ba36a1f12970615fbea92a8a3b1639fef9676dc2951a7150c73516cbde2301",
                            "receiverShardID": 1,
                            "reserved": "200a",
                            "senderShardID": 4294967295,
                            "txCount": 11,
                            "type": 255
                        },
                        {
                            "hash": "697a913df8d23454c56755c9f60dca2008d182ef685c124f0ade6332ae291647",
                            "receiverShardID": 4294967280,
                            "reserved": "200e",
                            "senderShardID": 4294967295,
                            "txCount": 15,
                            "type": 60
                        },
                        {
                            "hash": "9948e5f806de024ccc253429850f3e6b4203d2509c7d653f8dd00d89e8d32ae5",
                            "receiverShardID": 4294967280,
                            "reserved": "200e",
                            "senderShardID": 4294967295,
                            "txCount": 15,
                            "type": 60
                        },
                        {
                            "hash": "722b967aac3a34f4097e536176975f0f7fb06e70f45e35a67a09a09011f699be",
                            "receiverShardID": 4294967280,
                            "reserved": "200e",
                            "senderShardID": 4294967295,
                            "txCount": 15,
                            "type": 60
                        },
                        {
                            "hash": "7ab74c81351bf5d5876421da2fda21257c4924240be05fae66523dcc7cf165ed",
                            "receiverShardID": 4294967280,
                            "reserved": "200e",
                            "senderShardID": 4294967295,
                            "txCount": 15,
                            "type": 60
                        }
                    ],
                    "nonce": 403,
                    "peerChanges": [],
                    "prevHash": "5e2640a23517bb8fbba1ea9428c80bb86af907d3dca5f931a8c414ecab15816c",
                    "prevRandSeed": "41ec3c4ce905421a9646354435b0c6259d7f6268f784133dc0e3f5033580e5492071b90f60c84f25c396004f98c0f00a",
                    "pubKeysBitmap": "",
                    "randSeed": "2f26601869d5130613e685b0b9fd829db86310e30e446acfa50e0010865a1e5f82d1e7456930d10942e8e8f2e587b486",
                    "receiptsHash": "0e5751c026e543b2e8ab2eb06099daa1d1e5df47778f7787faab45cdf12fe3a8",
                    "reserved": "",
                    "rootHash": "0a4c40ca1a8488ca7d3832fb73c315a3a86facafca48978f2d28b2c0da7dcf41",
                    "round": 403,
                    "shardID": 1,
                    "signature": "",
                    "softwareVersion": "32",
                    "timeStamp": 1762940279000,
                    "txCount": 71
                },
                "scheduledAccumulatedFees": "0",
                "scheduledDeveloperFees": "0",
                "scheduledGasPenalized": 0,
                "scheduledGasProvided": 0,
                "scheduledGasRefunded": 0,
                "scheduledRootHash": "40ff71800f799bd91ad57e00b8fd232a12ab559360b93f16bfbd23463dd25721"
            },

metaheader: miniBlockHeaders, shardinfo/shardMiniBlockHeaders
Example:
             {
                "accumulatedFees": "5000000000000000",
                "accumulatedFeesInEpoch": "660292165000000000",
                "chainID": "31",
                "devFeesInEpoch": "6694699500000000",
                "developerFees": "1500000000000000",
                "epoch": 1,
                "epochStart": {
                    "economics": {
                        "nodePrice": null,
                        "prevEpochStartHash": "",
                        "prevEpochStartRound": 0,
                        "rewardsForProtocolSustainability": null,
                        "rewardsPerBlock": null,
                        "totalNewlyMinted": null,
                        "totalSupply": null,
                        "totalToDistribute": null
                    },
                    "lastFinalizedHeaders": []
                },
                "leaderSignature": "a5c38e4db58f7f6598948cf1050fc96f73ed4952db9d11f32a97ee9cfb9f5df84a46733e3b9bcc33b32f83ed9d9ec40a",
                "miniBlockHeaders": [
                    {
                        "hash": "f5323d263ac564829e92c457d4393a03d788ed81d9023b247a025d41a82f137b",
                        "receiverShardID": 4294967295,
                        "reserved": "",
                        "senderShardID": 0,
                        "txCount": 1,
                        "type": 0
                    },
                    {
                        "hash": "2a669d6ba2b61d3915b3b75d779443093dbe408a947445fb7d4ce9c0f8c3dbba",
                        "receiverShardID": 0,
                        "reserved": "2002",
                        "senderShardID": 4294967295,
                        "txCount": 3,
                        "type": 90
                    },
                    {
                        "hash": "83b76de2135a864cebf7845567ebdabbf31c3c4005340221c5feecb65867a88a",
                        "receiverShardID": 1,
                        "reserved": "2001",
                        "senderShardID": 4294967295,
                        "txCount": 2,
                        "type": 90
                    },
                    {
                        "hash": "88b7fd9f2c9d3df8bb88ec7d3dd3e3fd13d0dd3ca1e9e9e0d5547bcdb9a3f1b0",
                        "receiverShardID": 2,
                        "reserved": "2001",
                        "senderShardID": 4294967295,
                        "txCount": 2,
                        "type": 90
                    }
                ],
                "nonce": 283,
                "peerInfo": [],
                "prevHash": "b82b1e3ea44357d35d28c76de0ef5d66674c0a602edd8b8c73b45cf61087d0e1",
                "prevRandSeed": "19e8fbcf33054f8a5c0982a1d1bcdbe8e698318eaf8b6061316072819463b2b3ab1c22500cb4f61d9f37585d9b994d84",
                "pubKeysBitmap": "",
                "randSeed": "9d99b6595f2ff33bca4ca5c5cd0331b9b36053f7857bc52806806440feed7a0eae9f44c4691a16e753d05536da369b8f",
                "receiptsHash": "0e5751c026e543b2e8ab2eb06099daa1d1e5df47778f7787faab45cdf12fe3a8",
                "reserved": "",
                "rootHash": "315acd42e00cca35998436b7a060cb196674cf6e058b74a3637026e101519835",
                "round": 283,
                "shardInfo": [
                    {
                        "accumulatedFees": "22715500000000000",
                        "developerFees": "0",
                        "epoch": 1,
                        "headerHash": "3b41fc97dd499d9cb34bfeb5b12898b5f456886d06a543c72b2f0f758a13ccc1",
                        "lastIncludedMetaNonce": 280,
                        "nonce": 282,
                        "numPendingMiniBlocks": 1,
                        "prevHash": "38c906f96e2d56474407b08fd5be7b46ba51466537799b1b623437c65b325c66",
                        "prevRandSeed": "cb2ba79e42b33bd609694de59b2b8b24baad3d7f2b9bd2044563f15808c610fac34ac7580d5067bc177c45d01c625113",
                        "pubKeysBitmap": "",
                        "round": 282,
                        "shardID": 0,
                        "shardMiniBlockHeaders": [
                            {
                                "hash": "6c5248018490f44bc5e9961e095130c8aef96bc427f20b6031d51a80fa818ca8",
                                "receiverShardID": 0,
                                "reserved": "",
                                "senderShardID": 0,
                                "txCount": 92,
                                "type": 0
                            },
                            {
                                "hash": "4d1ceacabdcea75c9cde8a1f00058507760d03998c1a98bd7809be2a5f61973e",
                                "receiverShardID": 1,
                                "reserved": "",
                                "senderShardID": 0,
                                "txCount": 299,
                                "type": 0
                            },
                            {
                                "hash": "f5323d263ac564829e92c457d4393a03d788ed81d9023b247a025d41a82f137b",
                                "receiverShardID": 4294967295,
                                "reserved": "",
                                "senderShardID": 0,
                                "txCount": 1,
                                "type": 0
                            }
                        ],
                        "signature": "",
                        "txCount": 392
                    },
                    {
                        "accumulatedFees": "4150000000000000",
                        "developerFees": "0",
                        "epoch": 1,
                        "headerHash": "ba444fcc2da250641426831623e93fe2107e2c3f415bd245386d68286c78bb79",
                        "lastIncludedMetaNonce": 280,
                        "nonce": 282,
                        "numPendingMiniBlocks": 2,
                        "prevHash": "2a308ec0bd722d1197abd2824daa804833e4a78f50d01b43333b998d36657af7",
                        "prevRandSeed": "44d8d8a69e52494bcaf57ba8c52f07843ce47dac05498b6badee4457d8cf8c3846fb068c9edcc074df0d6b2f2ff5e391",
                        "pubKeysBitmap": "",
                        "round": 282,
                        "shardID": 1,
                        "shardMiniBlockHeaders": [
                            {
                                "hash": "a6b7bc2cecaddf1743109a5f045592c9fefb0954cfa4eb1cc1c44bfe81524645",
                                "receiverShardID": 1,
                                "reserved": "",
                                "senderShardID": 1,
                                "txCount": 83,
                                "type": 0
                            }
                        ],
                        "signature": "",
                        "txCount": 83
                    },
                    {
                        "accumulatedFees": "4150000000000000",
                        "developerFees": "0",
                        "epoch": 1,
                        "headerHash": "1b135e7cc2876ddbf7ee1679ab86c63f4c4416fd76e1ffb96a161f072f012550",
                        "lastIncludedMetaNonce": 280,
                        "nonce": 281,
                        "numPendingMiniBlocks": 2,
                        "prevHash": "a9da1c4b5e2e65f3c4a7aedbb230ee1f9afe0ae9432965b8971e6e26c5546509",
                        "prevRandSeed": "bb30cd93bac3a177f65beafbab717113be974e3d31ba1851911059e7a61643843d4b1b0308659f6fde0657cc90d7ca07",
                        "pubKeysBitmap": "",
                        "round": 282,
                        "shardID": 2,
                        "shardMiniBlockHeaders": [
                            {
                                "hash": "878916cd4e6aff248c15a0fcdd8bb19025a1db1cbabf6ad762426672cff0cd0a",
                                "receiverShardID": 2,
                                "reserved": "",
                                "senderShardID": 2,
                                "txCount": 83,
                                "type": 0
                            }
                        ],
                        "signature": "",
                        "txCount": 83
                    }
                ],
                "signature": "",
                "softwareVersion": "32",
                "timeStamp": 1762939559,
                "txCount": 566,
                "validatorStatsRootHash": "2bdc8762983b907c262896a4387b432746129bce1a357646a21e67c977a28eb5"
            },
        '''
