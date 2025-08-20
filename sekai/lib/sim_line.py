from sonolus.script.interval import clamp, lerp, unlerp

from sekai.lib.layer import LAYER_SIM_LINE, get_z
from sekai.lib.layout import Layout, approach, get_alpha, layout_sim_line
from sekai.lib.options import Options
from sekai.lib.skin import Skin


def draw_sim_line(
    lane_a: float,
    progress_a: float,
    target_time_a: float,
    lane_b: float,
    progress_b: float,
    target_time_b: float,
):
    if not Options.sim_line_enabled:
        return

    if progress_a < Layout.progress_start and progress_b < Layout.progress_start:
        return
    if progress_a > Layout.progress_cutoff and progress_b > Layout.progress_cutoff:
        return

    adj_progress_a = clamp(progress_a, Layout.progress_start, Layout.progress_cutoff)
    adj_progress_b = clamp(progress_b, Layout.progress_start, Layout.progress_cutoff)
    if abs(progress_a - progress_b) > 1e-6:
        frac_a = unlerp(progress_a, progress_b, adj_progress_a)
        frac_b = unlerp(progress_a, progress_b, adj_progress_b)
        adj_lane_a = lerp(lane_a, lane_b, frac_a)
        adj_lane_b = lerp(lane_a, lane_b, frac_b)
    else:
        adj_lane_a = lane_a
        adj_lane_b = lane_b
    adj_travel_a = approach(adj_progress_a)
    adj_travel_b = approach(adj_progress_b)
    layout = layout_sim_line(
        adj_lane_a,
        adj_travel_a,
        adj_lane_b,
        adj_travel_b,
    )
    z = get_z(LAYER_SIM_LINE, (target_time_a + target_time_b) / 2, (lane_a + lane_b) / 2)
    a = min(
        get_alpha(target_time_a),
        get_alpha(target_time_b),
    )
    Skin.sim_line.draw(layout, z=z, a=a)
