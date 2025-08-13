from enum import IntEnum
from typing import assert_never

from sonolus.script.easing import ease_in_cubic
from sonolus.script.runtime import time

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
    HIDDEN_SLIDE_START = 7

    SLIDE_END = 8
    CRITICAL_SLIDE_END = 9

    SLIDE_END_FLICK = 10
    CRITICAL_SLIDE_END_FLICK = 11

    SLIDE_TICK = 12
    CRITICAL_SLIDE_TICK = 13
    HIDDEN_SLIDE_TICK = 14
    IGNORED_SLIDE_TICK = 15

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
    match kind:
        case NoteKind.TAP:
            draw_regular_note_body(normal_note_body_sprites, lane, size, travel, target_time)
        case NoteKind.CRITICAL_TAP:
            draw_regular_note_body(critical_note_body_sprites, lane, size, travel, target_time)
        case NoteKind.FLICK:
            draw_regular_note_body(flick_note_body_sprites, lane, size, travel, target_time)
            draw_note_arrow(normal_arrow_sprites, lane, size, travel, target_time, direction)
        case NoteKind.CRITICAL_FLICK:
            draw_regular_note_body(critical_note_body_sprites, lane, size, travel, target_time)
            draw_note_arrow(critical_arrow_sprites, lane, size, travel, target_time, direction)
        case NoteKind.SLIDE_START:
            draw_regular_note_body(slide_note_body_sprites, lane, size, travel, target_time)
        case NoteKind.CRITICAL_SLIDE_START:
            draw_regular_note_body(critical_note_body_sprites, lane, size, travel, target_time)
        case NoteKind.HIDDEN_SLIDE_START:
            pass
        case NoteKind.SLIDE_END:
            draw_regular_note_body(slide_note_body_sprites, lane, size, travel, target_time)
        case NoteKind.CRITICAL_SLIDE_END:
            draw_regular_note_body(critical_note_body_sprites, lane, size, travel, target_time)
        case NoteKind.SLIDE_END_FLICK:
            draw_regular_note_body(flick_note_body_sprites, lane, size, travel, target_time)
            draw_note_arrow(normal_arrow_sprites, lane, size, travel, target_time, direction)
        case NoteKind.CRITICAL_SLIDE_END_FLICK:
            draw_regular_note_body(critical_note_body_sprites, lane, size, travel, target_time)
            draw_note_arrow(critical_arrow_sprites, lane, size, travel, target_time, direction)
        case NoteKind.SLIDE_TICK:
            draw_tick(slide_tick_sprites, lane, travel, target_time)
        case NoteKind.CRITICAL_SLIDE_TICK:
            draw_tick(critical_tick_sprites, lane, travel, target_time)
        case NoteKind.HIDDEN_SLIDE_TICK:
            pass
        case NoteKind.IGNORED_SLIDE_TICK:
            pass
        case NoteKind.ATTACHED_SLIDE_TICK:
            draw_tick(slide_tick_sprites, lane, travel, target_time)
        case NoteKind.CRITICAL_ATTACHED_SLIDE_TICK:
            draw_tick(critical_tick_sprites, lane, travel, target_time)
        case NoteKind.TRACE:
            draw_slim_note_body(normal_trace_note_body_sprites, lane, size, travel, target_time)
            draw_tick(normal_tick_sprites, lane, travel, target_time)
        case NoteKind.CRITICAL_TRACE:
            draw_slim_note_body(critical_trace_note_body_sprites, lane, size, travel, target_time)
            draw_tick(critical_tick_sprites, lane, travel, target_time)
        case NoteKind.TRACE_FLICK:
            draw_slim_note_body(trace_flick_note_body_sprites, lane, size, travel, target_time)
            draw_tick(flick_tick_sprites, lane, travel, target_time)
            draw_note_arrow(normal_arrow_sprites, lane, size, travel, target_time, direction)
        case NoteKind.CRITICAL_TRACE_FLICK:
            draw_slim_note_body(critical_trace_note_body_sprites, lane, size, travel, target_time)
            draw_tick(critical_tick_sprites, lane, travel, target_time)
            draw_note_arrow(critical_arrow_sprites, lane, size, travel, target_time, direction)
        case NoteKind.UNMARKED_TRACE_FLICK:
            draw_slim_note_body(trace_flick_note_body_sprites, lane, size, travel, target_time)
            # No tick or arrow for unmarked trace flicks
        case NoteKind.TRACE_SLIDE:
            draw_slim_note_body(trace_slide_note_body_sprites, lane, size, travel, target_time)
            draw_tick(slide_tick_sprites, lane, travel, target_time)
        case NoteKind.CRITICAL_TRACE_SLIDE:
            draw_slim_note_body(critical_trace_note_body_sprites, lane, size, travel, target_time)
            draw_tick(critical_tick_sprites, lane, travel, target_time)
        case NoteKind.TRACE_SLIDE_END:
            draw_slim_note_body(trace_slide_note_body_sprites, lane, size, travel, target_time)
            draw_tick(slide_tick_sprites, lane, travel, target_time)
        case NoteKind.CRITICAL_TRACE_SLIDE_END:
            draw_slim_note_body(critical_trace_note_body_sprites, lane, size, travel, target_time)
            draw_tick(critical_tick_sprites, lane, travel, target_time)
        case NoteKind.DAMAGE:
            draw_slim_note_body(damage_note_body_sprites, lane, size, travel, target_time)
        case _:
            assert_never(kind)


def draw_regular_note_body(sprites: BodySprites, lane: float, size: float, travel: float, target_time: float):
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


def draw_slim_note_body(sprites: BodySprites, lane: float, size: float, travel: float, target_time: float):
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


def draw_tick(sprites: TickSprites, lane: float, travel: float, target_time: float):
    a = get_alpha(target_time)
    z = get_z(LAYER_NOTE_TICK, time=target_time, lane=lane)
    layout = layout_tick(lane, travel)
    if sprites.custom_available:
        sprites.normal.draw(layout, z=z, a=a)
    else:
        sprites.fallback.draw(layout, z=z, a=a)


def draw_note_arrow(sprites: ArrowSprites, lane: float, size: float, travel: float, target_time: float, direction: int):
    animation_progress = (time() / FLICK_ARROW_PERIOD) % 1 if Options.marker_animation else 0
    a = get_alpha(target_time) * (1 - ease_in_cubic(animation_progress))
    z = get_z(LAYER_NOTE_ARROW, time=target_time, lane=lane)
    if sprites.custom_available:
        layout = layout_flick_arrow(lane, size, direction, travel, animation_progress)
        sprites.get_sprite(size, direction).draw(layout, z=z, a=a)
    else:
        layout = layout_flick_arrow_fallback(lane, size, direction, travel, animation_progress)
        sprites.fallback.draw(layout, z=z, a=a)
