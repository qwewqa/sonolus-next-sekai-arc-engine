from enum import IntEnum
from math import ceil, cos, pi
from typing import assert_never

from sonolus.script.easing import ease_out_cubic
from sonolus.script.effect import Effect, LoopedEffectHandle
from sonolus.script.interval import clamp, lerp, remap_clamped, unlerp
from sonolus.script.particle import Particle, ParticleHandle
from sonolus.script.quad import QuadLike, Rect
from sonolus.script.record import Record
from sonolus.script.runtime import time
from sonolus.script.sprite import Sprite

from sekai.lib.ease import EaseType, ease
from sekai.lib.effect import Effects
from sekai.lib.layer import (
    LAYER_NOTE_CONNECTOR,
    LAYER_NOTE_CONNECTOR_CRITICAL,
    LAYER_NOTE_GUIDE,
    LAYER_SLOT_GLOW_EFFECT,
    get_z,
)
from sekai.lib.layout import (
    Layout,
    approach,
    get_alpha,
    iter_slot_lanes,
    layout_circular_effect,
    layout_hitbox,
    layout_linear_effect,
    layout_slide_connector_segment,
    layout_slot_glow_effect,
    transformed_vec_at,
)
from sekai.lib.options import Options
from sekai.lib.particle import Particles
from sekai.lib.skin import (
    ConnectorSprites,
    GuideSprites,
    Skin,
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

CONNECTOR_QUALITY_SCALE = 3.0

CONNECTOR_TRAIL_SPAWN_PERIOD = 0.1
CONNECTOR_SLOT_SPAWN_PERIOD = 0.2


class SlideConnectorKind(IntEnum):
    NONE = 0
    NORMAL = 1
    CRITICAL = 2


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
        case SlideConnectorKind.NONE:
            pass
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
    start_size = max(1e-3, lerp(size_a, size_b, ease(ease_type, start_frac)))  # Lightweight rendering needs >0 size.
    end_size = max(1e-3, lerp(size_a, size_b, ease(ease_type, end_frac)))
    start_screen_center = transformed_vec_at(start_lane, start_travel)
    end_screen_center = transformed_vec_at(end_lane, end_travel)
    x_change = (
        max(
            abs((start_lane - start_size) - (end_lane - end_size)),
            abs((start_lane + start_size) - (end_lane + end_size)),
        )
        * max(start_travel, end_travel)
        * Layout.w_scale
    )
    y_change = abs(start_screen_center.y - end_screen_center.y)
    if Options.fade_out:
        change_scale = max(x_change, y_change)
    else:
        change_scale = min(x_change, y_change)
        if ease_type == EaseType.LINEAR:
            # Linear still curves due to the approach curve, but less, so we need fewer segments.
            change_scale /= 3
    segment_count = min(max(1, ceil(quality * change_scale * CONNECTOR_QUALITY_SCALE)), quality)

    last_travel = start_travel
    last_lane = start_lane
    last_size = start_size
    last_target_time = lerp(target_time_a, target_time_b, start_frac)

    z = get_z(
        LAYER_NOTE_CONNECTOR if kind != SlideConnectorKind.CRITICAL else LAYER_NOTE_CONNECTOR_CRITICAL,
        time=-target_time_a,
        lane=lane_a,
    )

    for i in range(1, segment_count + 1):
        next_frac = lerp(start_frac, end_frac, i / segment_count)
        next_progress = lerp(progress_a, progress_b, next_frac)
        next_travel = approach(next_progress)
        next_lane = lerp(lane_a, lane_b, ease(ease_type, next_frac))
        next_size = max(1e-3, lerp(size_a, size_b, ease(ease_type, next_frac)))
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
                a_modifier = (cos(2 * pi * time()) + 1) / 2
                sprites.normal.draw(layout, z=z, a=base_a * ease_out_cubic(a_modifier))
                sprites.active.draw(layout, z=z, a=base_a * ease_out_cubic(1 - a_modifier))
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
    start_size = max(1e-3, lerp(size_a, size_b, ease(ease_type, start_frac)))  # Lightweight rendering needs >0 size.
    end_size = max(1e-3, lerp(size_a, size_b, ease(ease_type, end_frac)))
    start_overall_progress = lerp(overall_progress_a, overall_progress_b, start_frac)
    end_overall_progress = lerp(overall_progress_a, overall_progress_b, end_frac)
    start_screen_center = transformed_vec_at(start_lane, start_travel)
    end_screen_center = transformed_vec_at(end_lane, end_travel)
    x_change = (
        max(
            abs((start_lane - start_size) - (end_lane - end_size)),
            abs((start_lane + start_size) - (end_lane + end_size)),
        )
        * max(start_travel, end_travel)
        * Layout.w_scale
    )
    y_change = abs(start_screen_center.y - end_screen_center.y)
    if Options.fade_out:
        change_scale = max(x_change, y_change)
    elif fade_type != GuideFadeType.NONE:
        change_scale = max(
            x_change,
            min(y_change, abs(start_overall_progress - end_overall_progress)),
        )
    else:
        change_scale = min(x_change, y_change)
        if ease_type == EaseType.LINEAR:
            # Linear still curves due to the approach curve, but less, so we need fewer segments.
            change_scale /= 3
    segment_count = min(max(1, ceil(quality * change_scale * CONNECTOR_QUALITY_SCALE)), quality)

    last_overall_progress = lerp(overall_progress_a, overall_progress_b, start_frac)
    last_travel = start_travel
    last_lane = start_lane
    last_size = start_size
    last_target_time = lerp(target_time_a, target_time_b, start_frac)

    z = get_z(
        LAYER_NOTE_GUIDE,
        time=-target_time_a,
        lane=lane_a,
        etc=color,
    )

    for i in range(1, segment_count + 1):
        next_frac = lerp(start_frac, end_frac, i / segment_count)
        next_progress = lerp(progress_a, progress_b, next_frac)
        next_overall_progress = lerp(overall_progress_a, overall_progress_b, next_frac)
        next_travel = approach(next_progress)
        next_lane = lerp(lane_a, lane_b, ease(ease_type, next_frac))
        next_size = max(1e-3, lerp(size_a, size_b, ease(ease_type, next_frac)))
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


def get_attached_params(
    ease_type: EaseType,
    lane_a: float,
    size_a: float,
    progress_a: float,
    lane_b: float,
    size_b: float,
    progress_b: float,
) -> tuple[float, float]:
    if (progress_a > 1 and progress_b > 1) or (progress_a < 1 and progress_b < 1):
        # This is an ill-behaved connector where it's entirely above or below the judgment line when the
        # attached tick is supposed to be at the judgment line.
        # Charts should not do this, but we'll still do this to handle it gracefully.
        frac = 0.5
    elif abs(progress_a - progress_b) < 1e-6:
        frac = 0.5
    else:
        frac = unlerp(progress_a, progress_b, 1)
    eased_frac = ease(ease_type, frac)
    lane = lerp(lane_a, lane_b, eased_frac)
    size = lerp(size_a, size_b, eased_frac)
    return lane, size


class ActiveConnectorInfo(Record):
    visual_lane: float
    visual_size: float
    input_lane: float
    input_size: float
    is_active: bool
    active_start_time: float
    connector_kind: SlideConnectorKind

    def get_hitbox(self, leniency: float) -> Rect:
        return layout_hitbox(
            self.input_lane - self.input_size - leniency,
            self.input_lane + self.input_size + leniency,
        )


def update_circular_connector_particle(
    handle: ParticleHandle,
    kind: SlideConnectorKind,
    lane: float,
    replace: bool,
):
    if not Options.note_effect_enabled:
        return
    layout = layout_circular_effect(lane, w=3.5, h=2.1)
    if replace:
        particle = +Particle
        match kind:
            case SlideConnectorKind.NONE:
                return
            case SlideConnectorKind.NORMAL:
                particle @= Particles.normal_slide_connector_circular
            case SlideConnectorKind.CRITICAL:
                particle @= Particles.critical_slide_connector_circular
            case _:
                assert_never(kind)
        replace_looped_particle(handle, particle, layout, duration=1)
    else:
        update_looped_particle(handle, layout)


def update_linear_connector_particle(
    handle: ParticleHandle,
    kind: SlideConnectorKind,
    lane: float,
    replace: bool,
):
    if not Options.note_effect_enabled:
        return
    layout = layout_linear_effect(lane, shear=0)
    particle = +Particle
    if replace:
        match kind:
            case SlideConnectorKind.NONE:
                return
            case SlideConnectorKind.NORMAL:
                particle @= Particles.normal_slide_connector_linear
            case SlideConnectorKind.CRITICAL:
                particle @= Particles.critical_slide_connector_linear
            case _:
                assert_never(kind)
        replace_looped_particle(handle, particle, layout, duration=1)
    else:
        update_looped_particle(handle, layout)


def spawn_linear_connector_trail_particle(
    kind: SlideConnectorKind,
    lane: float,
):
    if not Options.note_effect_enabled:
        return
    layout = layout_linear_effect(lane, shear=0)
    particle = +Particle
    match kind:
        case SlideConnectorKind.NONE:
            return
        case SlideConnectorKind.NORMAL:
            particle @= Particles.normal_slide_connector_trail_linear
        case SlideConnectorKind.CRITICAL:
            particle @= Particles.critical_slide_connector_trail_linear
        case _:
            assert_never(kind)
    particle.spawn(layout, duration=0.5)


def spawn_connector_slot_particles(
    kind: SlideConnectorKind,
    lane: float,
    size: float,
):
    particle = +Particle
    match kind:
        case SlideConnectorKind.NONE:
            return
        case SlideConnectorKind.NORMAL:
            particle @= Particles.normal_slide_connector_slot_linear
        case SlideConnectorKind.CRITICAL:
            particle @= Particles.critical_slide_connector_slot_linear
        case _:
            assert_never(kind)
    for slot_lane in iter_slot_lanes(lane, size):
        layout = layout_linear_effect(slot_lane, shear=0)
        particle.spawn(layout, duration=0.5)


def draw_connector_slot_glow_effect(
    kind: SlideConnectorKind,
    start_time: float,
    lane: float,
    size: float,
):
    sprite = +Sprite
    match kind:
        case SlideConnectorKind.NONE:
            return
        case SlideConnectorKind.NORMAL:
            sprite @= Skin.normal_slide_connector_slot_glow
        case SlideConnectorKind.CRITICAL:
            sprite @= Skin.critical_slide_connector_slot_glow
        case _:
            assert_never(kind)
    height = (3.25 + (cos((time() - start_time) * 8 * pi) + 1) / 2) / 4.25
    layout = layout_slot_glow_effect(lane, size, height)
    z = get_z(LAYER_SLOT_GLOW_EFFECT, -start_time, lane)
    a = remap_clamped(start_time, start_time + 0.25, 0.0, 0.3, time())
    sprite.draw(layout, z=z, a=a)


def update_connector_sfx(
    handle: LoopedEffectHandle,
    kind: SlideConnectorKind,
    replace: bool,
):
    if not Options.sfx_enabled:
        return
    if Options.auto_sfx:
        return
    effect = +Effect
    match kind:
        case SlideConnectorKind.NONE:
            return
        case SlideConnectorKind.NORMAL:
            effect @= Effects.normal_hold
        case SlideConnectorKind.CRITICAL:
            effect @= Effects.critical_hold
        case _:
            assert_never(kind)
    if replace:
        replace_looped_sfx(handle, effect)
    elif handle.id == 0:
        handle @= effect.loop()


def replace_looped_particle(handle: ParticleHandle, particle: Particle, layout: QuadLike, duration: float):
    if handle.id != 0:
        handle.destroy()
    handle @= particle.spawn(layout, duration, loop=True)


def update_looped_particle(handle: ParticleHandle, layout: QuadLike):
    if handle.id != 0:
        handle.move(layout)


def destroy_looped_particle(handle: ParticleHandle):
    if handle.id != 0:
        handle.destroy()
        handle.id = 0


def replace_looped_sfx(handle: LoopedEffectHandle, effect: Effect):
    if handle.id != 0:
        handle.stop()
    handle @= effect.loop()


def destroy_looped_sfx(handle: LoopedEffectHandle):
    if handle.id != 0:
        handle.stop()
        handle.id = 0


def schedule_looped_sfx(effect: Effect, start_time: float, end_time: float):
    effect.schedule_loop(start_time).stop(end_time)
