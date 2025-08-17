from __future__ import annotations

from typing import assert_never

from sonolus.script.archetype import PlayArchetype, callback
from sonolus.script.array import Dim
from sonolus.script.containers import ArraySet
from sonolus.script.globals import level_memory
from sonolus.script.iterator import maybe_next
from sonolus.script.quad import Rect
from sonolus.script.runtime import Touch, time, touches

from sekai.lib.buckets import SLIDE_END_LOCKOUT_DURATION
from sekai.lib.layout import layout_hitbox
from sekai.lib.note import NoteKind
from sekai.lib.options import Options
from sekai.play import note

# Notes within this threshold in seconds of each other in target time are considered simultaneous
# when it comes to hitbox conflict resolution.
SIMULTANEOUS_THRESHOLD = 0.002


@level_memory
class InputState:
    disallowed_empty_touches: ArraySet[int, Dim[32]]
    disallowed_release_touches: ArraySet[int, Dim[32]]


def disallow_empty(touch: Touch):
    InputState.disallowed_empty_touches.add(touch.id)


def disallow_release(touch: Touch):
    InputState.disallowed_release_touches.add(touch.id)


def is_allowed_empty(touch: Touch) -> bool:
    return touch.id not in InputState.disallowed_empty_touches


def is_allowed_release(touch: Touch) -> bool:
    return touch.id not in InputState.disallowed_release_touches


class InputManager(PlayArchetype):
    name = "InputManager"

    @callback(order=-1)
    def touch(self):
        preassign_taps()
        note.NoteMemory.active_tap_input_notes.clear()


def get_leniency(kind: NoteKind) -> float:
    if Options.ultra_leniency:
        return 12.0
    match kind:
        case NoteKind.NORM_TAP | NoteKind.CRIT_TAP:
            return 0.75
        case (
            NoteKind.NORM_FLICK
            | NoteKind.CRIT_FLICK
            | NoteKind.NORM_TRACE
            | NoteKind.CRIT_TRACE
            | NoteKind.NORM_TRACE_FLICK
            | NoteKind.CRIT_TRACE_FLICK
            | NoteKind.NORM_RELEASE
            | NoteKind.CRIT_RELEASE
            | NoteKind.NORM_HEAD_TAP
            | NoteKind.CRIT_HEAD_TAP
            | NoteKind.NORM_HEAD_FLICK
            | NoteKind.CRIT_HEAD_FLICK
            | NoteKind.NORM_HEAD_TRACE
            | NoteKind.CRIT_HEAD_TRACE
            | NoteKind.NORM_HEAD_TRACE_FLICK
            | NoteKind.CRIT_HEAD_TRACE_FLICK
            | NoteKind.NORM_HEAD_RELEASE
            | NoteKind.CRIT_HEAD_RELEASE
            | NoteKind.NORM_TAIL_TAP
            | NoteKind.CRIT_TAIL_TAP
            | NoteKind.NORM_TAIL_FLICK
            | NoteKind.CRIT_TAIL_FLICK
            | NoteKind.NORM_TAIL_TRACE
            | NoteKind.CRIT_TAIL_TRACE
            | NoteKind.NORM_TAIL_TRACE_FLICK
            | NoteKind.CRIT_TAIL_TRACE_FLICK
            | NoteKind.NORM_TAIL_RELEASE
            | NoteKind.CRIT_TAIL_RELEASE
            | NoteKind.NORM_TICK
            | NoteKind.CRIT_TICK
            | NoteKind.HIDE_TICK
        ):
            return 1.0
        case NoteKind.JOINT | NoteKind.DAMAGE:
            return 0
        case _:
            assert_never(kind)


def has_tap_input(kind: NoteKind) -> bool:
    match kind:
        case (
            NoteKind.NORM_TAP
            | NoteKind.CRIT_TAP
            | NoteKind.NORM_FLICK
            | NoteKind.CRIT_FLICK
            | NoteKind.NORM_HEAD_TAP
            | NoteKind.CRIT_HEAD_TAP
            | NoteKind.NORM_HEAD_FLICK
            | NoteKind.CRIT_HEAD_FLICK
            | NoteKind.NORM_TAIL_TAP
            | NoteKind.CRIT_TAIL_TAP
        ):
            return True
        case (
            NoteKind.NORM_TRACE
            | NoteKind.CRIT_TRACE
            | NoteKind.NORM_TRACE_FLICK
            | NoteKind.CRIT_TRACE_FLICK
            | NoteKind.NORM_RELEASE
            | NoteKind.CRIT_RELEASE
            | NoteKind.NORM_HEAD_TRACE
            | NoteKind.CRIT_HEAD_TRACE
            | NoteKind.NORM_HEAD_TRACE_FLICK
            | NoteKind.CRIT_HEAD_TRACE_FLICK
            | NoteKind.NORM_HEAD_RELEASE
            | NoteKind.CRIT_HEAD_RELEASE
            | NoteKind.NORM_TAIL_FLICK
            | NoteKind.CRIT_TAIL_FLICK
            | NoteKind.NORM_TAIL_TRACE
            | NoteKind.CRIT_TAIL_TRACE
            | NoteKind.NORM_TAIL_TRACE_FLICK
            | NoteKind.CRIT_TAIL_TRACE_FLICK
            | NoteKind.NORM_TAIL_RELEASE
            | NoteKind.CRIT_TAIL_RELEASE
            | NoteKind.NORM_TICK
            | NoteKind.CRIT_TICK
            | NoteKind.HIDE_TICK
            | NoteKind.JOINT
            | NoteKind.DAMAGE
        ):
            return False
        case _:
            assert_never(kind)


def update_input_state():
    old_disallowed_empty_touches = +InputState.disallowed_empty_touches
    InputState.disallowed_empty_touches.clear()
    for existing in old_disallowed_empty_touches:
        maybe_touch = maybe_next(touch for touch in touches() if touch.id == existing)
        if maybe_touch.is_nothing:
            continue
        touch = maybe_touch.get()
        disallow_empty(touch)

    old_disallowed_release_touches = +InputState.disallowed_release_touches
    InputState.disallowed_release_touches.clear()
    for existing in old_disallowed_release_touches:
        maybe_touch = maybe_next(touch for touch in touches() if touch.id == existing)
        if maybe_touch.is_nothing:
            continue
        touch = maybe_touch.get()
        if touch.start_time + SLIDE_END_LOCKOUT_DURATION < time():
            disallow_release(touch)


def preassign_taps():
    active_input_taps = note.NoteMemory.active_tap_input_notes
    active_input_taps.sort(key=lambda ref: ref.get().target_time)
    available_tap_indexes = ArraySet[int, Dim[32]].new()
    for i, touch in enumerate(touches()):
        if touch.started:
            available_tap_indexes.add(i)
    for current_i in range(len(active_input_taps)):
        current = active_input_taps[current_i].get()
        leniency = get_leniency(current.kind)
        current_l = current.lane - current.size
        current_r = current.lane + current.size
        hitbox_l = current_l - leniency
        hitbox_r = current_r + leniency
        # We don't need to conflict resolve with earlier notes since they are already processed and if they could
        # capture a tap, they would have done so already.
        for other_i in range(current_i + 1, len(active_input_taps)):
            other = active_input_taps[other_i].get()
            if other.target_time - current.target_time > SIMULTANEOUS_THRESHOLD:
                # Since the notes are sorted by target time, we can stop checking further
                break
            other_l = other.lane - other.size
            other_r = other.lane + other.size
            if other_l < current_l:
                hitbox_l = max(hitbox_l, (current_l + other_r) / 2)
            if other_r > current_r:
                hitbox_r = min(hitbox_r, (current_r + other_l) / 2)
        hitbox_l = min(hitbox_l, current_l)
        hitbox_r = max(hitbox_r, current_r)
        hitbox_layout = layout_hitbox(hitbox_l, hitbox_r)
        for tap_i in available_tap_indexes:
            touch = touches()[tap_i]
            if touch.started and hitbox_layout.contains_point(touch.position):
                disallow_release(touch)
                current.tap_id = touch.id
                available_tap_indexes.remove(tap_i)
                break


def get_full_hitbox(n: note.BaseNote) -> Rect:
    leniency = get_leniency(n.kind)
    hitbox_l = n.lane - n.size - leniency
    hitbox_r = n.lane + n.size + leniency
    return layout_hitbox(hitbox_l, hitbox_r)
