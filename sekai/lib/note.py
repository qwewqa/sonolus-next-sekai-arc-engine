from enum import IntEnum
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
    SLIDE_START_CRITICAL_WINDOW,
    SLIDE_START_NORMAL_WINDOW,
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
    slide_tick_sprites,
    trace_flick_note_body_sprites,
    trace_slide_note_body_sprites,
)

FLICK_ARROW_PERIOD = 0.5


class NoteKind(IntEnum):
    TAP = 1
    CRITICAL_TAP = 2

    FLICK = 3
    CRITICAL_FLICK = 4

    SLIDE_START = 5
    CRITICAL_SLIDE_START = 6
    SLIDE_START_ANCHOR = 7

    SLIDE_END = 8
    CRITICAL_SLIDE_END = 9

    SLIDE_END_FLICK = 10
    CRITICAL_SLIDE_END_FLICK = 11

    SLIDE_TICK = 12
    CRITICAL_SLIDE_TICK = 13
    SLIDE_ANCHOR = 14
    INVISIBLE_SLIDE_TICK = 15

    ATTACHED_SLIDE_TICK = 16
    CRITICAL_ATTACHED_SLIDE_TICK = 17

    TRACE = 18
    CRITICAL_TRACE = 19

    TRACE_FLICK = 20
    CRITICAL_TRACE_FLICK = 21
    UNMARKED_TRACE_FLICK = 22

    TRACE_SLIDE = 23
    CRITICAL_TRACE_SLIDE = 24

    TRACE_SLIDE_END = 25
    CRITICAL_TRACE_SLIDE_END = 26

    DAMAGE = 27


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


def draw_note_body(kind: NoteKind, lane: float, size: float, travel: float, target_time: float):
    match kind:
        case NoteKind.TAP:
            _draw_regular_body(normal_note_body_sprites, lane, size, travel, target_time)
        case (
            NoteKind.CRITICAL_TAP
            | NoteKind.CRITICAL_FLICK
            | NoteKind.CRITICAL_SLIDE_START
            | NoteKind.CRITICAL_SLIDE_END
            | NoteKind.CRITICAL_SLIDE_END_FLICK
        ):
            _draw_regular_body(critical_note_body_sprites, lane, size, travel, target_time)
        case NoteKind.FLICK | NoteKind.SLIDE_END_FLICK:
            _draw_regular_body(flick_note_body_sprites, lane, size, travel, target_time)
        case NoteKind.SLIDE_START | NoteKind.SLIDE_END:
            _draw_regular_body(slide_note_body_sprites, lane, size, travel, target_time)
        case NoteKind.TRACE:
            _draw_slim_body(normal_trace_note_body_sprites, lane, size, travel, target_time)
        case (
            NoteKind.CRITICAL_TRACE
            | NoteKind.CRITICAL_TRACE_FLICK
            | NoteKind.CRITICAL_TRACE_SLIDE
            | NoteKind.CRITICAL_TRACE_SLIDE_END
        ):
            _draw_slim_body(critical_trace_note_body_sprites, lane, size, travel, target_time)
        case NoteKind.TRACE_FLICK | NoteKind.UNMARKED_TRACE_FLICK:
            _draw_slim_body(trace_flick_note_body_sprites, lane, size, travel, target_time)
        case NoteKind.TRACE_SLIDE | NoteKind.TRACE_SLIDE_END:
            _draw_slim_body(trace_slide_note_body_sprites, lane, size, travel, target_time)
        case NoteKind.DAMAGE:
            _draw_slim_body(damage_note_body_sprites, lane, size, travel, target_time)
        case (
            NoteKind.SLIDE_START_ANCHOR
            | NoteKind.SLIDE_TICK
            | NoteKind.CRITICAL_SLIDE_TICK
            | NoteKind.SLIDE_ANCHOR
            | NoteKind.INVISIBLE_SLIDE_TICK
            | NoteKind.ATTACHED_SLIDE_TICK
            | NoteKind.CRITICAL_ATTACHED_SLIDE_TICK
        ):
            pass
        case _:
            assert_never(kind)


def draw_note_arrow(kind: NoteKind, lane: float, size: float, travel: float, target_time: float, direction: int):
    match kind:
        case NoteKind.FLICK | NoteKind.SLIDE_END_FLICK | NoteKind.TRACE_FLICK:
            _draw_arrow(normal_arrow_sprites, lane, size, travel, target_time, direction)
        case NoteKind.CRITICAL_FLICK | NoteKind.CRITICAL_SLIDE_END_FLICK | NoteKind.CRITICAL_TRACE_FLICK:
            _draw_arrow(critical_arrow_sprites, lane, size, travel, target_time, direction)
        case (
            NoteKind.TAP
            | NoteKind.CRITICAL_TAP
            | NoteKind.SLIDE_START
            | NoteKind.CRITICAL_SLIDE_START
            | NoteKind.SLIDE_START_ANCHOR
            | NoteKind.SLIDE_END
            | NoteKind.CRITICAL_SLIDE_END
            | NoteKind.SLIDE_TICK
            | NoteKind.CRITICAL_SLIDE_TICK
            | NoteKind.SLIDE_ANCHOR
            | NoteKind.INVISIBLE_SLIDE_TICK
            | NoteKind.ATTACHED_SLIDE_TICK
            | NoteKind.CRITICAL_ATTACHED_SLIDE_TICK
            | NoteKind.TRACE
            | NoteKind.CRITICAL_TRACE
            | NoteKind.UNMARKED_TRACE_FLICK
            | NoteKind.TRACE_SLIDE
            | NoteKind.CRITICAL_TRACE_SLIDE
            | NoteKind.TRACE_SLIDE_END
            | NoteKind.CRITICAL_TRACE_SLIDE_END
            | NoteKind.DAMAGE
        ):
            pass
        case _:
            assert_never(kind)


def draw_note_tick(kind: NoteKind, lane: float, travel: float, target_time: float):
    match kind:
        case NoteKind.SLIDE_TICK | NoteKind.ATTACHED_SLIDE_TICK | NoteKind.TRACE_SLIDE | NoteKind.TRACE_SLIDE_END:
            _draw_tick(slide_tick_sprites, lane, travel, target_time)
        case (
            NoteKind.CRITICAL_SLIDE_TICK
            | NoteKind.CRITICAL_ATTACHED_SLIDE_TICK
            | NoteKind.CRITICAL_TRACE
            | NoteKind.CRITICAL_TRACE_SLIDE
            | NoteKind.CRITICAL_TRACE_SLIDE_END
            | NoteKind.CRITICAL_TRACE_FLICK
        ):
            _draw_tick(critical_tick_sprites, lane, travel, target_time)
        case NoteKind.TRACE:
            _draw_tick(normal_tick_sprites, lane, travel, target_time)
        case NoteKind.TRACE_FLICK:
            _draw_tick(flick_tick_sprites, lane, travel, target_time)
        case (
            NoteKind.TAP
            | NoteKind.CRITICAL_TAP
            | NoteKind.FLICK
            | NoteKind.CRITICAL_FLICK
            | NoteKind.SLIDE_START
            | NoteKind.CRITICAL_SLIDE_START
            | NoteKind.SLIDE_START_ANCHOR
            | NoteKind.SLIDE_END
            | NoteKind.CRITICAL_SLIDE_END
            | NoteKind.SLIDE_END_FLICK
            | NoteKind.CRITICAL_SLIDE_END_FLICK
            | NoteKind.SLIDE_ANCHOR
            | NoteKind.INVISIBLE_SLIDE_TICK
            | NoteKind.UNMARKED_TRACE_FLICK
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
        case NoteKind.TAP:
            result @= TAP_NORMAL_WINDOW
        case NoteKind.CRITICAL_TAP:
            result @= TAP_CRITICAL_WINDOW
        case NoteKind.FLICK:
            result @= FLICK_NORMAL_WINDOW
        case NoteKind.CRITICAL_FLICK:
            result @= FLICK_CRITICAL_WINDOW
        case NoteKind.SLIDE_START:
            result @= SLIDE_START_NORMAL_WINDOW
        case NoteKind.CRITICAL_SLIDE_START:
            result @= SLIDE_START_CRITICAL_WINDOW
        case NoteKind.SLIDE_START_ANCHOR:
            pass
        case NoteKind.SLIDE_END:
            result @= SLIDE_END_NORMAL_WINDOW
        case NoteKind.CRITICAL_SLIDE_END:
            result @= SLIDE_END_CRITICAL_WINDOW
        case NoteKind.SLIDE_END_FLICK:
            result @= SLIDE_END_FLICK_NORMAL_WINDOW
        case NoteKind.CRITICAL_SLIDE_END_FLICK:
            result @= SLIDE_END_FLICK_CRITICAL_WINDOW
        case NoteKind.SLIDE_TICK:
            pass
        case NoteKind.CRITICAL_SLIDE_TICK:
            pass
        case NoteKind.SLIDE_ANCHOR:
            pass
        case NoteKind.INVISIBLE_SLIDE_TICK:
            pass
        case NoteKind.ATTACHED_SLIDE_TICK:
            pass
        case NoteKind.CRITICAL_ATTACHED_SLIDE_TICK:
            pass
        case NoteKind.TRACE:
            result @= TRACE_NORMAL_WINDOW
        case NoteKind.CRITICAL_TRACE:
            result @= TRACE_CRITICAL_WINDOW
        case NoteKind.TRACE_FLICK:
            result @= TRACE_FLICK_NORMAL_WINDOW
        case NoteKind.CRITICAL_TRACE_FLICK:
            result @= TRACE_FLICK_CRITICAL_WINDOW
        case NoteKind.UNMARKED_TRACE_FLICK:
            result @= TRACE_FLICK_NORMAL_WINDOW
        case NoteKind.TRACE_SLIDE:
            result @= TRACE_NORMAL_WINDOW
        case NoteKind.CRITICAL_TRACE_SLIDE:
            result @= TRACE_CRITICAL_WINDOW
        case NoteKind.TRACE_SLIDE_END:
            result @= TRACE_NORMAL_WINDOW
        case NoteKind.CRITICAL_TRACE_SLIDE_END:
            result @= TRACE_CRITICAL_WINDOW
        case NoteKind.DAMAGE:
            pass
        case _:
            assert_never(kind)
    return result


def get_note_bucket(kind: NoteKind) -> Bucket:
    result = +Bucket(-1)
    match kind:
        case NoteKind.TAP:
            result @= Buckets.normal_tap_note
        case NoteKind.CRITICAL_TAP:
            result @= Buckets.critical_tap_note
        case NoteKind.FLICK:
            result @= Buckets.normal_flick_note
        case NoteKind.CRITICAL_FLICK:
            result @= Buckets.critical_flick_note
        case NoteKind.SLIDE_START:
            result @= Buckets.normal_slide_start_note
        case NoteKind.CRITICAL_SLIDE_START:
            result @= Buckets.critical_slide_start_note
        case NoteKind.SLIDE_START_ANCHOR:
            pass
        case NoteKind.SLIDE_END:
            result @= Buckets.normal_slide_end_note
        case NoteKind.CRITICAL_SLIDE_END:
            result @= Buckets.critical_slide_end_note
        case NoteKind.SLIDE_END_FLICK:
            result @= Buckets.normal_slide_end_flick_note
        case NoteKind.CRITICAL_SLIDE_END_FLICK:
            result @= Buckets.critical_slide_end_flick_note
        case NoteKind.SLIDE_TICK:
            pass
        case NoteKind.CRITICAL_SLIDE_TICK:
            pass
        case NoteKind.SLIDE_ANCHOR:
            pass
        case NoteKind.INVISIBLE_SLIDE_TICK:
            pass
        case NoteKind.ATTACHED_SLIDE_TICK:
            pass
        case NoteKind.CRITICAL_ATTACHED_SLIDE_TICK:
            pass
        case NoteKind.TRACE:
            result @= Buckets.normal_trace_note
        case NoteKind.CRITICAL_TRACE:
            result @= Buckets.critical_trace_note
        case NoteKind.TRACE_FLICK:
            result @= Buckets.normal_trace_flick_note
        case NoteKind.CRITICAL_TRACE_FLICK:
            result @= Buckets.critical_trace_flick_note
        case NoteKind.UNMARKED_TRACE_FLICK:
            result @= Buckets.normal_trace_flick_note
        case NoteKind.TRACE_SLIDE:
            result @= Buckets.normal_slide_trace_note
        case NoteKind.CRITICAL_TRACE_SLIDE:
            result @= Buckets.critical_slide_trace_note
        case NoteKind.TRACE_SLIDE_END:
            result @= Buckets.normal_slide_end_trace_note
        case NoteKind.CRITICAL_TRACE_SLIDE_END:
            result @= Buckets.critical_slide_end_trace_note
        case NoteKind.DAMAGE:
            pass
        case _:
            assert_never(kind)
    return result
