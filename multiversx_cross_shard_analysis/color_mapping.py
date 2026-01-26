from multiversx_cross_shard_analysis.constants import Colors


from reportlab.lib import colors


COLORS_MAPPING = {
    Colors.origin_proposed: colors.lightyellow,
    Colors.origin_partial_executed: colors.orange,
    Colors.origin_final: colors.yellow,
    Colors.dest_proposed: colors.mistyrose,
    Colors.dest_partial_executed: colors.palevioletred,
    Colors.dest_final: colors.pink,
    Colors.meta_origin_committed: colors.lightgreen,
    Colors.meta_dest_committed: colors.lightblue,
    Colors.origin_exec_proposed: colors.khaki,
    Colors.origin_exec_partial_executed: colors.gold,
    Colors.origin_exec_final: colors.yellow,
    Colors.dest_exec_proposed: colors.lightcoral,
    Colors.dest_exec_partial_executed: colors.crimson,
    Colors.dest_exec_final: colors.pink,
    Colors.meta_origin_exec_committed: colors.mediumseagreen,
    Colors.meta_dest_exec_committed: colors.cornflowerblue,
}
