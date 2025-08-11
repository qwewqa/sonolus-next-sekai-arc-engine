from sonolus.script.archetype import PlayArchetype, StandardImport, entity_data, imported
from sonolus.script.debug import debug_log
from sonolus.script.interval import Interval
from sonolus.script.runtime import time
from sonolus.script.timing import beat_to_time

from sekai.lib.layout import approach_to, preempt_time
from sekai.lib.note import NoteKind, draw_note
from sekai.lib.options import Options
from sekai.lib.timescale import extended_scaled_time, extended_scaled_time_to_first_time, extended_time_to_scaled_time


class BaseNote(PlayArchetype):
    beat: StandardImport.BEAT
    lane: float = imported()
    size: float = imported()
    direction: int = imported()
    slide_ref_index: int = imported(name="slide")
    attach_ref_index: int = imported(name="attach")
    timescale_group_index: int = imported(name="timeScaleGroup")

    target_time: float = entity_data()
    spawn_time: float = entity_data()
    visual_interval: Interval = entity_data()
    input_interval: Interval = entity_data()

    @classmethod
    def global_preprocess(cls):
        pass

    def preprocess(self):
        if Options.mirror:
            self.lane *= -1
            self.direction *= -1

        self.target_time = beat_to_time(self.beat)
        self.visual_interval.end = extended_time_to_scaled_time(self.timescale_group_index, self.target_time)
        self.visual_interval.start = self.visual_interval.end - preempt_time()

        # TODO: handle input interval and take min
        self.spawn_time = extended_scaled_time_to_first_time(self.timescale_group_index, self.visual_interval.start)
        if self.index == 2665:
            debug_log(self.spawn_time)
            debug_log(self.visual_interval.end)

    def spawn_order(self) -> float:
        if self.kind == NoteKind.IGNORED_SLIDE_TICK:
            return 1e8
        return self.spawn_time

    def should_spawn(self) -> bool:
        if self.kind == NoteKind.IGNORED_SLIDE_TICK:
            return False
        return time() >= self.spawn_time

    def update_parallel(self):
        draw_note(self.kind, self.lane, self.size, self.progress, self.direction, self.target_time)

    @property
    def kind(self) -> NoteKind:
        return self.key  # type: ignore

    @property
    def progress(self) -> float:
        return approach_to(self.visual_interval.end, extended_scaled_time(self.timescale_group_index))


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
IgnoredSlideTickNote = BaseNote.derive("IgnoredSlideTickNote", is_scored=False, key=NoteKind.IGNORED_SLIDE_TICK)
NormalSlideTickNote = BaseNote.derive("NormalSlideTickNote", is_scored=True, key=NoteKind.SLIDE_TICK)
CriticalSlideTickNote = BaseNote.derive("CriticalSlideTickNote", is_scored=True, key=NoteKind.CRITICAL_SLIDE_TICK)
HiddenSlideTickNote = BaseNote.derive("HiddenSlideTickNote", is_scored=True, key=NoteKind.HIDDEN_SLIDE_TICK)
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
    IgnoredSlideTickNote,
    NormalSlideTickNote,
    CriticalSlideTickNote,
    HiddenSlideTickNote,
    NormalAttachedSlideTickNote,
    CriticalAttachedSlideTickNote,
    DamageNote,
)
