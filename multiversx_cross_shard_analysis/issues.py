from enum import Enum
from typing import Any, Callable

MAX_ROUND_GAP_ALLOWED = 1
SUPERNOVA_ACTIVATION_EPOCH = 2


class Issues(Enum):
    MISSING_OR_DUPLICATE_DESTINATION = 'missing_or_duplicate_destination'
    WRONG_PROCESSING_ORDER = 'wrong_processing_order'
    GAP_BETWEEN_ROUNDS = 'gap_between_rounds'

    # Logic for: GAP_BETWEEN_ROUNDS
    def check_gap_between_rounds(self, mb_info: dict[str, Any]) -> bool:
        last_round = -1
        for _, mentioning_header in mb_info.get('mentioned', []):
            if last_round == -1:
                last_round = mentioning_header.get('round')
            elif mentioning_header.get('round') - last_round > MAX_ROUND_GAP_ALLOWED:
                return True
            last_round = mentioning_header.get('round')
        return False

    # Logic for: MISSING_DESTINATION
    def check_missing_or_duplicate_destination(self, mb_info: dict[str, Any]) -> bool:
        receiver = mb_info.get("receiverShardID")
        sender = mb_info.get("senderShardID")
        count = 0

        for _, header in mb_info.get("mentioned", []):
            if header.get("shard_id") == receiver and mb_info.get("type") in [0, 90]:
                count += 1

        is_dest_missing = count == 0 and mb_info.get("type") in [0, 90]
        is_dest_duplicate = count > 2 and mb_info.get("type") in [0, 90] and receiver != sender and mb_info.get("first_seen_epoch", 0) >= SUPERNOVA_ACTIVATION_EPOCH

        return is_dest_missing or is_dest_duplicate

    # Logic for: WRONG_PROCESSING_ORDER
    def check_wrong_order(self, mb_info: dict[str, Any]) -> bool:
        max_phase = -1

        for mtype, data in sorted(mb_info.get('mentioned', []), key=lambda x: x[1].get('round', 0)):
            if 'exec' in mtype:
                phase = 1 if 'origin' in mtype else 4
            elif 'meta' in mtype:
                phase = 2 if 'origin' in mtype else 5
            else:
                phase = 0 if 'origin' in mtype else 3

            if phase < max_phase:
                return True
            max_phase = phase

        return False

    def run_check(self, issue_type: 'Issues', mb_info: dict[str, Any]) -> bool:
        """Helper to route to the correct method."""
        check_map: dict[Issues, Callable] = {
            Issues.MISSING_OR_DUPLICATE_DESTINATION: self.check_missing_or_duplicate_destination,
            Issues.WRONG_PROCESSING_ORDER: self.check_wrong_order,
            Issues.GAP_BETWEEN_ROUNDS: self.check_gap_between_rounds,
        }
        return check_map[issue_type](mb_info)


'''
Example miniblock structure after being processed and enriched:
    {
            "hash": "5db8a831cad452a5d85aa1b7aa033f864827d083f54fc5133f83e8e5d16a2dac",
            "receiverShardID": 1,
            "reserved": "209208",
            "senderShardID": 0,
            "txCount": 1043,
            "type": 0,
            "first_seen_round": 441,
            "last_seen_round": 443,
            "first_seen_epoch": 2,
            "nonce": 440,
            "mentioned": [
                [
                    "origin_shard_proposed_headers_exec",
                    {
                        "nonce": 440,
                        "round": 441,
                        "epoch": 2,
                        "shard_id": 0,
                        "reserved": {
                            "ExecutionType": "Normal",
                            "State": "Final",
                            "IndexOfFirstTxProcessed": 0,
                            "IndexOfLastTxProcessed": 26
                        }
                    }
                ],
                [
                    "origin_shard_committed_headers_exec",
                    {
                        "nonce": 440,
                        "round": 441,
                        "epoch": 2,
                        "shard_id": 0,
                        "reserved": {
                            "ExecutionType": "Normal",
                            "State": "Final",
                            "IndexOfFirstTxProcessed": 0,
                            "IndexOfLastTxProcessed": 26
                        }
                    }
                ],
                [
                    "dest_shard_proposed_headers",
                    {
                        "nonce": 443,
                        "round": 443,
                        "epoch": 2,
                        "shard_id": 1,
                        "reserved": {
                            "ExecutionType": "Normal",
                            "State": "Proposed",
                            "IndexOfFirstTxProcessed": 0,
                            "IndexOfLastTxProcessed": 1042
                        }
                    }
                ],
                [
                    "dest_shard_committed_headers",
                    {
                        "nonce": 443,
                        "round": 443,
                        "epoch": 2,
                        "shard_id": 1,
                        "reserved": {
                            "ExecutionType": "Normal",
                            "State": "Proposed",
                            "IndexOfFirstTxProcessed": 0,
                            "IndexOfLastTxProcessed": 1042
                        }
                    }
                ],
                [
                    "meta_origin_shard_proposed_headers",
                    {
                        "nonce": 442,
                        "round": 442,
                        "epoch": 2,
                        "shard_id": 4294967295,
                        "reserved": {}
                    }
                ],
                [
                    "meta_origin_shard_committed_headers",
                    {
                        "nonce": 442,
                        "round": 442,
                        "epoch": 2,
                        "shard_id": 4294967295,
                        "reserved": {}
                    }
                ]
            ]
        }

'''
