from typing import Any

from multiversx_cross_shard_analysis.constants import ALL_SHARDS_ID, META_SHARD_ID
from multiversx_cross_shard_analysis.issues import Issues


def mention(mtype: str, round_number: int, shard_id: int) -> tuple[str, dict[str, Any]]:
    return (mtype, {"nonce": 0, "round": round_number, "epoch": 8, "shard_id": shard_id, "reserved": {}})


def make_mb(receiver: int, mentioned: list[tuple[str, dict[str, Any]]], sender: int = 0, mb_type: int = 0) -> dict[
    str, Any]:
    return {
        "receiverShardID": receiver,
        "senderShardID": sender,
        "type": mb_type,
        "txCount": 1,
        "first_seen_epoch": 8,
        "mentioned": mentioned,
    }


# correct flow for a shard -> meta miniblock: the metablock proposes it for its own
# execution (labeled dest_shard) and commits the origin exec result (meta_origin)
# in the same round, then executes it in the next metablock
def meta_destined_correct_flow(mb_type: int = 0) -> dict[str, Any]:
    return make_mb(META_SHARD_ID, [
        mention("origin_shard_proposed_headers_exec", 6379, 0),
        mention("origin_shard_committed_headers_exec", 6379, 0),
        mention("dest_shard_proposed_headers", 6380, META_SHARD_ID),
        mention("meta_origin_shard_proposed_headers", 6380, META_SHARD_ID),
        mention("dest_shard_committed_headers", 6380, META_SHARD_ID),
        mention("meta_origin_shard_committed_headers", 6380, META_SHARD_ID),
        mention("dest_shard_proposed_headers_exec", 6381, META_SHARD_ID),
        mention("dest_shard_committed_headers_exec", 6381, META_SHARD_ID),
    ], mb_type=mb_type)


def normal_cross_shard_correct_flow() -> dict[str, Any]:
    return make_mb(1, [
        mention("origin_shard_proposed_headers_exec", 6379, 0),
        mention("origin_shard_committed_headers_exec", 6379, 0),
        mention("meta_origin_shard_proposed_headers", 6380, META_SHARD_ID),
        mention("meta_origin_shard_committed_headers", 6380, META_SHARD_ID),
        mention("dest_shard_proposed_headers", 6381, 1),
        mention("dest_shard_committed_headers", 6381, 1),
        mention("dest_shard_proposed_headers_exec", 6382, 1),
        mention("dest_shard_committed_headers_exec", 6382, 1),
        mention("meta_dest_shard_proposed_headers", 6383, META_SHARD_ID),
        mention("meta_dest_shard_committed_headers", 6383, META_SHARD_ID),
    ])


class TestMissingOrDuplicateDestination:
    issue = Issues.MISSING_OR_DUPLICATE_DESTINATION

    def test_meta_destined_correct_flow_is_clean(self):
        assert self.issue.check_missing_or_duplicate_destination(meta_destined_correct_flow()) is False

    def test_meta_destined_scr_correct_flow_is_clean(self):
        assert self.issue.check_missing_or_duplicate_destination(meta_destined_correct_flow(mb_type=90)) is False

    def test_normal_cross_shard_correct_flow_is_clean(self):
        assert self.issue.check_missing_or_duplicate_destination(normal_cross_shard_correct_flow()) is False

    def test_missing_destination_detected(self):
        mb = make_mb(1, [
            mention("origin_shard_proposed_headers_exec", 6379, 0),
            mention("origin_shard_committed_headers_exec", 6379, 0),
            mention("meta_origin_shard_committed_headers", 6380, META_SHARD_ID),
        ])
        assert self.issue.check_missing_or_duplicate_destination(mb) is True

    def test_duplicate_destination_detected(self):
        mb = normal_cross_shard_correct_flow()
        mb["mentioned"] += [
            mention("dest_shard_proposed_headers", 6383, 1),
            mention("dest_shard_committed_headers", 6383, 1),
        ]
        assert self.issue.check_missing_or_duplicate_destination(mb) is True

    def test_meta_destined_double_include_detected(self):
        mb = meta_destined_correct_flow()
        mb["mentioned"] += [
            mention("dest_shard_proposed_headers", 6382, META_SHARD_ID),
            mention("dest_shard_committed_headers", 6382, META_SHARD_ID),
        ]
        assert self.issue.check_missing_or_duplicate_destination(mb) is True


class TestWrongProcessingOrder:
    issue = Issues.WRONG_PROCESSING_ORDER

    def test_meta_destined_correct_flow_is_clean(self):
        assert self.issue.check_wrong_order(meta_destined_correct_flow()) is False

    def test_normal_cross_shard_correct_flow_is_clean(self):
        assert self.issue.check_wrong_order(normal_cross_shard_correct_flow()) is False

    def test_dest_proposal_before_meta_origin_commit_detected(self):
        mb = make_mb(1, [
            mention("origin_shard_committed_headers_exec", 6379, 0),
            mention("dest_shard_proposed_headers", 6380, 1),
            mention("meta_origin_shard_committed_headers", 6381, META_SHARD_ID),
            mention("dest_shard_committed_headers_exec", 6382, 1),
        ])
        assert self.issue.check_wrong_order(mb) is True

    def test_meta_destined_exec_before_proposal_detected(self):
        mb = make_mb(META_SHARD_ID, [
            mention("origin_shard_committed_headers_exec", 6379, 0),
            mention("dest_shard_committed_headers_exec", 6380, META_SHARD_ID),
            mention("dest_shard_committed_headers", 6381, META_SHARD_ID),
            mention("meta_origin_shard_committed_headers", 6381, META_SHARD_ID),
        ])
        assert self.issue.check_wrong_order(mb) is True

    # epoch-start peer (validator info) miniblock, broadcast from meta to all shards;
    # shards include it at their own pace, so meta notarizations interleave with
    # other shards' inclusions
    def test_broadcast_interleaved_destinations_is_clean(self):
        mb = make_mb(ALL_SHARDS_ID, [
            mention("origin_shard_proposed_headers", 101, META_SHARD_ID),
            mention("origin_shard_committed_headers", 101, META_SHARD_ID),
            mention("dest_shard_proposed_headers", 102, 1),
            mention("meta_dest_shard_proposed_headers", 103, META_SHARD_ID),
            mention("meta_dest_shard_committed_headers", 103, META_SHARD_ID),
            mention("dest_shard_committed_headers", 103, 1),
            mention("dest_shard_proposed_headers", 103, 0),
            mention("dest_shard_committed_headers", 103, 0),
            mention("meta_dest_shard_proposed_headers", 104, META_SHARD_ID),
            mention("meta_dest_shard_committed_headers", 104, META_SHARD_ID),
        ], sender=META_SHARD_ID, mb_type=60)
        assert self.issue.check_wrong_order(mb) is False

    def test_broadcast_destination_before_origin_detected(self):
        mb = make_mb(ALL_SHARDS_ID, [
            mention("dest_shard_proposed_headers", 100, 1),
            mention("origin_shard_committed_headers", 101, META_SHARD_ID),
            mention("dest_shard_committed_headers", 102, 1),
        ], sender=META_SHARD_ID, mb_type=60)
        assert self.issue.check_wrong_order(mb) is True
