from collections.abc import Callable
from math import pi

from sonolus.script.array import Array

from sekai.lib.layout import FlickDirection, transformed_vec_at
from sekai.lib.note import NoteKind
from sekai.tutorial.framework import PhaseTime, TutorialNoteInfo, zoom_to_center
from sekai.tutorial.instructions import Instructions
from sekai.tutorial.painting import paint_tap_flick_motion, paint_tap_motion

ANGLE_UP_LEFT = pi / 2 + pi / 4
ANGLE_UP_RIGHT = pi / 2 - pi / 4
ANGLE_DOWN_LEFT = -pi / 2 - pi / 4
ANGLE_DOWN_RIGHT = -pi / 2 + pi / 4
OMNI_ANGLES = Array(ANGLE_UP_LEFT, ANGLE_UP_RIGHT, ANGLE_DOWN_RIGHT, ANGLE_DOWN_LEFT)

INTRO_DURATION = 1.5
FALL_DURATION = 1.5
FROZEN_REPEATS = 4
FROZEN_TAP_DURATION = 1
FROZEN_HOLD_DURATION = 1
FROZEN_FLICK_DURATION = 0.5
FROZEN_RELEASE_DURATION = 1
END_DURATION = 1.5


LANE = 1.5
SIZE = 1.5


def tap_phase(t: PhaseTime):
    intro = t.first(INTRO_DURATION)
    fall = intro.next(FALL_DURATION)
    frozen = fall.next(FROZEN_TAP_DURATION, repeats=FROZEN_REPEATS)
    hit = frozen.end_instant()
    end = frozen.next(END_DURATION)
    post_hit = t.range(hit.timing, end.end)

    norm_note = TutorialNoteInfo.of(
        kind=NoteKind.NORM_TAP,
        lane=-LANE,
        size=SIZE,
        direction=FlickDirection.UP_OMNI,
    )
    crit_note = TutorialNoteInfo.of(
        kind=NoteKind.CRIT_TAP,
        lane=LANE,
        size=SIZE,
        direction=FlickDirection.UP_OMNI,
    )

    if intro:
        zoom_to_center()
        norm_note.draw_intro()
        crit_note.draw_intro()
    if fall:
        norm_note.draw_fall(fall)
        crit_note.draw_fall(fall)
    if frozen:
        norm_note.draw_frozen()
        crit_note.draw_frozen()
        paint_tap_motion(transformed_vec_at(norm_note.lane), frozen.progress)
        paint_tap_motion(transformed_vec_at(crit_note.lane), frozen.progress)
        Instructions.tap.show()
    if hit:
        norm_note.play_hit_effects()
        crit_note.play_hit_effects()
    if post_hit:
        norm_note.draw_slot_effects(post_hit)
        crit_note.draw_slot_effects(post_hit)
    if end:
        pass
    return end.is_done


def omni_flick_phase(t: PhaseTime):
    intro = t.first(INTRO_DURATION)
    fall = intro.next(FALL_DURATION)
    frozen = fall.next(FROZEN_TAP_DURATION + FROZEN_FLICK_DURATION, repeats=FROZEN_REPEATS)
    hit = t.instant(frozen.end - FROZEN_FLICK_DURATION)
    end = frozen.next(END_DURATION)
    post_hit = t.range(hit.timing, end.end)

    norm_note = TutorialNoteInfo.of(
        kind=NoteKind.NORM_FLICK,
        lane=-LANE,
        size=SIZE,
        direction=FlickDirection.UP_OMNI,
    )
    crit_note = TutorialNoteInfo.of(
        kind=NoteKind.CRIT_FLICK,
        lane=LANE,
        size=SIZE,
        direction=FlickDirection.DOWN_OMNI,
    )
    if intro:
        zoom_to_center()
        norm_note.draw_intro()
        crit_note.draw_intro()
    if fall:
        norm_note.draw_fall(fall)
        crit_note.draw_fall(fall)
    if frozen:
        if hit.is_upcoming:
            norm_note.draw_frozen()
            crit_note.draw_frozen()
        angle = OMNI_ANGLES[frozen.current_segment]
        paint_tap_flick_motion(
            transformed_vec_at(norm_note.lane), angle, frozen.progress, FROZEN_TAP_DURATION, FROZEN_FLICK_DURATION
        )
        paint_tap_flick_motion(
            transformed_vec_at(crit_note.lane), angle, frozen.progress, FROZEN_TAP_DURATION, FROZEN_FLICK_DURATION
        )
        Instructions.tap_flick.show()
    if hit:
        norm_note.play_hit_effects()
        crit_note.play_hit_effects()
    if post_hit:
        norm_note.draw_slot_effects(post_hit)
        crit_note.draw_slot_effects(post_hit)
    if end:
        pass
    return end.is_done


def up_flick_phase(t: PhaseTime):
    intro = t.first(INTRO_DURATION)
    fall = intro.next(FALL_DURATION)
    frozen = fall.next(FROZEN_TAP_DURATION + FROZEN_FLICK_DURATION, repeats=FROZEN_REPEATS)
    hit = t.instant(frozen.end - FROZEN_FLICK_DURATION)
    end = frozen.next(END_DURATION)
    post_hit = t.range(hit.timing, end.end)

    norm_note = TutorialNoteInfo.of(
        kind=NoteKind.NORM_FLICK,
        lane=-LANE,
        size=SIZE,
        direction=FlickDirection.UP_LEFT,
    )
    crit_note = TutorialNoteInfo.of(
        kind=NoteKind.CRIT_FLICK,
        lane=LANE,
        size=SIZE,
        direction=FlickDirection.UP_RIGHT,
    )
    if intro:
        zoom_to_center()
        norm_note.draw_intro()
        crit_note.draw_intro()
    if fall:
        norm_note.draw_fall(fall)
        crit_note.draw_fall(fall)
    if frozen:
        if hit.is_upcoming:
            norm_note.draw_frozen()
            crit_note.draw_frozen()
        paint_tap_flick_motion(
            transformed_vec_at(norm_note.lane),
            ANGLE_UP_LEFT,
            frozen.progress,
            FROZEN_TAP_DURATION,
            FROZEN_FLICK_DURATION,
        )
        paint_tap_flick_motion(
            transformed_vec_at(crit_note.lane),
            ANGLE_UP_RIGHT,
            frozen.progress,
            FROZEN_TAP_DURATION,
            FROZEN_FLICK_DURATION,
        )
        Instructions.tap_flick.show()
    if hit:
        norm_note.play_hit_effects()
        crit_note.play_hit_effects()
    if post_hit:
        norm_note.draw_slot_effects(post_hit)
        crit_note.draw_slot_effects(post_hit)
    if end:
        pass
    return end.is_done


def down_flick_phase(t: PhaseTime):
    intro = t.first(INTRO_DURATION)
    fall = intro.next(FALL_DURATION)
    frozen = fall.next(FROZEN_TAP_DURATION + FROZEN_FLICK_DURATION, repeats=FROZEN_REPEATS)
    hit = t.instant(frozen.end - FROZEN_FLICK_DURATION)
    end = frozen.next(END_DURATION)
    post_hit = t.range(hit.timing, end.end)

    norm_note = TutorialNoteInfo.of(
        kind=NoteKind.NORM_FLICK,
        lane=-LANE,
        size=SIZE,
        direction=FlickDirection.DOWN_RIGHT,
    )
    crit_note = TutorialNoteInfo.of(
        kind=NoteKind.CRIT_FLICK,
        lane=LANE,
        size=SIZE,
        direction=FlickDirection.DOWN_LEFT,
    )
    if intro:
        zoom_to_center()
        norm_note.draw_intro()
        crit_note.draw_intro()
    if fall:
        norm_note.draw_fall(fall)
        crit_note.draw_fall(fall)
    if frozen:
        if hit.is_upcoming:
            norm_note.draw_frozen()
            crit_note.draw_frozen()
        paint_tap_flick_motion(
            transformed_vec_at(norm_note.lane),
            ANGLE_DOWN_RIGHT,
            frozen.progress,
            FROZEN_TAP_DURATION,
            FROZEN_FLICK_DURATION,
            offset=True,
        )
        paint_tap_flick_motion(
            transformed_vec_at(crit_note.lane),
            ANGLE_DOWN_LEFT,
            frozen.progress,
            FROZEN_TAP_DURATION,
            FROZEN_FLICK_DURATION,
            offset=True,
        )
        Instructions.tap_flick.show()
    if hit:
        norm_note.play_hit_effects()
        crit_note.play_hit_effects()
    if post_hit:
        norm_note.draw_slot_effects(post_hit)
        crit_note.draw_slot_effects(post_hit)
    if end:
        pass
    return end.is_done


PHASES: tuple[Callable[[PhaseTime], bool], ...] = (
    tap_phase,
    omni_flick_phase,
    up_flick_phase,
    down_flick_phase,
)
