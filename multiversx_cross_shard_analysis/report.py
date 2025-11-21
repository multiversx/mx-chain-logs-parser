from collections import defaultdict
from typing import Any
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import json
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from multiversx_cross_shard_analysis.miniblock_data import MiniblockData

data = {
    "01f7f0f3503c62b69ff0fe22a57b97eaa2f164ac9e4a0bb852bc66e3f5c12369": {
        "lanes": {
            "origin": [
                [
                    "origin_shard_proposed_headers",
                    205
                ],
                [
                    "origin_shard_commited_headers",
                    205
                ]
            ],
            "dest": [
                [
                    "dest_shard_proposed_headers",
                    207
                ],
                [
                    "dest_shard_commited_headers",
                    207
                ]
            ],
            "meta": [
                [
                    "meta_origin_shard_proposed_headers",
                    206
                ],
                [
                    "meta_dest_shard_proposed_headers",
                    208
                ],
                [
                    "meta_origin_shard_commited_headers",
                    206
                ],
                [
                    "meta_dest_shard_commited_headers",
                    208
                ]
            ]
        },
        "origin_epoch": 1
    },
    "3fce18121e1ce8e57a3d776c91468649699e8238fad7898f46b8ac88b8d2c1cb": {
        "lanes": {
            "origin": [
                [
                    "origin_shard_proposed_headers",
                    210
                ],
                [
                    "origin_shard_commited_headers",
                    210
                ]
            ],
            "dest": [],
            "meta": [
                [
                    "meta_origin_shard_proposed_headers",
                    211
                ],
                [
                    "meta_origin_shard_commited_headers",
                    211
                ]
            ]
        },
        "origin_epoch": 1
    },
    "cb2bbdf01dd1a44c813ceecb58ae7404ad9016073fc707dda1be52f7dc5735fc": {
        "lanes": {
            "origin": [
                [
                    "origin_shard_proposed_headers",
                    210
                ],
                [
                    "origin_shard_commited_headers",
                    210
                ]
            ],
            "dest": [
                [
                    "dest_shard_proposed_headers",
                    212
                ],
                [
                    "dest_shard_commited_headers",
                    212
                ]
            ],
            "meta": [
                [
                    "meta_origin_shard_proposed_headers",
                    211
                ],
                [
                    "meta_dest_shard_proposed_headers",
                    213
                ],
                [
                    "meta_origin_shard_commited_headers",
                    211
                ],
                [
                    "meta_dest_shard_commited_headers",
                    213
                ]
            ]
        },
        "origin_epoch": 1
    },
    "01e7fc8132cd61f6aede3231bc9c9dc36dbe7d3ffcaca59fce7b46cca0e5884e": {
        "lanes": {
            "origin": [
                [
                    "origin_shard_proposed_headers",
                    210
                ],
                [
                    "origin_shard_commited_headers",
                    210
                ]
            ],
            "dest": [
                [
                    "dest_shard_proposed_headers",
                    212
                ],
                [
                    "dest_shard_commited_headers",
                    212
                ]
            ],
            "meta": [
                [
                    "meta_origin_shard_proposed_headers",
                    211
                ],
                [
                    "meta_dest_shard_proposed_headers",
                    213
                ],
                [
                    "meta_origin_shard_commited_headers",
                    211
                ],
                [
                    "meta_dest_shard_commited_headers",
                    213
                ]
            ]
        },
        "origin_epoch": 1
    },
    "f966a0d0370de9a7b0675ec153c03f61031e02864fe781ab49cca0f60439e590": {
        "lanes": {
            "origin": [
                [
                    "origin_shard_proposed_headers",
                    210
                ],
                [
                    "origin_shard_commited_headers",
                    210
                ]
            ],
            "dest": [
                [
                    "dest_shard_proposed_headers",
                    212
                ],
                [
                    "dest_shard_commited_headers",
                    212
                ]
            ],
            "meta": [
                [
                    "meta_origin_shard_proposed_headers",
                    211
                ],
                [
                    "meta_dest_shard_proposed_headers",
                    213
                ],
                [
                    "meta_origin_shard_commited_headers",
                    211
                ],
                [
                    "meta_dest_shard_commited_headers",
                    213
                ]
            ]
        },
        "origin_epoch": 1
    },
    "cdac3609485d6813f79c717e48e5d6cf94b3ca6e25dd372a21f3511f0eb1e536": {
        "lanes": {
            "origin": [
                [
                    "origin_shard_proposed_headers",
                    210
                ],
                [
                    "origin_shard_commited_headers",
                    210
                ]
            ],
            "dest": [
                [
                    "dest_shard_proposed_headers",
                    212
                ],
                [
                    "dest_shard_commited_headers",
                    212
                ]
            ],
            "meta": [
                [
                    "meta_origin_shard_proposed_headers",
                    211
                ],
                [
                    "meta_dest_shard_proposed_headers",
                    213
                ],
                [
                    "meta_origin_shard_commited_headers",
                    211
                ],
                [
                    "meta_dest_shard_commited_headers",
                    213
                ]
            ]
        },
        "origin_epoch": 1
    }
}


def draw_timeline(data: dict[str, Any]):
    lane_colors = {
        "origin": "#4CAF50",  # green
        "dest": "#FFEB3B",    # yellow
        "meta": "#2196F3"     # blue
    }

    shade_factor = {"proposed": 1.0, "commited": 0.6}

    plt.figure(figsize=(12, 6))

    for i, (mb_hash, mb_data) in enumerate(data.items()):
        # track number of events per round to offset them
        round_counts = defaultdict(int)
        for lane_type, events in mb_data["lanes"].items():
            for name, round_num in events:
                shade = shade_factor["proposed"] if "proposed" in name else shade_factor["commited"]
                rgb = mcolors.to_rgb(lane_colors[lane_type])
                color = tuple([c * shade for c in rgb])

                # stack multiple events in the same round
                offset = 0.15 * round_counts[round_num]
                plt.scatter(round_num, -i + offset, color=color, s=200, marker="s")
                round_counts[round_num] += 1

    plt.yticks([-i for i in range(len(data))], [h[:8] + '…' for h in data.keys()])
    plt.xlabel("Round")
    plt.title("Miniblock Timelines")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig("miniblocks.pdf")
    plt.show()


example = {"run_name": "cross-shard-execution-anal-9afe696daf", "miniblocks": {"01f7f0f3503c62b69ff0fe22a57b97eaa2f164ac9e4a0bb852bc66e3f5c12369": {"hash": "01f7f0f3503c62b69ff0fe22a57b97eaa2f164ac9e4a0bb852bc66e3f5c12369", "receiverShardID": 0, "reserved": "", "senderShardID": 1, "txCount": 1, "type": 0, "mentioned": [["dest_shard_proposed_headers", {"nonce": 207, "round": 207, "epoch": 1, "shard_id": 0}], ["dest_shard_commited_headers", {"nonce": 207, "round": 207, "epoch": 1, "shard_id": 0}], ["origin_shard_proposed_headers", {"nonce": 205, "round": 205, "epoch": 1, "shard_id": 1}], ["origin_shard_commited_headers", {"nonce": 205, "round": 205, "epoch": 1, "shard_id": 1}], ["meta_origin_shard_proposed_headers", {"nonce": 206, "round": 206, "epoch": 1, "shard_id": 4294967295}], ["meta_dest_shard_proposed_headers", {"nonce": 208, "round": 208, "epoch": 1, "shard_id": 4294967295}], ["meta_origin_shard_commited_headers", {"nonce": 206, "round": 206, "epoch": 1, "shard_id": 4294967295}], ["meta_dest_shard_commited_headers", {"nonce": 208, "round": 208, "epoch": 1, "shard_id": 4294967295}]]}, "3fce18121e1ce8e57a3d776c91468649699e8238fad7898f46b8ac88b8d2c1cb": {"hash": "3fce18121e1ce8e57a3d776c91468649699e8238fad7898f46b8ac88b8d2c1cb", "receiverShardID": 0, "reserved": "200b", "senderShardID": 0, "txCount": 12, "type": 0, "mentioned": [["origin_shard_proposed_headers", {"nonce": 210, "round": 210, "epoch": 1, "shard_id": 0}], ["origin_shard_commited_headers", {"nonce": 210, "round": 210, "epoch": 1, "shard_id": 0}], ["meta_origin_shard_proposed_headers", {"nonce": 211, "round": 211, "epoch": 1, "shard_id": 4294967295}], ["meta_origin_shard_commited_headers", {"nonce": 211, "round": 211, "epoch": 1, "shard_id": 4294967295}]]}, "cb2bbdf01dd1a44c813ceecb58ae7404ad9016073fc707dda1be52f7dc5735fc": {"hash": "cb2bbdf01dd1a44c813ceecb58ae7404ad9016073fc707dda1be52f7dc5735fc", "receiverShardID": 1, "reserved": "201c", "senderShardID": 0, "txCount": 29, "type": 0, "mentioned": [["origin_shard_proposed_headers", {"nonce": 210, "round": 210, "epoch": 1, "shard_id": 0}], ["origin_shard_commited_headers", {"nonce": 210, "round": 210, "epoch": 1, "shard_id": 0}], ["dest_shard_proposed_headers", {"nonce": 212, "round": 212, "epoch": 1, "shard_id": 1}], ["dest_shard_commited_headers", {"nonce": 212, "round": 212, "epoch": 1, "shard_id": 1}], ["meta_origin_shard_proposed_headers", {"nonce": 211, "round": 211, "epoch": 1, "shard_id": 4294967295}], ["meta_dest_shard_proposed_headers", {"nonce": 213, "round": 213, "epoch": 1, "shard_id": 4294967295}], ["meta_origin_shard_commited_headers", {"nonce": 211, "round": 211, "epoch": 1, "shard_id": 4294967295}], ["meta_dest_shard_commited_headers", {"nonce": 213, "round": 213, "epoch": 1, "shard_id": 4294967295}]]}, "01e7fc8132cd61f6aede3231bc9c9dc36dbe7d3ffcaca59fce7b46cca0e5884e": {"hash": "01e7fc8132cd61f6aede3231bc9c9dc36dbe7d3ffcaca59fce7b46cca0e5884e", "receiverShardID": 2, "reserved": "2008", "senderShardID": 0, "txCount": 9, "type": 0, "mentioned": [["origin_shard_proposed_headers", {"nonce": 210, "round": 210, "epoch": 1, "shard_id": 0}], ["origin_shard_commited_headers", {"nonce": 210, "round": 210, "epoch": 1, "shard_id": 0}], ["meta_origin_shard_proposed_headers", {"nonce": 211, "round": 211, "epoch": 1, "shard_id": 4294967295}], ["meta_dest_shard_proposed_headers", {"nonce": 213, "round": 213, "epoch": 1, "shard_id": 4294967295}], ["meta_origin_shard_commited_headers", {"nonce": 211, "round": 211, "epoch": 1, "shard_id": 4294967295}], ["meta_dest_shard_commited_headers", {"nonce": 213, "round": 213, "epoch": 1, "shard_id": 4294967295}], ["dest_shard_proposed_headers", {"nonce": 211, "round": 212, "epoch": 1, "shard_id": 2}], ["dest_shard_commited_headers", {"nonce": 211, "round": 212, "epoch": 1, "shard_id": 2}]]}, "f966a0d0370de9a7b0675ec153c03f61031e02864fe781ab49cca0f60439e590": {"hash": "f966a0d0370de9a7b0675ec153c03f61031e02864fe781ab49cca0f60439e590", "receiverShardID": 0, "reserved": "2012", "senderShardID": 2, "txCount": 19, "type": 0, "mentioned": [["dest_shard_proposed_headers", {"nonce": 212, "round": 212, "epoch": 1, "shard_id": 0}], ["dest_shard_commited_headers", {"nonce": 212, "round": 212, "epoch": 1, "shard_id": 0}], ["meta_origin_shard_proposed_headers", {"nonce": 211, "round": 211, "epoch": 1, "shard_id": 4294967295}], ["meta_dest_shard_proposed_headers", {"nonce": 213, "round": 213, "epoch": 1, "shard_id": 4294967295}], ["meta_origin_shard_commited_headers", {"nonce": 211, "round": 211, "epoch": 1, "shard_id": 4294967295}], ["meta_dest_shard_commited_headers", {"nonce": 213, "round": 213, "epoch": 1, "shard_id": 4294967295}], ["origin_shard_proposed_headers", {"nonce": 209, "round": 210, "epoch": 1, "shard_id": 2}], ["origin_shard_commited_headers", {"nonce": 209, "round": 210, "epoch": 1, "shard_id": 2}]]}, "cdac3609485d6813f79c717e48e5d6cf94b3ca6e25dd372a21f3511f0eb1e536": {"hash": "cdac3609485d6813f79c717e48e5d6cf94b3ca6e25dd372a21f3511f0eb1e536", "receiverShardID": 0, "reserved": "200e", "senderShardID": 1, "txCount": 15, "type": 0, "mentioned": [["dest_shard_proposed_headers", {"nonce": 212, "round": 212, "epoch": 1, "shard_id": 0}], ["dest_shard_commited_headers", {"nonce": 212, "round": 212, "epoch": 1, "shard_id": 0}], ["origin_shard_proposed_headers", {"nonce": 210, "round": 210, "epoch": 1, "shard_id": 1}], ["origin_shard_commited_headers", {"nonce": 210, "round": 210, "epoch": 1, "shard_id": 1}], ["meta_origin_shard_proposed_headers", {"nonce": 211, "round": 211, "epoch": 1, "shard_id": 4294967295}], ["meta_dest_shard_proposed_headers", {"nonce": 213, "round": 213, "epoch": 1, "shard_id": 4294967295}], ["meta_origin_shard_commited_headers", {"nonce": 211, "round": 211, "epoch": 1, "shard_id": 4294967295}], ["meta_dest_shard_commited_headers", {"nonce": 213, "round": 213, "epoch": 1, "shard_id": 4294967295}]]}}}
# usage:
# export_timeline_pdf(data, "miniblock_lifecycle.pdf")


def chunks(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]


if __name__ == "__main__":
    with open('./Reports/cross-shard-execution-anal-9afe696daf_old/Miniblocks/miniblocks_report.json', 'r') as f:
        data = json.load(f)

    mb_data = MiniblockData(list(data['miniblocks'].items())).get_data_for_detailed_report1()

    LIMIT = 30  # how many miniblocks per draw

    for epoch in sorted(mb_data.keys()):
        print(f"Epoch: {epoch} - miniblocks: {len(mb_data[epoch])}")

        sorted_mb = sorted(
            mb_data[epoch].items(),
            key=lambda x: x[1]['start_round']
        )

        for batch in chunks(sorted_mb, LIMIT):
            draw_timeline(data=dict(batch))
