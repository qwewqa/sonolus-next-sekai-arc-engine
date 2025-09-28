from enum import IntEnum
from math import ceil, cos, pi
from typing import Literal, assert_never

from sonolus.script.archetype import EntityRef
from sonolus.script.easing import ease_out_cubic
from sonolus.script.effect import Effect, LoopedEffectHandle
from sonolus.script.interval import clamp, lerp, remap, remap_clamped, unlerp_clamped
from sonolus.script.particle import Particle, ParticleHandle
from sonolus.script.quad import Quad, QuadLike
from sonolus.script.record import Record
from sonolus.script.runtime import time
from sonolus.script.sprite import Sprite
from sonolus.script.timing import beat_to_time

from sekai.lib.ease import EaseType, ease
from sekai.lib.effect import Effects
from sekai.lib.layer import (
    LAYER_ACTIVE_SIDE_CONNECTOR,
    LAYER_GUIDE_CONNECTOR,
    LAYER_SLOT_GLOW_EFFECT,
    get_z,
)
from sekai.lib.layout import (
    CONNECTOR_APPROACH_CUTOFF,
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
    ActiveConnectorSprites,
    GuideSprites,
    Skin,
    black_guide_sprites,
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
from sekai.lib.timescale import iter_timescale_changes_in_group_after_time_inclusive

CONNECTOR_TRAIL_SPAWN_PERIOD = 0.1
CONNECTOR_SLOT_SPAWN_PERIOD = 0.2


class ConnectorKind(IntEnum):
    NONE = 0

    ACTIVE_NORMAL = 1
    ACTIVE_CRITICAL = 2
    ACTIVE_FAKE_NORMAL = 51
    ACTIVE_FAKE_CRITICAL = 52

    GUIDE_NEUTRAL = 101
    GUIDE_RED = 102
    GUIDE_GREEN = 103
    GUIDE_BLUE = 104
    GUIDE_YELLOW = 105
    GUIDE_PURPLE = 106
    GUIDE_CYAN = 107
    GUIDE_BLACK = 108


ActiveConnectorKind = Literal[
    ConnectorKind.ACTIVE_NORMAL,
    ConnectorKind.ACTIVE_CRITICAL,
    ConnectorKind.ACTIVE_FAKE_NORMAL,
    ConnectorKind.ACTIVE_FAKE_CRITICAL,
]

GuideConnectorKind = Literal[
    ConnectorKind.GUIDE_NEUTRAL,
    ConnectorKind.GUIDE_RED,
    ConnectorKind.GUIDE_GREEN,
    ConnectorKind.GUIDE_BLUE,
    ConnectorKind.GUIDE_YELLOW,
    ConnectorKind.GUIDE_PURPLE,
    ConnectorKind.GUIDE_CYAN,
    ConnectorKind.GUIDE_BLACK,
]


class ConnectorVisualState(IntEnum):
    WAITING = 0
    INACTIVE = 1
    ACTIVE = 2


def get_active_connector_sprites(kind: ActiveConnectorKind) -> ActiveConnectorSprites:
    result = +ActiveConnectorSprites
    match kind:
        case ConnectorKind.ACTIVE_NORMAL | ConnectorKind.ACTIVE_FAKE_NORMAL:
            result @= normal_slide_connector_sprites
        case ConnectorKind.ACTIVE_CRITICAL | ConnectorKind.ACTIVE_FAKE_CRITICAL:
            result @= critical_slide_connector_sprites
        case _:
            assert_never(kind)
    return result


def get_guide_connector_sprites(kind: GuideConnectorKind) -> GuideSprites:
    result = +GuideSprites
    match kind:
        case ConnectorKind.GUIDE_NEUTRAL:
            result @= neutral_guide_sprites
        case ConnectorKind.GUIDE_RED:
            result @= red_guide_sprites
        case ConnectorKind.GUIDE_GREEN:
            result @= green_guide_sprites
        case ConnectorKind.GUIDE_BLUE:
            result @= blue_guide_sprites
        case ConnectorKind.GUIDE_YELLOW:
            result @= yellow_guide_sprites
        case ConnectorKind.GUIDE_PURPLE:
            result @= purple_guide_sprites
        case ConnectorKind.GUIDE_CYAN:
            result @= cyan_guide_sprites
        case ConnectorKind.GUIDE_BLACK:
            result @= black_guide_sprites
        case _:
            assert_never(kind)
    return result


def get_connector_z(kind: ConnectorKind, target_time: float, lane: float) -> float:
    match kind:
        case (
            ConnectorKind.ACTIVE_NORMAL
            | ConnectorKind.ACTIVE_FAKE_NORMAL
            | ConnectorKind.ACTIVE_CRITICAL
            | ConnectorKind.ACTIVE_FAKE_CRITICAL
        ):
            return get_z(
                LAYER_ACTIVE_SIDE_CONNECTOR, time=-target_time, lane=lane, etc=get_active_connector_z_offset(kind)
            )
        case (
            ConnectorKind.GUIDE_NEUTRAL
            | ConnectorKind.GUIDE_RED
            | ConnectorKind.GUIDE_GREEN
            | ConnectorKind.GUIDE_BLUE
            | ConnectorKind.GUIDE_YELLOW
            | ConnectorKind.GUIDE_PURPLE
            | ConnectorKind.GUIDE_CYAN
            | ConnectorKind.GUIDE_BLACK
        ):
            return get_z(LAYER_GUIDE_CONNECTOR, time=-target_time, lane=lane, etc=kind - ConnectorKind.GUIDE_NEUTRAL)
        case ConnectorKind.NONE:
            return 0.0
        case _:
            assert_never(kind)


def get_active_connector_z_offset(kind: ActiveConnectorKind) -> int:
    match kind:
        case ConnectorKind.ACTIVE_NORMAL | ConnectorKind.ACTIVE_FAKE_NORMAL:
            return 10
        case ConnectorKind.ACTIVE_CRITICAL | ConnectorKind.ACTIVE_FAKE_CRITICAL:
            return 0
        case _:
            assert_never(kind)


def get_connector_alpha_option(kind: ConnectorKind) -> float:
    match kind:
        case (
            ConnectorKind.ACTIVE_NORMAL
            | ConnectorKind.ACTIVE_FAKE_NORMAL
            | ConnectorKind.ACTIVE_CRITICAL
            | ConnectorKind.ACTIVE_FAKE_CRITICAL
        ):
            return Options.slide_alpha
        case (
            ConnectorKind.GUIDE_NEUTRAL
            | ConnectorKind.GUIDE_RED
            | ConnectorKind.GUIDE_GREEN
            | ConnectorKind.GUIDE_BLUE
            | ConnectorKind.GUIDE_YELLOW
            | ConnectorKind.GUIDE_PURPLE
            | ConnectorKind.GUIDE_CYAN
            | ConnectorKind.GUIDE_BLACK
        ):
            return Options.guide_alpha
        case ConnectorKind.NONE:
            return 0.0
        case _:
            assert_never(kind)


def get_connector_quality_option(kind: ConnectorKind) -> float:
    match kind:
        case (
            ConnectorKind.ACTIVE_NORMAL
            | ConnectorKind.ACTIVE_FAKE_NORMAL
            | ConnectorKind.ACTIVE_CRITICAL
            | ConnectorKind.ACTIVE_FAKE_CRITICAL
        ):
            return Options.slide_quality
        case (
            ConnectorKind.GUIDE_NEUTRAL
            | ConnectorKind.GUIDE_RED
            | ConnectorKind.GUIDE_GREEN
            | ConnectorKind.GUIDE_BLUE
            | ConnectorKind.GUIDE_YELLOW
            | ConnectorKind.GUIDE_PURPLE
            | ConnectorKind.GUIDE_CYAN
            | ConnectorKind.GUIDE_BLACK
        ):
            return Options.guide_quality
        case ConnectorKind.NONE:
            return 0
        case _:
            assert_never(kind)


def draw_connector(
    kind: ConnectorKind,
    visual_state: ConnectorVisualState,
    ease_type: EaseType,
    head_lane: float,
    head_size: float,
    head_progress: float,
    head_target_time: float,
    head_is_segment_head: bool,
    tail_lane: float,
    tail_size: float,
    tail_progress: float,
    tail_target_time: float,
    tail_is_segment_tail: bool,
    segment_head_target_time: float,
    segment_head_lane: float,
    segment_head_alpha: float,
    segment_tail_target_time: float,
    segment_tail_alpha: float,
):
    if time() < head_target_time and (
        (head_progress < Layout.progress_start and tail_progress < Layout.progress_start)
        or (head_progress > Layout.progress_cutoff and tail_progress > Layout.progress_cutoff)
        or head_progress == tail_progress
    ):
        return

    normal_sprite = Sprite(-1)
    active_sprite = Sprite(-1)
    match kind:
        case (
            ConnectorKind.ACTIVE_NORMAL
            | ConnectorKind.ACTIVE_CRITICAL
            | ConnectorKind.ACTIVE_FAKE_NORMAL
            | ConnectorKind.ACTIVE_FAKE_CRITICAL
        ):
            sprites = get_active_connector_sprites(kind)
            if sprites.custom_available:
                normal_sprite @= sprites.normal
                active_sprite @= sprites.active
            else:
                normal_sprite @= sprites.fallback
        case (
            ConnectorKind.GUIDE_NEUTRAL
            | ConnectorKind.GUIDE_RED
            | ConnectorKind.GUIDE_GREEN
            | ConnectorKind.GUIDE_BLUE
            | ConnectorKind.GUIDE_YELLOW
            | ConnectorKind.GUIDE_PURPLE
            | ConnectorKind.GUIDE_CYAN
            | ConnectorKind.GUIDE_BLACK
        ):
            sprites = get_guide_connector_sprites(kind)
            if sprites.custom_available:
                normal_sprite @= sprites.normal
            else:
                normal_sprite @= sprites.fallback
        case ConnectorKind.NONE:
            return
        case _:
            assert_never(kind)

    match kind:
        case ConnectorKind.ACTIVE_NORMAL | ConnectorKind.ACTIVE_CRITICAL:
            segment_head_alpha = 1.0
            segment_tail_alpha = 1.0
        case ConnectorKind.ACTIVE_FAKE_NORMAL | ConnectorKind.ACTIVE_FAKE_CRITICAL:
            segment_head_alpha = 1.0
            segment_tail_alpha = 1.0
            if visual_state == ConnectorVisualState.INACTIVE:
                visual_state = ConnectorVisualState.ACTIVE
        case (
            ConnectorKind.GUIDE_NEUTRAL
            | ConnectorKind.GUIDE_RED
            | ConnectorKind.GUIDE_GREEN
            | ConnectorKind.GUIDE_BLUE
            | ConnectorKind.GUIDE_YELLOW
            | ConnectorKind.GUIDE_PURPLE
            | ConnectorKind.GUIDE_CYAN
            | ConnectorKind.GUIDE_BLACK
        ):
            visual_state = ConnectorVisualState.WAITING
        case _:
            assert_never(kind)

    head_alpha = remap_clamped(
        segment_head_target_time, segment_tail_target_time, segment_head_alpha, segment_tail_alpha, head_target_time
    )
    tail_alpha = remap_clamped(
        segment_head_target_time, segment_tail_target_time, segment_head_alpha, segment_tail_alpha, tail_target_time
    )

    if time() >= tail_target_time:
        return
    if time() >= head_target_time:
        head_frac = unlerp_clamped(head_target_time, tail_target_time, time())
        head_progress = remap(head_frac, 1.0, 1.0, tail_progress, 0.0)
        start_progress = clamp(
            1.0, Layout.progress_start, min(Layout.progress_cutoff, CONNECTOR_APPROACH_CUTOFF)
        )  # Accounts for hidden
        head_is_segment_head = True  # Treat it as if it is since it's visible
    else:
        start_progress = clamp(
            head_progress, Layout.progress_start, min(Layout.progress_cutoff, CONNECTOR_APPROACH_CUTOFF)
        )
    end_progress = clamp(tail_progress, Layout.progress_start, min(Layout.progress_cutoff, CONNECTOR_APPROACH_CUTOFF))
    start_frac = unlerp_clamped(head_progress, tail_progress, start_progress)
    end_frac = unlerp_clamped(head_progress, tail_progress, end_progress)

    eased_start_frac = ease(ease_type, start_frac)
    eased_end_frac = ease(ease_type, end_frac)
    start_travel = approach(start_progress)
    end_travel = approach(end_progress)
    start_lane = lerp(head_lane, tail_lane, eased_start_frac)
    end_lane = lerp(head_lane, tail_lane, eased_end_frac)
    start_size = max(1e-3, lerp(head_size, tail_size, eased_start_frac))  # Lightweight rendering needs >0 size.
    end_size = max(1e-3, lerp(head_size, tail_size, eased_end_frac))  # Lightweight rendering needs >0 size.
    start_alpha = lerp(head_alpha, tail_alpha, start_frac)
    end_alpha = lerp(head_alpha, tail_alpha, end_frac)

    pos_offset = 0
    for sl, el, hl, tl in (
        (start_lane - start_size, end_lane - end_size, head_lane - head_size, tail_lane - tail_size),
        (start_lane + start_size, end_lane + end_size, head_lane + head_size, tail_lane + tail_size),
    ):
        start_ref = transformed_vec_at(sl, start_travel)
        end_ref = transformed_vec_at(el, end_travel)
        pos_offset_this_side = 0
        for r in (0.25, 0.5, 0.75):
            frac = lerp(start_frac, end_frac, r)
            progress = lerp(start_progress, end_progress, r)
            travel = approach(progress)
            lane = lerp(hl, tl, ease(ease_type, frac))
            pos = transformed_vec_at(lane, travel)
            ref_pos = lerp(start_ref, end_ref, unlerp_clamped(start_travel, end_travel, travel))
            pos_offset_this_side += abs(pos.x - ref_pos.x)
        pos_offset = max(pos_offset, pos_offset_this_side)
    start_pos_y = transformed_vec_at(start_lane, start_travel).y
    end_pos_y = transformed_vec_at(end_lane, end_travel).y
    curve_change_scale = pos_offset**0.4 * 1.6
    alpha_change_scale = max(
        (abs(start_alpha - end_alpha) * get_connector_alpha_option(kind)) ** 0.8 * 3,
        (abs(start_alpha - end_alpha) * get_connector_alpha_option(kind)) ** 0.5 * abs(start_pos_y - end_pos_y) * 3,
    )
    quality = get_connector_quality_option(kind)
    segment_count = max(1, ceil(max(curve_change_scale, alpha_change_scale) * quality * 10))

    z = get_connector_z(kind, segment_head_target_time, segment_head_lane)

    last_travel = start_travel
    last_lane = start_lane
    last_size = start_size
    last_alpha = start_alpha
    last_target_time = lerp(head_target_time, tail_target_time, start_frac)

    for v_segment_i in range(1, segment_count + 1):
        next_frac = lerp(start_frac, end_frac, v_segment_i / segment_count)
        next_progress = lerp(start_progress, end_progress, v_segment_i / segment_count)
        next_travel = approach(next_progress)
        next_lane = lerp(head_lane, tail_lane, ease(ease_type, next_frac))
        next_size = max(1e-3, lerp(head_size, tail_size, ease(ease_type, next_frac)))
        next_alpha = lerp(head_alpha, tail_alpha, next_frac)
        next_target_time = lerp(head_target_time, tail_target_time, next_frac)

        base_a = (
            get_alpha((last_target_time + next_target_time) / 2)
            * (last_alpha + next_alpha)
            / 2
            * get_connector_alpha_option(kind)
        )

        start_arc_factor = 0.8
        end_arc_factor = 0.8
        if v_segment_i == 1 and (head_is_segment_head or abs(start_progress - Layout.progress_start) < 1e-3):
            start_arc_factor = 1.5
        if v_segment_i == segment_count and (tail_is_segment_tail or abs(end_progress - Layout.progress_cutoff) < 1e-3):
            end_arc_factor = 1.5
        start_arc_factor *= Options.arc_quality
        end_arc_factor *= Options.arc_quality
        start_arc_n = max(1, ceil(quality * Options.arc_quality * last_size * start_arc_factor))
        end_arc_n = max(1, ceil(quality * Options.arc_quality * next_size * end_arc_factor))
        arc_n = max(start_arc_n, end_arc_n)

        start_layout = layout_slide_connector_segment(
            start_lane=last_lane,
            start_size=last_size,
            start_travel=last_travel,
            end_lane=next_lane,
            end_size=next_size,
            end_travel=next_travel,
            n=start_arc_n,
        )
        end_layout = layout_slide_connector_segment(
            start_lane=last_lane,
            start_size=last_size,
            start_travel=last_travel,
            end_lane=next_lane,
            end_size=next_size,
            end_travel=next_travel,
            n=end_arc_n,
        )

        start_segment_i = 0
        end_segment_i = 0
        start_segment = +Quad
        end_segment = +Quad
        start_subsegment_i = 0
        end_subsegment_i = 0
        start_subsegment_n = 0
        end_subsegment_n = 0
        for h_segment_i in range(arc_n):
            if h_segment_i * start_arc_n >= start_segment_i * arc_n:
                start_segment @= next(start_layout)
                start_segment_i += 1
                start_subsegment_i = 0
                succeeding_h_segment_i = ceil(start_segment_i * arc_n / start_arc_n)
                # Paranoia about rounding errors
                if succeeding_h_segment_i * start_arc_n >= (start_segment_i + 1) * arc_n:
                    succeeding_h_segment_i -= 1
                elif succeeding_h_segment_i * start_arc_n < start_segment_i * arc_n:
                    succeeding_h_segment_i += 1
                start_subsegment_n = succeeding_h_segment_i - h_segment_i
            else:
                start_subsegment_i += 1
            if h_segment_i * end_arc_n >= end_segment_i * arc_n:
                end_segment @= next(end_layout)
                end_segment_i += 1
                end_subsegment_i = 0
                succeeding_h_segment_i = ceil(end_segment_i * arc_n / end_arc_n)
                if succeeding_h_segment_i * end_arc_n >= (end_segment_i + 1) * arc_n:
                    succeeding_h_segment_i -= 1
                elif succeeding_h_segment_i * end_arc_n < end_segment_i * arc_n:
                    succeeding_h_segment_i += 1
                end_subsegment_n = succeeding_h_segment_i - h_segment_i
            else:
                end_subsegment_i += 1

            start_segment_l_frac = start_subsegment_i / start_subsegment_n
            start_segment_r_frac = (start_subsegment_i + 1) / start_subsegment_n
            end_segment_l_frac = end_subsegment_i / end_subsegment_n
            end_segment_r_frac = (end_subsegment_i + 1) / end_subsegment_n

            segment = Quad(
                bl=lerp(start_segment.bl, start_segment.br, start_segment_l_frac),
                br=lerp(start_segment.bl, start_segment.br, start_segment_r_frac),
                tl=lerp(end_segment.tl, end_segment.tr, end_segment_l_frac),
                tr=lerp(end_segment.tl, end_segment.tr, end_segment_r_frac),
            )

            if visual_state == ConnectorVisualState.ACTIVE and active_sprite.is_available:
                if Options.connector_animation:
                    a_modifier = (cos(2 * pi * time()) + 1) / 2
                    normal_sprite.draw(segment, z=z + 1 / 128, a=base_a * ease_out_cubic(a_modifier))
                    active_sprite.draw(segment, z=z, a=base_a * ease_out_cubic(1 - a_modifier))
                else:
                    active_sprite.draw(segment, z=z, a=base_a)
            else:
                normal_sprite.draw(
                    segment, z=z, a=base_a * (1 if visual_state != ConnectorVisualState.INACTIVE else 0.5)
                )
        last_travel = next_travel
        last_lane = next_lane
        last_size = next_size
        last_alpha = next_alpha
        last_target_time = next_target_time


class ActiveConnectorInfo(Record):
    visual_lane: float
    visual_size: float
    input_lane: float
    input_size: float
    prev_input_lane: float
    prev_input_size: float
    is_active: bool
    active_start_time: float
    connector_kind: ConnectorKind

    def get_hitbox(self, leniency: float) -> Quad:
        return layout_hitbox(
            self.input_lane - self.input_size - leniency,
            self.input_lane + self.input_size + leniency,
        )

    def get_prev_hitbox(self, leniency: float) -> Quad:
        return layout_hitbox(
            self.prev_input_lane - self.prev_input_size - leniency,
            self.prev_input_lane + self.prev_input_size + leniency,
        )


def update_circular_connector_particle(
    handle: ParticleHandle,
    kind: ActiveConnectorKind,
    lane: float,
    replace: bool,
):
    if not Options.note_effect_enabled:
        return
    layout = layout_circular_effect(lane, w=3.5, h=2.1, y_offset=0.1)
    if replace or handle.id == 0:
        particle = +Particle(-1)
        match kind:
            case ConnectorKind.ACTIVE_NORMAL | ConnectorKind.ACTIVE_FAKE_NORMAL:
                particle @= Particles.normal_slide_connector_circular
            case ConnectorKind.ACTIVE_CRITICAL | ConnectorKind.ACTIVE_FAKE_CRITICAL:
                particle @= Particles.critical_slide_connector_circular
            case _:
                assert_never(kind)
        replace_looped_particle(handle, particle, layout, duration=1)
    else:
        update_looped_particle(handle, layout)


def update_linear_connector_particle(
    handle: ParticleHandle,
    kind: ActiveConnectorKind,
    lane: float,
    replace: bool,
):
    if not Options.note_effect_enabled:
        return
    layout = layout_linear_effect(lane, shear=0)
    particle = +Particle
    if replace or handle.id == 0:
        match kind:
            case ConnectorKind.ACTIVE_NORMAL | ConnectorKind.ACTIVE_FAKE_NORMAL:
                particle @= Particles.normal_slide_connector_linear
            case ConnectorKind.ACTIVE_CRITICAL | ConnectorKind.ACTIVE_FAKE_CRITICAL:
                particle @= Particles.critical_slide_connector_linear
            case _:
                assert_never(kind)
        replace_looped_particle(handle, particle, layout, duration=1)
    else:
        update_looped_particle(handle, layout)


def spawn_linear_connector_trail_particle(
    kind: ActiveConnectorKind,
    lane: float,
):
    if not Options.note_effect_enabled:
        return
    layout = layout_linear_effect(lane, shear=0)
    particle = +Particle
    match kind:
        case ConnectorKind.ACTIVE_NORMAL | ConnectorKind.ACTIVE_FAKE_NORMAL:
            particle @= Particles.normal_slide_connector_trail_linear
        case ConnectorKind.ACTIVE_CRITICAL | ConnectorKind.ACTIVE_FAKE_CRITICAL:
            particle @= Particles.critical_slide_connector_trail_linear
        case _:
            assert_never(kind)
    particle.spawn(layout, duration=0.5)


def spawn_connector_slot_particles(
    kind: ActiveConnectorKind,
    lane: float,
    size: float,
):
    if not Options.note_effect_enabled:
        return
    particle = +Particle
    match kind:
        case ConnectorKind.ACTIVE_NORMAL | ConnectorKind.ACTIVE_FAKE_NORMAL:
            particle @= Particles.normal_slide_connector_slot_linear
        case ConnectorKind.ACTIVE_CRITICAL | ConnectorKind.ACTIVE_FAKE_CRITICAL:
            particle @= Particles.critical_slide_connector_slot_linear
        case _:
            assert_never(kind)
    for slot_lane in iter_slot_lanes(lane, size):
        layout = layout_linear_effect(slot_lane, shear=0)
        particle.spawn(layout, duration=0.5)


def draw_connector_slot_glow_effect(
    kind: ActiveConnectorKind,
    start_time: float,
    lane: float,
    size: float,
):
    sprite = +Sprite
    match kind:
        case ConnectorKind.ACTIVE_NORMAL | ConnectorKind.ACTIVE_FAKE_NORMAL:
            sprite @= Skin.normal_slide_connector_slot_glow
        case ConnectorKind.ACTIVE_CRITICAL | ConnectorKind.ACTIVE_FAKE_CRITICAL:
            sprite @= Skin.critical_slide_connector_slot_glow
        case _:
            assert_never(kind)
    height = (3.25 + (cos((time() - start_time) * 8 * pi) + 1) / 2) / 4.25
    layout = layout_slot_glow_effect(lane, size, height)
    z = get_z(LAYER_SLOT_GLOW_EFFECT, -start_time, lane)
    a = remap_clamped(start_time, start_time + 0.25, 0.0, 0.3, time())
    for segment in layout:
        sprite.draw(segment, z=z, a=a)


def update_connector_sfx(
    handle: LoopedEffectHandle,
    kind: ActiveConnectorKind,
    replace: bool,
):
    if not Options.sfx_enabled:
        return
    if Options.auto_sfx:
        return
    effect = +Effect
    match kind:
        case ConnectorKind.ACTIVE_NORMAL | ConnectorKind.ACTIVE_FAKE_NORMAL:
            effect @= Effects.normal_hold
        case ConnectorKind.ACTIVE_CRITICAL | ConnectorKind.ACTIVE_FAKE_CRITICAL:
            effect @= Effects.critical_hold
        case _:
            assert_never(kind)
    if replace:
        replace_looped_sfx(handle, effect)
    elif handle.id == 0:
        handle @= effect.loop()


def schedule_connector_sfx(
    kind: ActiveConnectorKind,
    timescale_group: int | EntityRef,
    start_time: float,
    end_time: float,
):
    if not Options.sfx_enabled:
        return
    effect = +Effect
    match kind:
        case ConnectorKind.ACTIVE_NORMAL | ConnectorKind.ACTIVE_FAKE_NORMAL:
            effect @= Effects.normal_hold
        case ConnectorKind.ACTIVE_CRITICAL | ConnectorKind.ACTIVE_FAKE_CRITICAL:
            effect @= Effects.critical_hold
        case _:
            assert_never(kind)
    last_start_time = start_time
    hide = False
    for group in iter_timescale_changes_in_group_after_time_inclusive(timescale_group, start_time):
        group_time = beat_to_time(group.beat)
        if group_time >= end_time:
            break
        if hide and not group.hide_notes:
            last_start_time = group_time
        elif not hide and group.hide_notes and group_time > last_start_time:
            schedule_looped_sfx(effect, last_start_time, group_time)
        hide = group.hide_notes
    if not hide and end_time > last_start_time:
        schedule_looped_sfx(effect, last_start_time, end_time)


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
