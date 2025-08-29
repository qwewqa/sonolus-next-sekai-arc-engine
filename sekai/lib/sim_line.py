from sonolus.script.interval import clamp, lerp, unlerp

from sekai.lib.layer import LAYER_SIM_LINE, get_z
from sekai.lib.layout import Layout, approach, get_alpha, layout_sim_line
from sekai.lib.options import Options
from sekai.lib.skin import Skin


def draw_sim_line(
    left_lane: float,
    left_progress: float,
    left_target_time: float,
    right_lane: float,
    right_progress: float,
    right_target_time: float,
):
    if not Options.sim_line_enabled:
        return

    if left_progress < Layout.progress_start and right_progress < Layout.progress_start:
        return
    if left_progress > Layout.progress_cutoff and right_progress > Layout.progress_cutoff:
        return

    adj_progress_a = clamp(left_progress, Layout.progress_start, Layout.progress_cutoff)
    adj_progress_b = clamp(right_progress, Layout.progress_start, Layout.progress_cutoff)
    if abs(left_progress - right_progress) > 1e-6:
        frac_a = unlerp(left_progress, right_progress, adj_progress_a)
        frac_b = unlerp(left_progress, right_progress, adj_progress_b)
        adj_lane_a = lerp(left_lane, right_lane, frac_a)
        adj_lane_b = lerp(left_lane, right_lane, frac_b)
    else:
        adj_lane_a = left_lane
        adj_lane_b = right_lane
    adj_travel_a = approach(adj_progress_a)
    adj_travel_b = approach(adj_progress_b)
    layout = layout_sim_line(
        adj_lane_a,
        adj_travel_a,
        adj_lane_b,
        adj_travel_b,
    )
    z = get_z(LAYER_SIM_LINE, (left_target_time + right_target_time) / 2, (left_lane + right_lane) / 2)
    a = min(
        get_alpha(left_target_time),
        get_alpha(right_target_time),
    )
    Skin.sim_line.draw(layout, z=z, a=a)
