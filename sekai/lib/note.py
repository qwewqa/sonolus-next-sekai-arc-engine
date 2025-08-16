from enum import IntEnum, auto
from typing import assert_never

from sonolus.script.bucket import Bucket, JudgmentWindow
from sonolus.script.easing import ease_in_cubic
from sonolus.script.runtime import time

from sekai.lib.buckets import (
    FLICK_CRITICAL_WINDOW,
    FLICK_NORMAL_WINDOW,
    SLIDE_END_CRITICAL_WINDOW,
    SLIDE_END_FLICK_CRITICAL_WINDOW,
    SLIDE_END_FLICK_NORMAL_WINDOW,
    SLIDE_END_NORMAL_WINDOW,
    TAP_CRITICAL_WINDOW,
    TAP_NORMAL_WINDOW,
    TRACE_CRITICAL_WINDOW,
    TRACE_FLICK_CRITICAL_WINDOW,
    TRACE_FLICK_NORMAL_WINDOW,
    TRACE_NORMAL_WINDOW,
    Buckets,
)
from sekai.lib.layer import LAYER_NOTE_ARROW, LAYER_NOTE_BODY, LAYER_NOTE_SLIM_BODY, LAYER_NOTE_TICK, get_z
from sekai.lib.layout import (
    Layout,
    approach,
    get_alpha,
    layout_flick_arrow,
    layout_flick_arrow_fallback,
    layout_regular_note_body,
    layout_regular_note_body_fallback,
    layout_slim_note_body,
    layout_slim_note_body_fallback,
    layout_tick,
)
from sekai.lib.options import Options
from sekai.lib.skin import (
    ArrowSprites,
    BodySprites,
    TickSprites,
    critical_arrow_sprites,
    critical_note_body_sprites,
    critical_tick_sprites,
    critical_trace_note_body_sprites,
    damage_note_body_sprites,
    flick_note_body_sprites,
    flick_tick_sprites,
    normal_arrow_sprites,
    normal_note_body_sprites,
    normal_tick_sprites,
    normal_trace_note_body_sprites,
    slide_note_body_sprites,
    trace_flick_note_body_sprites,
    trace_slide_note_body_sprites,
)

FLICK_ARROW_PERIOD = 0.5


class NoteKind(IntEnum):
    NORM_TAP = auto()
    CRIT_TAP = auto()

    NORM_FLICK = auto()
    CRIT_FLICK = auto()

    NORM_TRACE = auto()
    CRIT_TRACE = auto()

    NORM_TRACE_FLICK = auto()
    CRIT_TRACE_FLICK = auto()

    NORM_RELEASE = auto()
    CRIT_RELEASE = auto()

    NORM_HEAD_TAP = auto()
    CRIT_HEAD_TAP = auto()

    NORM_HEAD_FLICK = auto()
    CRIT_HEAD_FLICK = auto()

    NORM_HEAD_TRACE = auto()
    CRIT_HEAD_TRACE = auto()

    NORM_HEAD_TRACE_FLICK = auto()
    CRIT_HEAD_TRACE_FLICK = auto()

    NORM_HEAD_RELEASE = auto()
    CRIT_HEAD_RELEASE = auto()

    NORM_TAIL_TAP = auto()
    CRIT_TAIL_TAP = auto()

    NORM_TAIL_FLICK = auto()
    CRIT_TAIL_FLICK = auto()

    NORM_TAIL_TRACE = auto()
    CRIT_TAIL_TRACE = auto()

    NORM_TAIL_TRACE_FLICK = auto()
    CRIT_TAIL_TRACE_FLICK = auto()

    NORM_TAIL_RELEASE = auto()
    CRIT_TAIL_RELEASE = auto()

    NORM_TICK = auto()
    CRIT_TICK = auto()
    HIDE_TICK = auto()

    JOINT = auto()

    DAMAGE = auto()


class Direction(IntEnum):
    LEFT = -1
    NONE = 0
    RIGHT = 1


def draw_note(kind: NoteKind, lane: float, size: float, progress: float, direction: int, target_time: float):
    if not Layout.progress_start <= progress <= Layout.progress_cutoff:
        return
    travel = approach(progress)
    draw_note_body(kind, lane, size, travel, target_time)
    draw_note_arrow(kind, lane, size, travel, target_time, direction)
    draw_note_tick(kind, lane, travel, target_time)


def draw_slide_note_head(kind: NoteKind, lane: float, size: float):
    draw_note_body(kind, lane, size, 1.0, time())
    draw_note_tick(kind, lane, 1.0, time())


def draw_note_body(kind: NoteKind, lane: float, size: float, travel: float, target_time: float):
    match kind:
        case NoteKind.NORM_TAP:
            _draw_regular_body(normal_note_body_sprites, lane, size, travel, target_time)
        case NoteKind.NORM_FLICK | NoteKind.NORM_HEAD_FLICK | NoteKind.NORM_TAIL_FLICK:
            _draw_regular_body(flick_note_body_sprites, lane, size, travel, target_time)
        case NoteKind.NORM_TRACE | NoteKind.NORM_HEAD_TRACE | NoteKind.NORM_TAIL_TRACE:
            _draw_slim_body(normal_trace_note_body_sprites, lane, size, travel, target_time)
        case NoteKind.NORM_TRACE_FLICK | NoteKind.NORM_HEAD_TRACE_FLICK | NoteKind.NORM_TAIL_TRACE_FLICK:
            _draw_slim_body(trace_flick_note_body_sprites, lane, size, travel, target_time)
        case (
            NoteKind.NORM_RELEASE
            | NoteKind.NORM_HEAD_TAP
            | NoteKind.NORM_HEAD_RELEASE
            | NoteKind.NORM_TAIL_TAP
            | NoteKind.NORM_TAIL_RELEASE
        ):
            _draw_regular_body(slide_note_body_sprites, lane, size, travel, target_time)
        case (
            NoteKind.CRIT_TAP
            | NoteKind.CRIT_FLICK
            | NoteKind.CRIT_RELEASE
            | NoteKind.CRIT_HEAD_TAP
            | NoteKind.CRIT_HEAD_FLICK
            | NoteKind.CRIT_HEAD_RELEASE
            | NoteKind.CRIT_TAIL_TAP
            | NoteKind.CRIT_TAIL_FLICK
            | NoteKind.CRIT_TAIL_RELEASE
        ):
            _draw_regular_body(critical_note_body_sprites, lane, size, travel, target_time)
        case (
            NoteKind.CRIT_TRACE
            | NoteKind.CRIT_HEAD_TRACE
            | NoteKind.CRIT_TAIL_TRACE
            | NoteKind.CRIT_TRACE_FLICK
            | NoteKind.CRIT_HEAD_TRACE_FLICK
            | NoteKind.CRIT_TAIL_TRACE_FLICK
        ):
            _draw_slim_body(critical_trace_note_body_sprites, lane, size, travel, target_time)
        case NoteKind.NORM_HEAD_TRACE | NoteKind.NORM_TAIL_TRACE:
            _draw_slim_body(trace_slide_note_body_sprites, lane, size, travel, target_time)
        case NoteKind.DAMAGE:
            _draw_slim_body(damage_note_body_sprites, lane, size, travel, target_time)
        case NoteKind.NORM_TICK | NoteKind.CRIT_TICK | NoteKind.HIDE_TICK | NoteKind.JOINT:
            pass
        case _:
            assert_never(kind)


def draw_note_arrow(kind: NoteKind, lane: float, size: float, travel: float, target_time: float, direction: int):
    match kind:
        case (
            NoteKind.NORM_FLICK
            | NoteKind.NORM_TRACE_FLICK
            | NoteKind.NORM_HEAD_FLICK
            | NoteKind.NORM_HEAD_TRACE_FLICK
            | NoteKind.NORM_TAIL_FLICK
            | NoteKind.NORM_TAIL_TRACE_FLICK
        ):
            _draw_arrow(normal_arrow_sprites, lane, size, travel, target_time, direction)
        case (
            NoteKind.CRIT_FLICK
            | NoteKind.CRIT_TRACE_FLICK
            | NoteKind.CRIT_HEAD_FLICK
            | NoteKind.CRIT_HEAD_TRACE_FLICK
            | NoteKind.CRIT_TAIL_FLICK
            | NoteKind.CRIT_TAIL_TRACE_FLICK
        ):
            _draw_arrow(critical_arrow_sprites, lane, size, travel, target_time, direction)
        case (
            NoteKind.NORM_TAP
            | NoteKind.CRIT_TAP
            | NoteKind.NORM_TRACE
            | NoteKind.CRIT_TRACE
            | NoteKind.NORM_RELEASE
            | NoteKind.CRIT_RELEASE
            | NoteKind.NORM_HEAD_TAP
            | NoteKind.CRIT_HEAD_TAP
            | NoteKind.NORM_HEAD_TRACE
            | NoteKind.CRIT_HEAD_TRACE
            | NoteKind.NORM_TAIL_TAP
            | NoteKind.CRIT_TAIL_TAP
            | NoteKind.NORM_TAIL_TRACE
            | NoteKind.CRIT_TAIL_TRACE
            | NoteKind.NORM_HEAD_RELEASE
            | NoteKind.CRIT_HEAD_RELEASE
            | NoteKind.NORM_TAIL_RELEASE
            | NoteKind.CRIT_TAIL_RELEASE
            | NoteKind.NORM_TICK
            | NoteKind.CRIT_TICK
            | NoteKind.HIDE_TICK
            | NoteKind.JOINT
            | NoteKind.DAMAGE
        ):
            pass
        case _:
            assert_never(kind)


def draw_note_tick(kind: NoteKind, lane: float, travel: float, target_time: float):
    match kind:
        case NoteKind.NORM_TRACE | NoteKind.NORM_HEAD_TRACE | NoteKind.NORM_TAIL_TRACE | NoteKind.NORM_TICK:
            _draw_tick(normal_tick_sprites, lane, travel, target_time)
        case NoteKind.CRIT_TRACE | NoteKind.CRIT_HEAD_TRACE | NoteKind.CRIT_TAIL_TRACE | NoteKind.CRIT_TICK:
            _draw_tick(critical_tick_sprites, lane, travel, target_time)
        case NoteKind.NORM_TRACE_FLICK | NoteKind.NORM_HEAD_TRACE_FLICK | NoteKind.NORM_TAIL_TRACE_FLICK:
            _draw_tick(flick_tick_sprites, lane, travel, target_time)
        case NoteKind.CRIT_TRACE_FLICK | NoteKind.CRIT_HEAD_TRACE_FLICK | NoteKind.CRIT_TAIL_TRACE_FLICK:
            _draw_tick(critical_tick_sprites, lane, travel, target_time)
        case (
            NoteKind.NORM_TAP
            | NoteKind.CRIT_TAP
            | NoteKind.NORM_FLICK
            | NoteKind.CRIT_FLICK
            | NoteKind.NORM_RELEASE
            | NoteKind.CRIT_RELEASE
            | NoteKind.NORM_HEAD_TAP
            | NoteKind.CRIT_HEAD_TAP
            | NoteKind.NORM_HEAD_FLICK
            | NoteKind.CRIT_HEAD_FLICK
            | NoteKind.NORM_TAIL_TAP
            | NoteKind.CRIT_TAIL_TAP
            | NoteKind.NORM_TAIL_FLICK
            | NoteKind.CRIT_TAIL_FLICK
            | NoteKind.NORM_HEAD_RELEASE
            | NoteKind.CRIT_HEAD_RELEASE
            | NoteKind.NORM_TAIL_RELEASE
            | NoteKind.CRIT_TAIL_RELEASE
            | NoteKind.HIDE_TICK
            | NoteKind.JOINT
            | NoteKind.DAMAGE
        ):
            pass
        case _:
            assert_never(kind)


def _draw_regular_body(sprites: BodySprites, lane: float, size: float, travel: float, target_time: float):
    a = get_alpha(target_time)
    z = get_z(LAYER_NOTE_BODY, time=target_time, lane=lane)
    if sprites.custom_available:
        left_layout, middle_layout, right_layout = layout_regular_note_body(lane, size, travel)
        sprites.left.draw(left_layout, z=z, a=a)
        sprites.middle.draw(middle_layout, z=z, a=a)
        sprites.right.draw(right_layout, z=z, a=a)
    else:
        layout = layout_regular_note_body_fallback(lane, size, travel)
        sprites.fallback.draw(layout, z=z, a=a)


def _draw_slim_body(sprites: BodySprites, lane: float, size: float, travel: float, target_time: float):
    a = get_alpha(target_time)
    z = get_z(LAYER_NOTE_SLIM_BODY, time=target_time, lane=lane)
    if sprites.custom_available:
        left_layout, middle_layout, right_layout = layout_slim_note_body(lane, size, travel)
        sprites.left.draw(left_layout, z=z, a=a)
        sprites.middle.draw(middle_layout, z=z, a=a)
        sprites.right.draw(right_layout, z=z, a=a)
    else:
        layout = layout_slim_note_body_fallback(lane, size, travel)
        sprites.fallback.draw(layout, z=z, a=a)


def _draw_tick(sprites: TickSprites, lane: float, travel: float, target_time: float):
    a = get_alpha(target_time)
    z = get_z(LAYER_NOTE_TICK, time=target_time, lane=lane)
    layout = layout_tick(lane, travel)
    if sprites.custom_available:
        sprites.normal.draw(layout, z=z, a=a)
    else:
        sprites.fallback.draw(layout, z=z, a=a)


def _draw_arrow(sprites: ArrowSprites, lane: float, size: float, travel: float, target_time: float, direction: int):
    animation_progress = (time() / FLICK_ARROW_PERIOD) % 1 if Options.marker_animation else 0
    a = get_alpha(target_time) * (1 - ease_in_cubic(animation_progress))
    z = get_z(LAYER_NOTE_ARROW, time=target_time, lane=lane)
    if sprites.custom_available:
        layout = layout_flick_arrow(lane, size, direction, travel, animation_progress)
        sprites.get_sprite(size, direction).draw(layout, z=z, a=a)
    else:
        layout = layout_flick_arrow_fallback(lane, size, direction, travel, animation_progress)
        sprites.fallback.draw(layout, z=z, a=a)


def get_note_window(kind: NoteKind) -> JudgmentWindow:
    result = +JudgmentWindow
    match kind:
        case NoteKind.NORM_TAP | NoteKind.NORM_HEAD_TAP | NoteKind.NORM_TAIL_TAP:
            result @= TAP_NORMAL_WINDOW
        case NoteKind.CRIT_TAP | NoteKind.CRIT_HEAD_TAP | NoteKind.CRIT_TAIL_TAP:
            result @= TAP_CRITICAL_WINDOW
        case NoteKind.NORM_FLICK | NoteKind.NORM_HEAD_FLICK | NoteKind.NORM_TAIL_FLICK:
            result @= FLICK_NORMAL_WINDOW
        case NoteKind.CRIT_FLICK | NoteKind.CRIT_HEAD_FLICK | NoteKind.CRIT_TAIL_FLICK:
            result @= FLICK_CRITICAL_WINDOW
        case NoteKind.NORM_TRACE | NoteKind.NORM_HEAD_TRACE | NoteKind.NORM_TAIL_TRACE:
            result @= TRACE_NORMAL_WINDOW
        case NoteKind.CRIT_TRACE | NoteKind.CRIT_HEAD_TRACE | NoteKind.CRIT_TAIL_TRACE:
            result @= TRACE_CRITICAL_WINDOW
        case NoteKind.NORM_TRACE_FLICK | NoteKind.NORM_HEAD_TRACE_FLICK | NoteKind.NORM_TAIL_TRACE_FLICK:
            result @= TRACE_FLICK_NORMAL_WINDOW
        case NoteKind.CRIT_TRACE_FLICK | NoteKind.CRIT_HEAD_TRACE_FLICK | NoteKind.CRIT_TAIL_TRACE_FLICK:
            result @= TRACE_FLICK_CRITICAL_WINDOW
        case NoteKind.NORM_RELEASE | NoteKind.NORM_HEAD_RELEASE | NoteKind.NORM_TAIL_RELEASE:
            result @= SLIDE_END_NORMAL_WINDOW
        case NoteKind.CRIT_RELEASE | NoteKind.CRIT_HEAD_RELEASE | NoteKind.CRIT_TAIL_RELEASE:
            result @= SLIDE_END_CRITICAL_WINDOW
        case NoteKind.NORM_TAIL_FLICK | NoteKind.NORM_TAIL_TRACE_FLICK:
            result @= SLIDE_END_FLICK_NORMAL_WINDOW
        case NoteKind.CRIT_TAIL_FLICK | NoteKind.CRIT_TAIL_TRACE_FLICK:
            result @= SLIDE_END_FLICK_CRITICAL_WINDOW
        case NoteKind.NORM_TICK | NoteKind.CRIT_TICK | NoteKind.HIDE_TICK | NoteKind.JOINT | NoteKind.DAMAGE:
            pass
        case _:
            assert_never(kind)
    return result


def get_note_bucket(kind: NoteKind) -> Bucket:
    result = +Bucket(-1)
    match kind:
        case NoteKind.NORM_TAP:
            result @= Buckets.normal_tap
        case NoteKind.CRIT_TAP:
            result @= Buckets.critical_tap
        case NoteKind.NORM_FLICK:
            result @= Buckets.normal_flick
        case NoteKind.CRIT_FLICK:
            result @= Buckets.critical_flick
        case NoteKind.NORM_TRACE:
            result @= Buckets.normal_trace
        case NoteKind.CRIT_TRACE:
            result @= Buckets.critical_trace
        case NoteKind.NORM_TRACE_FLICK:
            result @= Buckets.normal_trace_flick
        case NoteKind.CRIT_TRACE_FLICK:
            result @= Buckets.critical_trace_flick
        case NoteKind.NORM_HEAD_TAP:
            result @= Buckets.normal_head_tap
        case NoteKind.CRIT_HEAD_TAP:
            result @= Buckets.critical_head_tap
        case NoteKind.NORM_HEAD_FLICK:
            result @= Buckets.normal_head_flick
        case NoteKind.CRIT_HEAD_FLICK:
            result @= Buckets.critical_head_flick
        case NoteKind.NORM_HEAD_TRACE:
            result @= Buckets.normal_head_trace
        case NoteKind.CRIT_HEAD_TRACE:
            result @= Buckets.critical_head_trace
        case NoteKind.NORM_HEAD_TRACE_FLICK:
            result @= Buckets.normal_head_trace_flick
        case NoteKind.CRIT_HEAD_TRACE_FLICK:
            result @= Buckets.critical_head_trace_flick
        case NoteKind.NORM_TAIL_FLICK:
            result @= Buckets.normal_tail_flick
        case NoteKind.CRIT_TAIL_FLICK:
            result @= Buckets.critical_tail_flick
        case NoteKind.NORM_TAIL_TRACE:
            result @= Buckets.normal_tail_trace
        case NoteKind.CRIT_TAIL_TRACE:
            result @= Buckets.critical_tail_trace
        case NoteKind.NORM_TAIL_TRACE_FLICK:
            result @= Buckets.normal_tail_trace_flick
        case NoteKind.CRIT_TAIL_TRACE_FLICK:
            result @= Buckets.critical_tail_trace_flick
        case NoteKind.NORM_TAIL_RELEASE:
            result @= Buckets.normal_tail_release
        case NoteKind.CRIT_TAIL_RELEASE:
            result @= Buckets.critical_tail_release
        case (
            NoteKind.NORM_RELEASE
            | NoteKind.CRIT_RELEASE
            | NoteKind.NORM_HEAD_RELEASE
            | NoteKind.CRIT_HEAD_RELEASE
            | NoteKind.NORM_TAIL_TAP
            | NoteKind.CRIT_TAIL_TAP
            | NoteKind.NORM_TICK
            | NoteKind.CRIT_TICK
            | NoteKind.HIDE_TICK
            | NoteKind.JOINT
            | NoteKind.DAMAGE
        ):
            pass
        case _:
            assert_never(kind)
    return result
