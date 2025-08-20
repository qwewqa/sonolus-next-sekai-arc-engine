from __future__ import annotations

from math import pi
from typing import assert_never, cast

from sonolus.script.archetype import (
    EntityRef,
    PlayArchetype,
    StandardImport,
    entity_data,
    entity_memory,
    exported,
    imported,
    shared_memory,
)
from sonolus.script.array import Dim
from sonolus.script.bucket import Judgment, JudgmentWindow
from sonolus.script.containers import VarArray
from sonolus.script.globals import level_memory
from sonolus.script.interval import Interval
from sonolus.script.quad import Rect
from sonolus.script.runtime import Touch, delta_time, input_offset, offset_adjusted_time, time, touches
from sonolus.script.timing import beat_to_time

from sekai.lib.buckets import WINDOW_SCALE
from sekai.lib.connector import ActiveConnectorInfo
from sekai.lib.layout import Direction, Layout, layout_hitbox, preempt_time, progress_to
from sekai.lib.note import (
    NoteKind,
    draw_note,
    get_leniency,
    get_note_bucket,
    get_note_window,
    has_release_input,
    has_tap_input,
    invert_direction,
    is_head,
    play_note_hit_effects,
)
from sekai.lib.options import Options
from sekai.lib.timescale import group_scaled_time, group_scaled_time_to_first_time, group_time_to_scaled_time
from sekai.play import connector, input_manager
from sekai.play.timescale import TimescaleGroup

DEFAULT_BEST_TOUCH_TIME = -1e8


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

    # The id of the tap that activated this note, for tap notes and flicks or released the note, for release notes.
    # This is set by the input manager rather than the note itself.
    captured_touch_id: int = shared_memory()

    active_connector_info: ActiveConnectorInfo = shared_memory()

    # For trace early touches
    best_touch_time: float = entity_memory()
    best_touch_matches_direction: bool = entity_memory()

    finish_time: float = exported()

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

        self.input_interval = self.judgment_window.good + self.target_time + input_offset()

        self.start_time = group_scaled_time_to_first_time(self.timescale_group_ref, self.start_scaled_time)
        self.spawn_time = min(self.start_time, self.input_interval.start)

    def preprocess(self):
        self.init_data()

        self.result.bucket = get_note_bucket(self.kind)

        self.best_touch_time = DEFAULT_BEST_TOUCH_TIME

        if self.attach_ref.index > 0:
            lane, size = self.attach_ref.get().get_attached_params(self.target_time)
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

    def update_sequential(self):
        if self.despawn:
            return
        if time() in self.input_interval and self.captured_touch_id == 0:
            if has_tap_input(self.kind):
                NoteMemory.active_tap_input_notes.append(self.ref())
            elif has_release_input(self.kind):
                NoteMemory.active_release_input_notes.append(self.ref())

    def touch(self):
        if self.despawn:
            return
        kind = self.kind
        match kind:
            case (
                NoteKind.NORM_TAP
                | NoteKind.CRIT_TAP
                | NoteKind.NORM_HEAD_TAP
                | NoteKind.CRIT_HEAD_TAP
                | NoteKind.NORM_TAIL_TAP
                | NoteKind.CRIT_TAIL_TAP
            ):
                self.handle_tap_input()
            case NoteKind.NORM_FLICK | NoteKind.CRIT_FLICK | NoteKind.NORM_HEAD_FLICK | NoteKind.CRIT_HEAD_FLICK:
                self.handle_flick_input()
            case NoteKind.NORM_TAIL_FLICK | NoteKind.CRIT_TAIL_FLICK:
                self.handle_tail_flick_input()
            case (
                NoteKind.NORM_TRACE
                | NoteKind.CRIT_TRACE
                | NoteKind.NORM_HEAD_TRACE
                | NoteKind.CRIT_HEAD_TRACE
                | NoteKind.NORM_TAIL_TRACE
                | NoteKind.CRIT_TAIL_TRACE
            ):
                self.handle_trace_input()
            case (
                NoteKind.NORM_TRACE_FLICK
                | NoteKind.CRIT_TRACE_FLICK
                | NoteKind.NORM_HEAD_TRACE_FLICK
                | NoteKind.CRIT_HEAD_TRACE_FLICK
                | NoteKind.NORM_TAIL_TRACE_FLICK
                | NoteKind.CRIT_TAIL_TRACE_FLICK
            ):
                self.handle_trace_flick_input()
            case (
                NoteKind.NORM_RELEASE
                | NoteKind.CRIT_RELEASE
                | NoteKind.NORM_HEAD_RELEASE
                | NoteKind.CRIT_HEAD_RELEASE
                | NoteKind.NORM_TAIL_RELEASE
                | NoteKind.CRIT_TAIL_RELEASE
            ):
                self.handle_release_input()
            case NoteKind.NORM_TICK | NoteKind.CRIT_TICK | NoteKind.HIDE_TICK | NoteKind.JOINT:
                self.handle_tick_input()
            case NoteKind.DAMAGE:
                self.handle_damage_input()
            case _:
                assert_never(kind)

    def update_parallel(self):
        if self.despawn:
            return
        if time() < self.start_time:
            return
        if offset_adjusted_time() >= self.target_time and self.best_touch_time > DEFAULT_BEST_TOUCH_TIME:
            if self.best_touch_matches_direction:
                self.judge(self.best_touch_time)
            else:
                self.judge_wrong_way(self.best_touch_time)
            return
        if time() > self.input_interval.end:
            self.fail_late()
            return
        if is_head(self.kind) and time() > self.target_time:
            return
        draw_note(self.kind, self.lane, self.size, self.progress, self.direction, self.target_time)

    def terminate(self):
        self.finish_time = time()

    def handle_tap_input(self):
        if time() < self.input_interval.start:
            return
        if self.captured_touch_id == 0:
            return
        touch = next(tap for tap in touches() if tap.id == self.captured_touch_id)
        self.judge(touch.start_time)

    def handle_release_input(self):
        if time() < self.input_interval.start:
            return
        if self.captured_touch_id == 0:
            return
        touch = next(tap for tap in touches() if tap.id == self.captured_touch_id)
        self.judge(touch.time)

    def handle_flick_input(self):
        if time() < self.input_interval.start:
            return
        if self.captured_touch_id == 0:
            return

        # Another touch is allowed to flick the note as long as it started after the start of the input interval,
        # so we don't care which touch matched the tap id, just that the tap id is set.

        hitbox = self.get_full_hitbox()

        for touch in touches():
            if not self.check_touch_touch_is_eligible_for_flick(hitbox, touch):
                continue
            if not self.check_direction_matches(touch.angle):
                continue
            input_manager.disallow_empty(touch)
            self.judge(touch.time)
            return
        for touch in touches():
            if not self.check_touch_touch_is_eligible_for_flick(hitbox, touch):
                continue
            input_manager.disallow_empty(touch)
            self.judge_wrong_way(touch.time)
            return

    def handle_tail_flick_input(self):
        if time() < self.input_interval.start:
            return

        if offset_adjusted_time() < self.target_time:
            slide_connector = self.slide_ref.get()
            start = slide_connector.start
            if start.active_connector_info.is_active:
                return
            hitbox = slide_connector.active_connector_info.get_hitbox(input_manager.get_leniency(self.kind))
            for touch in touches():
                if not touch.ended and hitbox.contains_point(touch.position):
                    return
            for touch in touches():
                if not self.check_touch_touch_is_eligible_for_early_tail_flick(hitbox, touch):
                    continue
                if not self.check_direction_matches(touch.angle):
                    continue
                input_manager.disallow_empty(touch)
                self.judge(touch.time)
                return
            for touch in touches():
                if not self.check_touch_touch_is_eligible_for_early_tail_flick(hitbox, touch):
                    continue
                input_manager.disallow_empty(touch)
                self.judge_wrong_way(touch.time)
                return
        else:
            hitbox = self.get_full_hitbox()
            for touch in touches():
                # Trace flick eligibility since no tap is needed for tail flicks.
                if not self.check_touch_is_eligible_for_trace_flick(hitbox, touch):
                    continue
                if not self.check_direction_matches(touch.angle):
                    continue
                input_manager.disallow_empty(touch)
                self.judge(touch.time)
                return
            for touch in touches():
                if not self.check_touch_is_eligible_for_trace_flick(hitbox, touch):
                    continue
                input_manager.disallow_empty(touch)
                self.judge_wrong_way(touch.time)
                return

    def handle_trace_input(self):
        if time() < self.input_interval.start:
            return

        hitbox = self.get_full_hitbox()
        has_touch = False
        for touch in touches():
            if not hitbox.contains_point(touch.position):
                continue
            input_manager.disallow_empty(touch)
            has_touch = True
            # Keep going so we disallow empty on all touches that are in the hitbox.
        if not has_touch:
            return
        if offset_adjusted_time() >= self.target_time:
            if offset_adjusted_time() - delta_time() <= self.target_time <= offset_adjusted_time():
                self.complete()
            else:
                self.judge(offset_adjusted_time())
        else:
            self.best_touch_time = offset_adjusted_time()
            self.best_touch_matches_direction = True

    def handle_trace_flick_input(self):
        if time() < self.input_interval.start:
            return

        hitbox = self.get_full_hitbox()
        has_touch = False
        has_correct_direction_touch = False
        for touch in touches():
            if not self.check_touch_is_eligible_for_trace_flick(hitbox, touch):
                continue
            input_manager.disallow_empty(touch)
            has_touch = True
            if self.check_direction_matches(touch.angle):
                has_correct_direction_touch = True
        if not has_touch:
            return
        if offset_adjusted_time() >= self.target_time:
            if offset_adjusted_time() - delta_time() <= self.target_time <= offset_adjusted_time():
                if has_correct_direction_touch:
                    self.complete()
                else:
                    self.complete_wrong_way()
            elif has_correct_direction_touch:
                self.judge(offset_adjusted_time())
            else:
                self.judge_wrong_way(offset_adjusted_time())
        elif (
            has_correct_direction_touch or self.best_touch_time < self.judgment_window.perfect.start + self.target_time
        ):
            self.best_touch_time = offset_adjusted_time()
            self.best_touch_matches_direction = has_correct_direction_touch

    def handle_tick_input(self):
        if time() < self.input_interval.start:
            return

        hitbox = self.get_full_hitbox()
        has_touch = False
        for touch in touches():
            if not hitbox.contains_point(touch.position):
                continue
            input_manager.disallow_empty(touch)
            has_touch = True
        if has_touch:
            self.complete()
        else:
            self.fail_late(0.125)

    def handle_damage_input(self):
        if time() < self.input_interval.start:
            return

        hitbox = self.get_full_hitbox()
        has_touch = False
        for touch in touches():
            if not hitbox.contains_point(touch.position):
                continue
            input_manager.disallow_empty(touch)
            has_touch = True
        if has_touch:
            self.fail_damage()
        else:
            self.complete_damage()

    def check_touch_touch_is_eligible_for_flick(self, hitbox: Rect, touch: Touch) -> bool:
        return (
            touch.start_time >= self.input_interval.start
            and touch.speed >= Layout.flick_speed_threshold
            and (hitbox.contains_point(touch.position) or hitbox.contains_point(touch.prev_position))
        )

    @staticmethod
    def check_touch_touch_is_eligible_for_early_tail_flick(hitbox: Rect, touch: Touch) -> bool:
        return (
            touch.speed >= Layout.flick_speed_threshold
            and (not hitbox.contains_point(touch.position) or touch.ended)
            and hitbox.contains_point(touch.prev_position)
        )

    @staticmethod
    def check_touch_is_eligible_for_trace_flick(hitbox: Rect, touch: Touch) -> bool:
        return touch.speed >= Layout.flick_speed_threshold and (
            hitbox.contains_point(touch.position) or hitbox.contains_point(touch.prev_position)
        )

    def check_direction_matches(self, angle: float) -> bool:
        leniency = pi / 2
        match self.direction:
            case Direction.NONE:
                return True
            case Direction.UP_LEFT:
                target_angle = pi / 2 + 1
            case Direction.UP_RIGHT:
                target_angle = pi / 2 - 1
            case Direction.DOWN_LEFT:
                target_angle = -pi / 2 - 1
            case Direction.DOWN_RIGHT:
                target_angle = -pi / 2 + 1
            case _:
                assert_never(self.direction)
        angle_diff = abs((angle - target_angle + pi) % (2 * pi) - pi)
        return angle_diff <= leniency

    def judge(self, actual_time: float):
        judgment = self.judgment_window.judge(actual_time, self.target_time)
        error = actual_time - self.target_time
        self.result.judgment = judgment
        self.result.accuracy = error
        if self.result.bucket.id != -1:
            self.result.bucket_value = error * WINDOW_SCALE
        self.despawn = True
        self.play_hit_effects()

    def judge_wrong_way(self, actual_time: float):
        judgment = self.judgment_window.judge(actual_time, self.target_time)
        if judgment == Judgment.PERFECT:
            judgment = Judgment.GREAT
        error = actual_time - self.target_time
        self.result.judgment = judgment
        if error in self.judgment_window.perfect:
            self.result.accuracy = self.judgment_window.perfect.end
        else:
            self.result.accuracy = error
        if self.result.bucket.id != -1:
            self.result.bucket_value = error * WINDOW_SCALE
        self.despawn = True
        self.play_hit_effects()

    def complete(self):
        self.result.judgment = Judgment.PERFECT
        self.result.accuracy = 0
        if self.result.bucket.id != -1:
            self.result.bucket_value = 0
        self.despawn = True
        self.play_hit_effects()

    def complete_wrong_way(self):
        self.result.judgment = Judgment.GREAT
        self.result.accuracy = self.judgment_window.good.end
        if self.result.bucket.id != -1:
            self.result.bucket_value = 0
        self.despawn = True
        self.play_hit_effects()

    def complete_damage(self):
        self.result.judgment = Judgment.PERFECT
        self.result.accuracy = 0
        if self.result.bucket.id != -1:
            self.result.bucket_value = 0
        self.despawn = True

    def fail_late(self, accuracy: float | None = None):
        if accuracy is None:
            accuracy = self.judgment_window.good.end
        self.result.judgment = Judgment.MISS
        self.result.accuracy = accuracy
        if self.result.bucket.id != -1:
            self.result.bucket_value = self.judgment_window.good.end * WINDOW_SCALE
        self.despawn = True

    def fail_damage(self):
        self.result.judgment = Judgment.MISS
        self.result.accuracy = 0.125
        self.despawn = True
        self.play_hit_effects()

    def play_hit_effects(self):
        play_note_hit_effects(self.kind, self.lane, self.size, self.direction, self.result.judgment)

    def get_full_hitbox(self) -> Rect:
        leniency = get_leniency(self.kind)
        return layout_hitbox(self.lane - self.size - leniency, self.lane + self.size + leniency)

    @property
    def kind(self) -> NoteKind:
        return cast(NoteKind, self.key)

    @property
    def progress(self) -> float:
        if self.attach_ref.index > 0:
            return self.attach_ref.get().get_attached_progress(self.target_time)
        else:
            return progress_to(self.target_scaled_time, group_scaled_time(self.timescale_group_ref))


@level_memory
class NoteMemory:
    active_tap_input_notes: VarArray[EntityRef[BaseNote], Dim[256]]
    active_release_input_notes: VarArray[EntityRef[BaseNote], Dim[256]]


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

NOTE_ARCHETYPES = (
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
