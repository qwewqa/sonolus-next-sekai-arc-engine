from sekai.lib.effect import SFX_DISTANCE, Effects
from sekai.lib.layer import LAYER_COVER, LAYER_JUDGMENT_LINE, LAYER_STAGE, get_z
from sekai.lib.layout import (
    layout_hidden_cover,
    layout_judge_line,
    layout_lane,
    layout_lane_by_edges,
    layout_stage_cover,
)
from sekai.lib.options import Options
from sekai.lib.particle import Particles
from sekai.lib.skin import Skin


def draw_stage_and_accessories():
    draw_stage()
    draw_stage_cover()


def draw_stage():
    if not Options.show_lane:
        return
    layout = layout_lane_by_edges(-6.5, -6)
    Skin.stage_left_border.draw(layout, z=get_z(LAYER_STAGE))
    layout = layout_lane_by_edges(6, 6.5)
    Skin.stage_right_border.draw(layout, z=get_z(LAYER_STAGE))

    for lane in (-5, -3, -1, 1, 3, 5):
        layout = layout_lane(lane, 1)
        Skin.lane.draw(layout, z=get_z(LAYER_STAGE))

    for segment in layout_judge_line():
        Skin.judgment_line.draw(segment, z=get_z(LAYER_JUDGMENT_LINE))


def draw_stage_cover():
    if Options.stage_cover > 0:
        for segment in layout_stage_cover():
            Skin.cover.draw(segment, z=get_z(LAYER_COVER), a=0.8)
    if Options.hidden > 0:
        for segment in layout_hidden_cover():
            Skin.cover.draw(segment, z=get_z(LAYER_COVER), a=0.8)


def play_lane_hit_effects(lane: float):
    play_lane_sfx(lane)
    play_lane_particle(lane)


def play_lane_sfx(lane: float):
    if Options.sfx_enabled:
        Effects.stage.play(SFX_DISTANCE)


def schedule_lane_sfx(lane: float, target_time: float):
    if Options.sfx_enabled:
        Effects.stage.schedule(target_time, SFX_DISTANCE)


def play_lane_particle(lane: float):
    if Options.lane_effect_enabled:
        layout = layout_lane(lane, 0.5)
        Particles.lane.spawn(layout, duration=0.3)
