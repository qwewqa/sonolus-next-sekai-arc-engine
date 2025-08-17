from __future__ import annotations

from typing import cast

from sonolus.script.archetype import EntityRef, PlayArchetype, StandardImport, entity_data, imported
from sonolus.script.array import Dim
from sonolus.script.bucket import JudgmentWindow
from sonolus.script.containers import VarArray
from sonolus.script.globals import level_memory
from sonolus.script.interval import Interval
from sonolus.script.runtime import input_offset, time
from sonolus.script.timing import beat_to_time

from sekai.lib.layout import Direction, preempt_time, progress_to
from sekai.lib.note import NoteKind, draw_note, get_note_bucket, get_note_window, invert_direction
from sekai.lib.options import Options
from sekai.lib.timescale import group_scaled_time, group_scaled_time_to_first_time, group_time_to_scaled_time
from sekai.play import connector
from sekai.play.timescale import TimescaleGroup


class BaseNote(PlayArchetype):
    beat: StandardImport.BEAT
    lane: float = imported()
    size: float = imported()
    direction: Direction = imported()
    slide_ref: EntityRef[connector.BaseSlideConnector] = imported(name="slide")
    attach_ref: EntityRef[connector.BaseSlideConnector] = imported(name="attach")
    timescale_group_ref: EntityRef[TimescaleGroup] = imported(name="timeScaleGroup")

    data_init_done: bool = entity_data()
    target_time: float = entity_data()
    start_time: float = entity_data()
    spawn_time: float = entity_data()
    start_scaled_time: float = entity_data()
    target_scaled_time: float = entity_data()
    judgment_window: JudgmentWindow = entity_data()
    input_interval: Interval = entity_data()

    @classmethod
    def global_preprocess(cls):
        pass

    def init_data(self):
        if self.data_init_done:
            return

        self.data_init_done = True

        if Options.mirror:
            self.lane *= -1
            self.direction = invert_direction(self.direction)

        self.target_time = beat_to_time(self.beat)
        self.target_scaled_time = group_time_to_scaled_time(self.timescale_group_ref, self.target_time)
        self.start_scaled_time = self.target_scaled_time - preempt_time()

        self.judgment_window = get_note_window(self.kind)

        if self.judgment_window.good.length > 0:
            self.input_interval = self.judgment_window.good + self.target_time + input_offset()
        else:
            self.input_interval = Interval(0, 1) + self.target_time + input_offset()

        self.start_time = group_scaled_time_to_first_time(self.timescale_group_ref, self.start_scaled_time)
        self.spawn_time = min(self.start_time, self.input_interval.start)

    def preprocess(self):
        self.init_data()

        self.result.bucket = get_note_bucket(self.kind)

        if self.attach_ref.index > 0:
            lane, size = self.attach_ref.get().get_attached(self.target_time)
            self.lane = lane
            self.size = size

    def spawn_order(self) -> float:
        if self.kind == NoteKind.JOINT:
            return 1e8
        return self.spawn_time

    def should_spawn(self) -> bool:
        if self.kind == NoteKind.JOINT:
            return False
        return time() >= self.spawn_time

    def update_parallel(self):
        if time() < self.start_time:
            return
        if time() > self.input_interval.end:
            self.despawn = True
        if self.despawn:
            return
        draw_note(self.kind, self.lane, self.size, self.progress, self.direction, self.target_time)

    @property
    def kind(self) -> NoteKind:
        return cast(NoteKind, self.key)

    @property
    def progress(self) -> float:
        return progress_to(self.target_scaled_time, group_scaled_time(self.timescale_group_ref))


@level_memory
class NoteMemory:
    active_tappable_notes: VarArray[EntityRef[BaseNote], Dim[32]]


NormalTapNote = BaseNote.derive("NormalTapNote", is_scored=True, key=NoteKind.NORM_TAP)
CriticalTapNote = BaseNote.derive("CriticalTapNote", is_scored=True, key=NoteKind.CRIT_TAP)
NormalFlickNote = BaseNote.derive("NormalFlickNote", is_scored=True, key=NoteKind.NORM_FLICK)
CriticalFlickNote = BaseNote.derive("CriticalFlickNote", is_scored=True, key=NoteKind.CRIT_FLICK)
NormalTraceNote = BaseNote.derive("NormalTraceNote", is_scored=True, key=NoteKind.NORM_TRACE)
CriticalTraceNote = BaseNote.derive("CriticalTraceNote", is_scored=True, key=NoteKind.CRIT_TRACE)
NormalTraceFlickNote = BaseNote.derive("NormalTraceFlickNote", is_scored=True, key=NoteKind.NORM_TRACE_FLICK)
CriticalTraceFlickNote = BaseNote.derive("CriticalTraceFlickNote", is_scored=True, key=NoteKind.CRIT_TRACE_FLICK)
NonDirectionalTraceFlickNote = BaseNote.derive(
    "NonDirectionalTraceFlickNote", is_scored=True, key=NoteKind.NORM_TRACE_FLICK
)
NormalSlideTraceNote = BaseNote.derive("NormalSlideTraceNote", is_scored=True, key=NoteKind.NORM_TRACE)
CriticalSlideTraceNote = BaseNote.derive("CriticalSlideTraceNote", is_scored=True, key=NoteKind.CRIT_TRACE)
NormalSlideStartNote = BaseNote.derive("NormalSlideStartNote", is_scored=True, key=NoteKind.NORM_HEAD_TAP)
CriticalSlideStartNote = BaseNote.derive("CriticalSlideStartNote", is_scored=True, key=NoteKind.CRIT_HEAD_TAP)
SlideStartAnchor = BaseNote.derive("HiddenSlideStartNote", is_scored=False, key=NoteKind.JOINT)
NormalTraceSlideStartNote = BaseNote.derive("NormalTraceSlideStartNote", is_scored=True, key=NoteKind.NORM_HEAD_TRACE)
CriticalTraceSlideStartNote = BaseNote.derive(
    "CriticalTraceSlideStartNote", is_scored=True, key=NoteKind.CRIT_HEAD_TRACE
)
NormalSlideEndNote = BaseNote.derive("NormalSlideEndNote", is_scored=True, key=NoteKind.NORM_TAIL_RELEASE)
CriticalSlideEndNote = BaseNote.derive("CriticalSlideEndNote", is_scored=True, key=NoteKind.CRIT_TAIL_RELEASE)
NormalTraceSlideEndNote = BaseNote.derive("NormalTraceSlideEndNote", is_scored=True, key=NoteKind.NORM_TAIL_TRACE)
CriticalTraceSlideEndNote = BaseNote.derive("CriticalTraceSlideEndNote", is_scored=True, key=NoteKind.CRIT_TAIL_TRACE)
NormalSlideEndFlickNote = BaseNote.derive("NormalSlideEndFlickNote", is_scored=True, key=NoteKind.NORM_TAIL_FLICK)
CriticalSlideEndFlickNote = BaseNote.derive("CriticalSlideEndFlickNote", is_scored=True, key=NoteKind.CRIT_TAIL_FLICK)
InvisibleSlideTickNote = BaseNote.derive("IgnoredSlideTickNote", is_scored=True, key=NoteKind.HIDE_TICK)
NormalSlideTickNote = BaseNote.derive("NormalSlideTickNote", is_scored=True, key=NoteKind.NORM_TICK)
CriticalSlideTickNote = BaseNote.derive("CriticalSlideTickNote", is_scored=True, key=NoteKind.CRIT_TICK)
SlideAnchor = BaseNote.derive("HiddenSlideTickNote", is_scored=False, key=NoteKind.JOINT)
NormalAttachedSlideTickNote = BaseNote.derive("NormalAttachedSlideTickNote", is_scored=True, key=NoteKind.NORM_TICK)
CriticalAttachedSlideTickNote = BaseNote.derive("CriticalAttachedSlideTickNote", is_scored=True, key=NoteKind.CRIT_TICK)
DamageNote = BaseNote.derive("DamageNote", is_scored=True, key=NoteKind.DAMAGE)

ALL_NOTE_ARCHETYPES = (
    NormalTapNote,
    CriticalTapNote,
    NormalFlickNote,
    CriticalFlickNote,
    NormalTraceNote,
    CriticalTraceNote,
    NormalTraceFlickNote,
    CriticalTraceFlickNote,
    NonDirectionalTraceFlickNote,
    NormalSlideTraceNote,
    CriticalSlideTraceNote,
    NormalSlideStartNote,
    CriticalSlideStartNote,
    SlideStartAnchor,
    NormalTraceSlideStartNote,
    CriticalTraceSlideStartNote,
    NormalSlideEndNote,
    CriticalSlideEndNote,
    NormalTraceSlideEndNote,
    CriticalTraceSlideEndNote,
    NormalSlideEndFlickNote,
    CriticalSlideEndFlickNote,
    InvisibleSlideTickNote,
    NormalSlideTickNote,
    CriticalSlideTickNote,
    SlideAnchor,
    NormalAttachedSlideTickNote,
    CriticalAttachedSlideTickNote,
    DamageNote,
)
