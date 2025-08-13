from enum import IntEnum
from math import ceil, pi, sin
from typing import assert_never

from sonolus.script.easing import ease_out_cubic
from sonolus.script.interval import clamp, lerp, unlerp
from sonolus.script.runtime import time

from sekai.lib.ease import EaseType, ease
from sekai.lib.layer import LAYER_NOTE_CONNECTOR, LAYER_NOTE_CONNECTOR_CRITICAL, LAYER_NOTE_GUIDE, get_z
from sekai.lib.layout import (
    Layout,
    approach,
    get_alpha,
    layout_slide_connector_segment,
    transformed_vec_at,
)
from sekai.lib.options import Options
from sekai.lib.skin import (
    ConnectorSprites,
    GuideSprites,
    blue_guide_sprites,
    critical_slide_connector_sprites,
    cyan_guide_sprites,
    green_guide_sprites,
    neutral_guide_sprites,
    normal_slide_connector_sprites,
    purple_guide_sprites,
    red_guide_sprites,
    yellow_guide_sprites,
)

CONNECTOR_QUALITY_SCALE = 1.5


class SlideConnectorKind(IntEnum):
    NORMAL = 1
    CRITICAL = 2


class SlideStartType(IntEnum):
    TAP = 0
    TRACE = 1
    NONE = 2


class SlideVisualState(IntEnum):
    WAITING = 0
    INACTIVE = 1
    ACTIVE = 2


class GuideFadeType(IntEnum):
    OUT = 0
    NONE = 1
    IN = 2


class GuideColor(IntEnum):
    NEUTRAL = 0
    RED = 1
    GREEN = 2
    BLUE = 3
    YELLOW = 4
    PURPLE = 5
    CYAN = 6
    BLACK = 7


def get_connector_sprites(kind: SlideConnectorKind) -> ConnectorSprites:
    result = +ConnectorSprites
    match kind:
        case SlideConnectorKind.NORMAL:
            result @= normal_slide_connector_sprites
        case SlideConnectorKind.CRITICAL:
            result @= critical_slide_connector_sprites
        case _:
            assert_never(kind)
    return result


def get_guide_sprites(color: GuideColor) -> GuideSprites:
    result = +GuideSprites
    match color:
        case GuideColor.NEUTRAL:
            result @= neutral_guide_sprites
        case GuideColor.RED:
            result @= red_guide_sprites
        case GuideColor.GREEN:
            result @= green_guide_sprites
        case GuideColor.BLUE:
            result @= blue_guide_sprites
        case GuideColor.YELLOW:
            result @= yellow_guide_sprites
        case GuideColor.PURPLE:
            result @= purple_guide_sprites
        case GuideColor.CYAN:
            result @= cyan_guide_sprites
        case GuideColor.BLACK:
            result @= blue_guide_sprites
        case _:
            assert_never(color)
    return result


def get_guide_alpha(fade_type: GuideFadeType, overall_progress: float) -> float:
    match fade_type:
        case GuideFadeType.OUT:
            return (1 - overall_progress) * 0.5
        case GuideFadeType.NONE:
            return 0.5
        case GuideFadeType.IN:
            return overall_progress * 0.5
        case _:
            assert_never(fade_type)


def draw_connector(
    kind: SlideConnectorKind,
    visual_state: SlideVisualState,
    ease_type: EaseType,
    quality: int,
    lane_a: float,
    size_a: float,
    progress_a: float,
    target_time_a: float,
    lane_b: float,
    size_b: float,
    progress_b: float,
    target_time_b: float,
):
    if progress_a < Layout.progress_start and progress_b < Layout.progress_start:
        return
    if progress_a > Layout.progress_cutoff and progress_b > Layout.progress_cutoff:
        return
    if progress_a == progress_b:
        return
    if time() >= target_time_b:
        return

    sprites = get_connector_sprites(kind)

    start_progress = clamp(progress_a if time() < target_time_a else 1, Layout.progress_start, Layout.progress_cutoff)
    end_progress = clamp(progress_b, Layout.progress_start, Layout.progress_cutoff)
    start_frac = unlerp(progress_a, progress_b, start_progress)
    end_frac = unlerp(progress_a, progress_b, end_progress)

    start_travel = approach(start_progress)
    end_travel = approach(end_progress)
    start_lane = lerp(lane_a, lane_b, ease(ease_type, start_frac))
    end_lane = lerp(lane_a, lane_b, ease(ease_type, end_frac))
    start_screen_center = transformed_vec_at(start_lane, start_travel)
    end_screen_center = transformed_vec_at(end_lane, end_travel)
    dist = (end_screen_center - start_screen_center).magnitude  # Lower bound since with easing it can be longer.
    segment_count = min(ceil(quality * dist * CONNECTOR_QUALITY_SCALE), quality)

    last_travel = start_travel
    last_lane = start_lane
    last_size = max(1e-3, lerp(size_a, size_b, ease(ease_type, start_frac)))
    last_target_time = lerp(target_time_a, target_time_b, start_frac)

    z = get_z(
        LAYER_NOTE_CONNECTOR if kind != SlideConnectorKind.CRITICAL else LAYER_NOTE_CONNECTOR_CRITICAL,
        time=target_time_a,
        lane=lane_a,
    )

    for i in range(1, segment_count + 1):
        next_frac = lerp(start_frac, end_frac, i / segment_count)
        next_progress = lerp(progress_a, progress_b, next_frac)
        next_travel = approach(next_progress)
        next_lane = lerp(lane_a, lane_b, ease(ease_type, next_frac))
        next_size = max(1e-3, lerp(size_a, size_b, ease(ease_type, next_frac)))  # Lightweight rendering needs >0 size.
        next_target_time = lerp(target_time_a, target_time_b, next_frac)

        base_a = get_alpha((last_target_time + next_target_time) / 2) * Options.connector_alpha

        layout = layout_slide_connector_segment(
            start_lane=last_lane,
            start_size=last_size,
            start_travel=last_travel,
            end_lane=next_lane,
            end_size=next_size,
            end_travel=next_travel,
        )

        if sprites.custom_available:
            if Options.connector_animation and visual_state == SlideVisualState.ACTIVE:
                active_a = ease_out_cubic((sin(time() * 2 * pi) + 1) / 2)
                sprites.active.draw(layout, z=z, a=base_a * active_a)
                sprites.normal.draw(layout, z=z + 1, a=base_a * (1 - active_a))
            else:
                sprites.normal.draw(layout, z=z, a=base_a * (1 if visual_state != SlideVisualState.INACTIVE else 0.5))
        else:
            sprites.fallback.draw(layout, z=z, a=base_a * (1 if visual_state != SlideVisualState.INACTIVE else 0.5))

        last_travel = next_travel
        last_lane = next_lane
        last_size = next_size
        last_target_time = next_target_time


def draw_guide(
    color: GuideColor,
    fade_type: GuideFadeType,
    ease_type: EaseType,
    quality: int,
    lane_a: float,
    size_a: float,
    progress_a: float,
    overall_progress_a: float,
    target_time_a: float,
    lane_b: float,
    size_b: float,
    progress_b: float,
    overall_progress_b: float,
    target_time_b: float,
):
    if progress_a < Layout.progress_start and progress_b < Layout.progress_start:
        return
    if progress_a > Layout.progress_cutoff and progress_b > Layout.progress_cutoff:
        return
    if progress_a == progress_b:
        return
    if time() >= target_time_b:
        return

    sprites = get_guide_sprites(color)

    start_progress = clamp(progress_a if time() < target_time_a else 1, Layout.progress_start, Layout.progress_cutoff)
    end_progress = clamp(progress_b, Layout.progress_start, Layout.progress_cutoff)
    start_frac = unlerp(progress_a, progress_b, start_progress)
    end_frac = unlerp(progress_a, progress_b, end_progress)

    start_travel = approach(start_progress)
    end_travel = approach(end_progress)
    start_lane = lerp(lane_a, lane_b, ease(ease_type, start_frac))
    end_lane = lerp(lane_a, lane_b, ease(ease_type, end_frac))
    start_screen_center = transformed_vec_at(start_lane, start_travel)
    end_screen_center = transformed_vec_at(end_lane, end_travel)
    dist = (end_screen_center - start_screen_center).magnitude  # Lower bound since with easing it can be longer.
    segment_count = min(ceil(quality * dist * CONNECTOR_QUALITY_SCALE), quality)

    last_overall_progress = lerp(overall_progress_a, overall_progress_b, start_frac)
    last_travel = start_travel
    last_lane = start_lane
    last_size = lerp(size_a, size_b, ease(ease_type, start_frac))
    last_target_time = lerp(target_time_a, target_time_b, start_frac)

    z = get_z(
        LAYER_NOTE_GUIDE,
        time=target_time_a,
        lane=lane_a,
        etc=color,
    )

    for i in range(1, segment_count + 1):
        next_frac = lerp(start_frac, end_frac, i / segment_count)
        next_progress = lerp(progress_a, progress_b, next_frac)
        next_overall_progress = lerp(overall_progress_a, overall_progress_b, next_frac)
        next_travel = approach(next_progress)
        next_lane = lerp(lane_a, lane_b, ease(ease_type, next_frac))
        next_size = lerp(size_a, size_b, ease(ease_type, next_frac))
        next_target_time = lerp(target_time_a, target_time_b, next_frac)

        a = get_alpha((last_target_time + next_target_time) / 2) * get_guide_alpha(
            fade_type, (last_overall_progress + next_overall_progress) / 2
        )

        layout = layout_slide_connector_segment(
            start_lane=last_lane,
            start_size=last_size,
            start_travel=last_travel,
            end_lane=next_lane,
            end_size=next_size,
            end_travel=next_travel,
        )

        if sprites.custom_available:
            sprites.normal.draw(layout, z=z, a=a)
        else:
            sprites.fallback.draw(layout, z=z, a=a)

        last_overall_progress = next_overall_progress
        last_travel = next_travel
        last_lane = next_lane
        last_size = next_size
        last_target_time = next_target_time
