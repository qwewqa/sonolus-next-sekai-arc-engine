from typing import assert_never

from sonolus.script.easing import ease_out_quad
from sonolus.script.interval import interp_clamped, lerp, unlerp_clamped
from sonolus.script.runtime import time
from sonolus.script.sprite import Sprite

from sekai.lib.layer import LAYER_SLOT_EFFECT, LAYER_SLOT_GLOW_EFFECT, get_z
from sekai.lib.layout import layout_slot_effect, layout_slot_glow_effect
from sekai.lib.options import Options, SlotEffectStyle


def slot_glow_effect_duration():
    return 0.25 * Options.effect_duration


def slot_effect_duration():
    return 0.5 * Options.effect_duration


def draw_slot_glow_effect(
    sprite: Sprite,
    start_time: float,
    end_time: float,
    lane: float,
    size: float,
):
    progress = unlerp_clamped(start_time, end_time, time())
    match Options.slot_effect_style:
        case SlotEffectStyle.VERTICAL | SlotEffectStyle.LANE:
            height = interp_clamped(
                (0, 0.1, 0.8, 1),
                (0, 1, 1, 0),
                progress,
            )
            a = lerp(1, 0, progress)
        case SlotEffectStyle.DISSIPATE:
            height = lerp(0.6, 1.2, ease_out_quad(progress))
            a = 1 - ease_out_quad(progress)
        case _:
            assert_never(Options.slot_effect_style)
    layout = layout_slot_glow_effect(lane, size, height)
    z = get_z(LAYER_SLOT_GLOW_EFFECT, -start_time, lane)
    for segment in layout:
        sprite.draw(segment, z=z, a=a)


def draw_slot_effect(
    sprite: Sprite,
    start_time: float,
    end_time: float,
    lane: float,
):
    progress = unlerp_clamped(start_time, end_time, time())
    layout = layout_slot_effect(lane)
    z = get_z(LAYER_SLOT_EFFECT, -start_time, lane)
    a = lerp(1, 0, progress)
    sprite.draw(layout, z=z, a=a)
