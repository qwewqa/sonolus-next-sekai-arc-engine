from __future__ import annotations

from math import floor
from typing import Self

from sonolus.script.array import Array, Dim
from sonolus.script.bucket import Judgment
from sonolus.script.effect import LoopedEffectHandle
from sonolus.script.globals import level_memory
from sonolus.script.instruction import clear_instruction
from sonolus.script.interval import lerp, remap, remap_clamped, unlerp
from sonolus.script.particle import ParticleHandle
from sonolus.script.record import Record
from sonolus.script.runtime import set_particle_transform, set_skin_transform, time
from sonolus.script.transform import Transform2d
from sonolus.script.vec import Vec2

from sekai.lib.connector import (
    CONNECTOR_SLOT_SPAWN_PERIOD,
    CONNECTOR_TRAIL_SPAWN_PERIOD,
    ConnectorKind,
    ConnectorVisualState,
    destroy_looped_particle,
    destroy_looped_sfx,
    draw_connector,
    draw_connector_slot_glow_effect,
    spawn_connector_slot_particles,
    spawn_linear_connector_trail_particle,
    update_circular_connector_particle,
    update_connector_sfx,
    update_linear_connector_particle,
)
from sekai.lib.ease import EaseType, ease
from sekai.lib.layout import FlickDirection, transformed_vec_at
from sekai.lib.note import (
    NoteKind,
    draw_note,
    draw_slide_note_head,
    draw_tutorial_note_slot_effects,
    play_note_hit_effects,
)
from sekai.lib.stage import draw_stage
from sekai.tutorial.painting import paint_hold_motion


class SlideEffectHandles(Record):
    linear: ParticleHandle
    circular: ParticleHandle
    sfx: LoopedEffectHandle
    next_trail_spawn_time: float
    next_slot_spawn_time: float

    def destroy(self):
        destroy_looped_particle(self.linear)
        destroy_looped_particle(self.circular)
        destroy_looped_sfx(self.sfx)
        self.next_trail_spawn_time = 0
        self.next_slot_spawn_time = 0


@level_memory
class PhaseState:
    start_time: float
    slide_handles: Array[SlideEffectHandles, Dim[2]]
    slide_is_active: bool
    prev_time: float


def update_start():
    PhaseState.slide_is_active = False
    clear_instruction()
    draw_stage()
    reset_zoom()


def update_end():
    if not PhaseState.slide_is_active:
        for handles in PhaseState.slide_handles:
            handles.destroy()
    PhaseState.prev_time = time()


def reset_phase():
    PhaseState.start_time = time()
    for handles in PhaseState.slide_handles:
        handles.destroy()


def get_slide_effect_handles(index: int) -> SlideEffectHandles:
    PhaseState.slide_is_active = True
    return PhaseState.slide_handles[index]


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

    @property
    def time_since_start(self) -> float:
        return self.phase.time - self.start

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
    transform = Transform2d.new().translate(-pos).scale(Vec2(1.75, 1.75))
    set_skin_transform(transform)
    set_particle_transform(transform)


def zoom_for_intro():
    zoom_to(transformed_vec_at(0, 0.8))


def reset_zoom():
    transform = Transform2d.new()
    set_skin_transform(transform)
    set_particle_transform(transform)


class TutorialNoteInfo[Kind](Record):
    lane: float
    size: float
    direction: FlickDirection
    offset: float

    @classmethod
    def of(
        cls,
        kind: NoteKind,
        lane: float,
        size: float,
        direction: FlickDirection = FlickDirection.UP_OMNI,
        offset: float = 0,
    ) -> Self:
        return cls[kind](lane=lane, size=size, direction=direction, offset=offset)  # type: ignore

    @property
    def kind(self) -> NoteKind:
        return self.type_var_value(Kind)

    def draw(self, progress: float = 1):
        draw_note(
            kind=self.kind,
            lane=self.lane,
            size=self.size,
            progress=progress + self.offset,
            direction=self.direction,
            target_time=time() + 1 - progress - self.offset,
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

    def draw_connector_to(
        self,
        other: TutorialNoteInfo,
        critical: bool,
        active: bool,
        progress: float = 1,
        active_head_kind: NoteKind = NoteKind.ANCHOR,
        ease_type: EaseType = EaseType.OUT_QUAD,
        show_touch: bool = False,
        effect_index: int = -1,
    ):
        kind = ConnectorKind.ACTIVE_CRITICAL if critical else ConnectorKind.ACTIVE_NORMAL
        visual_state = ConnectorVisualState.ACTIVE if active else ConnectorVisualState.WAITING
        head_progress = progress + self.offset
        head_target_time = time() + 1 - progress - self.offset
        tail_progress = progress + other.offset
        tail_target_time = time() + 1 - progress - other.offset
        draw_connector(
            kind=kind,
            visual_state=visual_state,
            ease_type=ease_type,
            head_lane=self.lane,
            head_size=self.size,
            head_progress=head_progress,
            head_target_time=head_target_time,
            tail_lane=other.lane,
            tail_size=other.size,
            tail_progress=tail_progress,
            tail_target_time=tail_target_time,
            segment_head_target_time=head_target_time,
            segment_head_lane=self.lane,
            segment_head_alpha=1,
            segment_tail_target_time=tail_target_time,
            segment_tail_alpha=1,
        )
        if effect_index >= 0 and tail_progress < 1 < head_progress and active:
            frac = unlerp(head_progress, tail_progress, 1)
            eased_frac = ease(ease_type, frac)
            lane = lerp(self.lane, other.lane, eased_frac)
            size = lerp(self.size, other.size, eased_frac)
            handles = get_slide_effect_handles(effect_index)
            update_circular_connector_particle(
                handles.circular,
                kind,
                lane,
                replace=False,
            )
            update_linear_connector_particle(
                handles.linear,
                kind,
                lane,
                replace=False,
            )
            if time() >= handles.next_trail_spawn_time:
                handles.next_trail_spawn_time = max(
                    handles.next_trail_spawn_time + CONNECTOR_TRAIL_SPAWN_PERIOD,
                    time() + CONNECTOR_TRAIL_SPAWN_PERIOD / 2,
                )
                spawn_linear_connector_trail_particle(kind, lane)
            if time() >= handles.next_slot_spawn_time:
                handles.next_slot_spawn_time = max(
                    handles.next_slot_spawn_time + CONNECTOR_SLOT_SPAWN_PERIOD,
                    time() + CONNECTOR_SLOT_SPAWN_PERIOD / 2,
                )
                spawn_connector_slot_particles(kind, lane, size)
            update_connector_sfx(
                handles.sfx,
                kind,
                replace=False,
            )
            draw_connector_slot_glow_effect(kind, head_target_time, lane, size)
            draw_slide_note_head(
                active_head_kind,
                lane,
                size,
                head_target_time,
            )
            if show_touch:
                paint_hold_motion(transformed_vec_at(lane))
