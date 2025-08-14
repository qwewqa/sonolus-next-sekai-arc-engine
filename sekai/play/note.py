from __future__ import annotations

from typing import cast

from sonolus.script.archetype import EntityRef, PlayArchetype, StandardImport, entity_data, imported
from sonolus.script.interval import Interval
from sonolus.script.runtime import time
from sonolus.script.timing import beat_to_time

from sekai.lib.layout import preempt_time, progress_to
from sekai.lib.note import NoteKind, draw_note
from sekai.lib.options import Options
from sekai.lib.timescale import group_scaled_time, group_scaled_time_to_first_time, group_time_to_scaled_time
from sekai.play import connector
from sekai.play.timescale import TimescaleGroup


class BaseNote(PlayArchetype):
    beat: StandardImport.BEAT
    lane: float = imported()
    size: float = imported()
    direction: int = imported()
    slide_ref: EntityRef[connector.BaseSlideConnector] = imported(name="slide")
    attach_ref: EntityRef[connector.BaseSlideConnector] = imported(name="attach")
    timescale_group_ref: EntityRef[TimescaleGroup] = imported(name="timeScaleGroup")

    data_init_done: bool = entity_data()
    target_time: float = entity_data()
    spawn_time: float = entity_data()
    start_scaled_time: float = entity_data()
    target_scaled_time: float = entity_data()
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
            self.direction *= -1

        self.target_time = beat_to_time(self.beat)
        self.target_scaled_time = group_time_to_scaled_time(self.timescale_group_ref, self.target_time)
        self.start_scaled_time = self.target_scaled_time - preempt_time()

        # TODO: handle input interval and take min
        self.spawn_time = group_scaled_time_to_first_time(self.timescale_group_ref, self.start_scaled_time)

    def preprocess(self):
        self.init_data()

        match self.kind:
            case NoteKind.INVISIBLE_SLIDE_TICK | NoteKind.ATTACHED_SLIDE_TICK | NoteKind.CRITICAL_ATTACHED_SLIDE_TICK:
                lane, size = self.attach_ref.get().get_attached(self.target_time)
                self.lane = lane
                self.size = size

    def spawn_order(self) -> float:
        if self.kind == NoteKind.SLIDE_ANCHOR:
            return 1e8
        return self.spawn_time

    def should_spawn(self) -> bool:
        if self.kind == NoteKind.SLIDE_ANCHOR:
            return False
        return time() >= self.spawn_time

    def update_parallel(self):
        if time() >= self.target_time:
            self.despawn = True
            return
        draw_note(self.kind, self.lane, self.size, self.progress, self.direction, self.target_time)

    @property
    def kind(self) -> NoteKind:
        return cast(NoteKind, self.key)

    @property
    def progress(self) -> float:
        return progress_to(self.target_scaled_time, group_scaled_time(self.timescale_group_ref))


NormalTapNote = BaseNote.derive("NormalTapNote", is_scored=True, key=NoteKind.TAP)
CriticalTapNote = BaseNote.derive("CriticalTapNote", is_scored=True, key=NoteKind.CRITICAL_TAP)
NormalFlickNote = BaseNote.derive("NormalFlickNote", is_scored=True, key=NoteKind.FLICK)
CriticalFlickNote = BaseNote.derive("CriticalFlickNote", is_scored=True, key=NoteKind.CRITICAL_FLICK)
NormalTraceNote = BaseNote.derive("NormalTraceNote", is_scored=True, key=NoteKind.TRACE)
CriticalTraceNote = BaseNote.derive("CriticalTraceNote", is_scored=True, key=NoteKind.CRITICAL_TRACE)
NormalTraceFlickNote = BaseNote.derive("NormalTraceFlickNote", is_scored=True, key=NoteKind.TRACE_FLICK)
CriticalTraceFlickNote = BaseNote.derive("CriticalTraceFlickNote", is_scored=True, key=NoteKind.CRITICAL_TRACE_FLICK)
NonDirectionalTraceFlickNote = BaseNote.derive(
    "NonDirectionalTraceFlickNote", is_scored=True, key=NoteKind.UNMARKED_TRACE_FLICK
)
NormalSlideTraceNote = BaseNote.derive("NormalSlideTraceNote", is_scored=True, key=NoteKind.TRACE_SLIDE)
CriticalSlideTraceNote = BaseNote.derive("CriticalSlideTraceNote", is_scored=True, key=NoteKind.CRITICAL_TRACE_SLIDE)
NormalSlideStartNote = BaseNote.derive("NormalSlideStartNote", is_scored=True, key=NoteKind.SLIDE_START)
CriticalSlideStartNote = BaseNote.derive("CriticalSlideStartNote", is_scored=True, key=NoteKind.CRITICAL_SLIDE_START)
HiddenSlideStartNote = BaseNote.derive("HiddenSlideStartNote", is_scored=False, key=NoteKind.HIDDEN_SLIDE_START)
NormalTraceSlideStartNote = BaseNote.derive("NormalTraceSlideStartNote", is_scored=True, key=NoteKind.TRACE_SLIDE)
CriticalTraceSlideStartNote = BaseNote.derive(
    "CriticalTraceSlideStartNote", is_scored=True, key=NoteKind.CRITICAL_TRACE_SLIDE
)
NormalSlideEndNote = BaseNote.derive("NormalSlideEndNote", is_scored=True, key=NoteKind.SLIDE_END)
CriticalSlideEndNote = BaseNote.derive("CriticalSlideEndNote", is_scored=True, key=NoteKind.CRITICAL_SLIDE_END)
NormalTraceSlideEndNote = BaseNote.derive("NormalTraceSlideEndNote", is_scored=True, key=NoteKind.TRACE_SLIDE_END)
CriticalTraceSlideEndNote = BaseNote.derive(
    "CriticalTraceSlideEndNote", is_scored=True, key=NoteKind.CRITICAL_TRACE_SLIDE_END
)
NormalSlideEndFlickNote = BaseNote.derive("NormalSlideEndFlickNote", is_scored=True, key=NoteKind.SLIDE_END_FLICK)
CriticalSlideEndFlickNote = BaseNote.derive(
    "CriticalSlideEndFlickNote", is_scored=True, key=NoteKind.CRITICAL_SLIDE_END_FLICK
)
InvisibleSlideTickNote = BaseNote.derive("IgnoredSlideTickNote", is_scored=True, key=NoteKind.INVISIBLE_SLIDE_TICK)
NormalSlideTickNote = BaseNote.derive("NormalSlideTickNote", is_scored=True, key=NoteKind.SLIDE_TICK)
CriticalSlideTickNote = BaseNote.derive("CriticalSlideTickNote", is_scored=True, key=NoteKind.CRITICAL_SLIDE_TICK)
SideAnchor = BaseNote.derive("HiddenSlideTickNote", is_scored=False, key=NoteKind.SLIDE_ANCHOR)
NormalAttachedSlideTickNote = BaseNote.derive(
    "NormalAttachedSlideTickNote", is_scored=True, key=NoteKind.ATTACHED_SLIDE_TICK
)
CriticalAttachedSlideTickNote = BaseNote.derive(
    "CriticalAttachedSlideTickNote", is_scored=True, key=NoteKind.CRITICAL_ATTACHED_SLIDE_TICK
)
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
    HiddenSlideStartNote,
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
    SideAnchor,
    NormalAttachedSlideTickNote,
    CriticalAttachedSlideTickNote,
    DamageNote,
)
