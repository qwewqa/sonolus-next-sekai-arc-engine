from collections.abc import Callable
from math import pi

from sekai.lib.layout import FlickDirection, transformed_vec_at
from sekai.lib.note import NoteKind
from sekai.tutorial.framework import PhaseTime, TutorialNoteInfo, zoom_to_center
from sekai.tutorial.instructions import Instructions
from sekai.tutorial.painting import paint_tap_motion

ANGLE_UP_LEFT = pi / 2 + pi / 6
ANGLE_UP_RIGHT = pi / 2 - pi / 6
ANGLE_DOWN_LEFT = -pi / 2 - pi / 6
ANGLE_DOWN_RIGHT = -pi / 2 + pi / 6

INTRO_DURATION = 1.5
FALL_DURATION = 1.5
FROZEN_REPEATS = 4
FROZEN_TAP_DURATION = 1
FROZEN_HOLD_DURATION = 1
FROZEN_FLICK_DURATION = 0.5
FROZEN_RELEASE_DURATION = 1
END_DURATION = 1.5


def tap_phase(t: PhaseTime):
    intro = t.first(INTRO_DURATION)
    fall = intro.next(FALL_DURATION)
    frozen = fall.next(FROZEN_TAP_DURATION, repeats=FROZEN_REPEATS)
    hit = frozen.end_instant()
    end = frozen.next(END_DURATION)

    norm_note = TutorialNoteInfo.of(
        kind=NoteKind.NORM_TAP,
        lane=-1,
        size=1,
        direction=FlickDirection.UP_OMNI,
    )
    crit_note = TutorialNoteInfo.of(
        kind=NoteKind.CRIT_TAP,
        lane=1,
        size=1,
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
    if end:
        norm_note.draw_slot_effects(end)
        crit_note.draw_slot_effects(end)
    return end.is_done


PHASES: tuple[Callable[[PhaseTime], bool], ...] = (tap_phase,)
