from __future__ import annotations

from math import floor
from typing import Self

from sonolus.script.bucket import Judgment
from sonolus.script.effect import LoopedEffectHandle
from sonolus.script.globals import level_memory
from sonolus.script.instruction import clear_instruction
from sonolus.script.interval import remap, remap_clamped
from sonolus.script.particle import ParticleHandle
from sonolus.script.record import Record
from sonolus.script.runtime import set_particle_transform, set_skin_transform, time
from sonolus.script.transform import Transform2d
from sonolus.script.vec import Vec2

from sekai.lib.connector import destroy_looped_particle, destroy_looped_sfx
from sekai.lib.layout import FlickDirection, transformed_vec_at
from sekai.lib.note import NoteKind, draw_note, draw_tutorial_note_slot_effects, play_note_hit_effects
from sekai.lib.stage import draw_stage


@level_memory
class PhaseState:
    start_time: float
    linear_slide_particle: ParticleHandle
    circular_slide_particle: ParticleHandle
    slide_sfx: LoopedEffectHandle
    slide_is_active: bool
    prev_time: float


def update_start():
    PhaseState.slide_is_active = False
    clear_instruction()
    draw_stage()
    reset_zoom()


def update_end():
    if not PhaseState.slide_is_active:
        destroy_looped_particle(PhaseState.linear_slide_particle)
        destroy_looped_particle(PhaseState.circular_slide_particle)
        destroy_looped_sfx(PhaseState.slide_sfx)
    PhaseState.prev_time = time()


def reset_phase():
    PhaseState.start_time = time()
    destroy_looped_particle(PhaseState.linear_slide_particle)
    destroy_looped_particle(PhaseState.circular_slide_particle)
    destroy_looped_sfx(PhaseState.slide_sfx)


def get_hold_effect_handles() -> tuple[ParticleHandle, ParticleHandle, LoopedEffectHandle]:
    PhaseState.slide_is_active = True
    return (
        PhaseState.linear_slide_particle,
        PhaseState.circular_slide_particle,
        PhaseState.slide_sfx,
    )


def current_phase_time() -> PhaseTime:
    """Return the current phase timing information."""
    return PhaseTime(time() - PhaseState.start_time, PhaseState.prev_time - PhaseState.start_time)


def phase_time_to_time(phase_time: float) -> float:
    return phase_time + PhaseState.start_time


class PhaseTime(Record):
    time: float
    prev_time: float

    def range(self, start: float, end: float, segments: int = 1) -> PhaseRange:
        return PhaseRange(self, start, end, segments)

    def first(self, end: float, repeats: int = 1) -> PhaseRange:
        return self.range(0, end * repeats, segments=repeats)

    def instant(self, timing: float) -> PhaseInstant:
        return PhaseInstant(self, timing)


class PhaseRange(Record):
    phase: PhaseTime
    start: float
    end: float
    segments: int

    @property
    def is_active(self):
        return self.start <= self.phase.time < self.end

    @property
    def progress(self) -> float:
        if self.segments == 1:
            return remap(self.start, self.end, 0, 1, self.phase.time)
        else:
            return remap_clamped(self.start, self.end, 0, 1, self.phase.time) * self.segments % 1

    @property
    def current_segment(self) -> int:
        return floor(remap_clamped(self.start, self.end, 0, self.segments, self.phase.time))

    @property
    def is_done(self):
        return self.phase.time >= self.end

    def next(self, duration: float, repeats: int = 1):
        return self.phase.range(self.end, self.end + duration * repeats, segments=repeats)

    def start_instant(self) -> PhaseInstant:
        return self.phase.instant(self.start)

    def end_instant(self) -> PhaseInstant:
        return self.phase.instant(self.end)

    def __bool__(self):
        return self.is_active


class PhaseInstant(Record):
    phase: PhaseTime
    timing: float

    @property
    def is_active(self):
        return self.phase.prev_time < self.timing <= self.phase.time

    @property
    def is_done(self):
        return self.phase.time >= self.timing and not self.is_active

    @property
    def is_upcoming(self):
        return self.phase.time < self.timing

    def __bool__(self):
        return self.is_active


def zoom_to(pos: Vec2):
    transform = Transform2d.new().translate(-pos).scale(Vec2(1.8, 1.8))
    set_skin_transform(transform)
    set_particle_transform(transform)


def zoom_to_center():
    zoom_to(transformed_vec_at(0, 0.82))


def reset_zoom():
    transform = Transform2d.new()
    set_skin_transform(transform)
    set_particle_transform(transform)


class TutorialNoteInfo[Kind](Record):
    lane: float
    size: float
    direction: FlickDirection

    @classmethod
    def of(cls, kind: NoteKind, lane: float, size: float, direction: FlickDirection = FlickDirection.UP_OMNI) -> Self:
        return cls[kind](lane=lane, size=size, direction=direction)  # type: ignore

    @property
    def kind(self) -> NoteKind:
        return self.type_var_value(Kind)

    def draw_intro(self):
        draw_note(
            kind=self.kind,
            lane=self.lane,
            size=self.size,
            progress=1,
            direction=self.direction,
            target_time=time(),
        )

    def draw_fall(self, fall_range: PhaseRange):
        draw_note(
            kind=self.kind,
            lane=self.lane,
            size=self.size,
            progress=fall_range.progress,
            direction=self.direction,
            target_time=phase_time_to_time(fall_range.end),
        )

    def draw_frozen(self):
        draw_note(
            kind=self.kind,
            lane=self.lane,
            size=self.size,
            progress=1,
            direction=self.direction,
            target_time=time(),
        )

    def play_hit_effects(self):
        play_note_hit_effects(
            kind=self.kind,
            lane=self.lane,
            size=self.size,
            direction=self.direction,
            judgment=Judgment.PERFECT,
        )

    def draw_slot_effects(self, end_range: PhaseRange):
        draw_tutorial_note_slot_effects(
            kind=self.kind,
            lane=self.lane,
            size=self.size,
            start_time=phase_time_to_time(end_range.start),
        )
