from __future__ import annotations

from math import pi
from typing import assert_never, cast

from sonolus.script.archetype import (
    AnyArchetype,
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
from sonolus.script.interval import Interval, remap_clamped, unlerp_clamped
from sonolus.script.quad import Quad
from sonolus.script.runtime import Touch, delta_time, input_offset, offset_adjusted_time, time, touches
from sonolus.script.timing import beat_to_time

from sekai.lib import archetype_names
from sekai.lib.buckets import WINDOW_SCALE
from sekai.lib.connector import ActiveConnectorInfo, ConnectorKind
from sekai.lib.ease import EaseType
from sekai.lib.layout import FlickDirection, Layout, layout_hitbox, progress_to
from sekai.lib.note import (
    NoteKind,
    draw_note,
    get_attach_params,
    get_leniency,
    get_note_bucket,
    get_note_window,
    get_visual_spawn_time,
    has_release_input,
    has_tap_input,
    is_head,
    map_note_kind,
    mirror_flick_direction,
    play_note_hit_effects,
    schedule_note_auto_sfx,
)
from sekai.lib.options import Options
from sekai.lib.timescale import group_hide_notes, group_scaled_time, group_time_to_scaled_time
from sekai.play import input_manager

DEFAULT_BEST_TOUCH_TIME = -1e8


class BaseNote(PlayArchetype):
    beat: StandardImport.BEAT
    timescale_group: StandardImport.TIMESCALE_GROUP
    lane: float = imported()
    size: float = imported()
    direction: FlickDirection = imported()
    active_head_ref: EntityRef[BaseNote] = imported(name="activeHead")
    is_attached: bool = imported(name="isAttached")
    connector_ease: EaseType = imported(name="connectorEase")
    segment_kind: ConnectorKind = imported(name="segmentKind")
    segment_alpha: float = imported(name="segmentAlpha")
    attach_head_ref: EntityRef[BaseNote] = imported(name="attachHead")
    attach_tail_ref: EntityRef[BaseNote] = imported(name="attachTail")
    next_ref: EntityRef[BaseNote] = imported(name="next")  # Only for level data; not used in-game.

    kind: NoteKind = entity_data()
    data_init_done: bool = entity_data()
    target_time: float = entity_data()
    visual_start_time: float = entity_data()
    start_time: float = entity_data()
    target_scaled_time: float = entity_data()
    judgment_window: JudgmentWindow = entity_data()
    input_interval: Interval = entity_data()
    unadjusted_input_interval: Interval = entity_data()

    # The id of the tap that activated this note, for tap notes and flicks or released the note, for release notes.
    # This is set by the input manager rather than the note itself.
    captured_touch_id: int = shared_memory()
    captured_touch_time: float = shared_memory()

    active_connector_info: ActiveConnectorInfo = shared_memory()

    # For trace early touches
    best_touch_time: float = entity_memory()
    best_touch_matches_direction: bool = entity_memory()

    should_play_hit_effects: bool = entity_memory()

    end_time: float = exported()
    played_hit_effects: bool = exported()

    def init_data(self):
        if self.data_init_done:
            return

        self.kind = map_note_kind(cast(NoteKind, self.key))

        self.data_init_done = True

        if Options.mirror:
            self.lane *= -1
            self.direction = mirror_flick_direction(self.direction)

        self.target_time = beat_to_time(self.beat)
        self.judgment_window = get_note_window(self.kind)
        self.input_interval = self.judgment_window.good + self.target_time + input_offset()
        self.unadjusted_input_interval = self.judgment_window.good + self.target_time

        if not self.is_attached:
            self.target_scaled_time = group_time_to_scaled_time(self.timescale_group, self.target_time)
            self.visual_start_time = get_visual_spawn_time(self.timescale_group, self.target_scaled_time)
            self.start_time = min(self.visual_start_time, self.input_interval.start)

    def preprocess(self):
        self.init_data()

        self.result.bucket = get_note_bucket(self.kind)

        self.best_touch_time = DEFAULT_BEST_TOUCH_TIME

        if self.is_attached:
            attach_head = self.attach_head_ref.get()
            attach_tail = self.attach_tail_ref.get()
            attach_head.init_data()
            attach_tail.init_data()
            lane, size = get_attach_params(
                ease_type=attach_head.connector_ease,
                head_lane=attach_head.lane,
                head_size=attach_head.size,
                head_target_time=attach_head.target_time,
                tail_lane=attach_tail.lane,
                tail_size=attach_tail.size,
                tail_target_time=attach_tail.target_time,
                target_time=self.target_time,
            )
            self.lane = lane
            self.size = size
            self.visual_start_time = min(attach_head.visual_start_time, attach_tail.visual_start_time)
            self.start_time = min(self.visual_start_time, self.input_interval.start)

        if is_head(self.kind):
            self.active_connector_info.input_lane = self.lane
            self.active_connector_info.input_size = self.size
            self.active_connector_info.prev_input_lane = self.lane
            self.active_connector_info.prev_input_size = self.size

        schedule_note_auto_sfx(self.kind, self.target_time)

    def spawn_order(self) -> float:
        if self.kind == NoteKind.ANCHOR:
            return 1e8
        return self.start_time

    def should_spawn(self) -> bool:
        return time() >= self.start_time

    def update_sequential(self):
        if self.despawn:
            return
        if self.is_scored and time() in self.input_interval and self.captured_touch_id == 0:
            if has_tap_input(self.kind):
                NoteMemory.active_tap_input_notes.append(self.ref())
            elif has_release_input(self.kind) and (
                self.active_head_ref.index <= 0
                or self.active_head_ref.get().is_despawned
                or self.active_head_ref.get().captured_touch_id != 0
                or not self.active_head_ref.get().is_scored
            ):
                NoteMemory.active_release_input_notes.append(self.ref())

    def touch(self):
        if not self.is_scored:
            return
        if self.despawn:
            return
        if time() < self.input_interval.start:
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
            case NoteKind.NORM_TICK | NoteKind.CRIT_TICK | NoteKind.HIDE_TICK:
                self.handle_tick_input()
            case NoteKind.DAMAGE:
                self.handle_damage_input()
            case NoteKind.ANCHOR:
                pass
            case _:
                assert_never(kind)

    def update_parallel(self):
        if self.despawn:
            return
        if not self.is_scored and time() >= self.target_time:
            self.despawn = True
            return
        if time() < self.visual_start_time:
            return
        if offset_adjusted_time() >= self.target_time and self.best_touch_time > DEFAULT_BEST_TOUCH_TIME:
            if self.best_touch_matches_direction:
                self.judge(self.best_touch_time)
            else:
                self.judge_wrong_way(self.best_touch_time)
            return
        if time() > self.input_interval.end:
            self.handle_late_miss()
            return
        if is_head(self.kind) and time() > self.target_time:
            return
        if group_hide_notes(self.timescale_group):
            return
        draw_note(self.kind, self.lane, self.size, self.progress, self.direction, self.target_time)

    def terminate(self):
        if self.should_play_hit_effects:
            # We do this here for parallelism, and to reduce compilation time.
            play_note_hit_effects(self.kind, self.lane, self.size, self.direction, self.result.judgment)
        self.end_time = offset_adjusted_time()
        self.played_hit_effects = self.should_play_hit_effects

    def handle_tap_input(self):
        if time() > self.input_interval.end:
            return
        if self.captured_touch_id == 0:
            return
        touch = next(tap for tap in touches() if tap.id == self.captured_touch_id)
        self.judge(touch.start_time)

    def handle_release_input(self):
        if time() > self.input_interval.end:
            return
        if self.captured_touch_id == 0:
            return
        touch = next(tap for tap in touches() if tap.id == self.captured_touch_id)
        self.judge(touch.time)

    def handle_flick_input(self):
        if time() > self.input_interval.end:
            return
        if self.captured_touch_id == 0:
            return

        # Another touch is allowed to flick the note as long as it started after the start of the input interval,
        # so we don't care which touch matched the tap id, just that the tap id is set.

        hitbox = self.get_full_hitbox()

        for touch in touches():
            if not self.check_touch_touch_is_eligible_for_flick(hitbox, touch):
                continue
            if not self.check_direction_matches(hitbox, touch.angle):
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
        if time() > self.input_interval.end:
            return
        if offset_adjusted_time() < self.target_time:
            active_connector_info = self.active_head_ref.get().active_connector_info
            hitbox = active_connector_info.get_hitbox(input_manager.get_leniency(self.kind))
            prev_hitbox = active_connector_info.get_prev_hitbox(input_manager.get_leniency(self.kind))
            for touch in touches():
                if not touch.ended and hitbox.contains_point(touch.position):
                    return
            for touch in touches():
                if not self.check_touch_touch_is_eligible_for_early_tail_flick(hitbox, prev_hitbox, touch):
                    continue
                if not self.check_direction_matches(hitbox, touch.angle):
                    continue
                input_manager.disallow_empty(touch)
                self.judge(touch.time)
                return
            for touch in touches():
                if not self.check_touch_touch_is_eligible_for_early_tail_flick(hitbox, prev_hitbox, touch):
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
                if not self.check_direction_matches(hitbox, touch.angle):
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
        if time() > self.input_interval.end:
            return
        hitbox = self.get_full_hitbox()
        has_touch = False
        for touch in touches():
            if not self.check_touch_is_eligible_for_trace(hitbox, touch):
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
        if time() > self.input_interval.end:
            return
        hitbox = self.get_full_hitbox()
        has_touch = False
        has_correct_direction_touch = False
        for touch in touches():
            if not self.check_touch_is_eligible_for_trace_flick(hitbox, touch):
                continue
            input_manager.disallow_empty(touch)
            has_touch = True
            if self.check_direction_matches(hitbox, touch.angle):
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

    def handle_late_miss(self):
        kind = self.kind
        match kind:
            case NoteKind.NORM_TICK | NoteKind.CRIT_TICK | NoteKind.HIDE_TICK:
                self.fail_late(0.125)
            case NoteKind.DAMAGE:
                self.complete_damage()
            case (
                NoteKind.NORM_TAP
                | NoteKind.CRIT_TAP
                | NoteKind.NORM_FLICK
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
            ):
                self.fail_late()
            case NoteKind.ANCHOR:
                pass
            case _:
                assert_never(kind)

    def check_touch_touch_is_eligible_for_flick(self, hitbox: Quad, touch: Touch) -> bool:
        return (
            touch.start_time >= self.captured_touch_time
            and touch.speed >= Layout.flick_speed_threshold
            and (hitbox.contains_point(touch.position) or hitbox.contains_point(touch.prev_position))
        )

    def check_touch_touch_is_eligible_for_early_tail_flick(self, hitbox: Quad, prev_hitbox: Quad, touch: Touch) -> bool:
        return (
            touch.time >= self.unadjusted_input_interval.start
            and touch.speed >= Layout.flick_speed_threshold
            and (not hitbox.contains_point(touch.position) or touch.ended)
            and (hitbox.contains_point(touch.prev_position) or prev_hitbox.contains_point(touch.prev_position))
        )

    def check_touch_is_eligible_for_trace(self, hitbox: Quad, touch: Touch) -> bool:
        # Note that this does not check the time, since time may not be updated if the touch is stationary.
        return hitbox.contains_point(touch.position)

    def check_touch_is_eligible_for_trace_flick(self, hitbox: Quad, touch: Touch) -> bool:
        return (
            touch.time >= self.unadjusted_input_interval.start
            and touch.speed >= Layout.flick_speed_threshold
            and (hitbox.contains_point(touch.position) or hitbox.contains_point(touch.prev_position))
        )

    def check_direction_matches(self, hitbox: Quad, angle: float) -> bool:
        leniency = pi / 2
        match self.direction:
            case FlickDirection.UP_OMNI | FlickDirection.DOWN_OMNI:
                return True
            case FlickDirection.UP_LEFT:
                target_angle = pi / 2 + 1
            case FlickDirection.UP_RIGHT:
                target_angle = pi / 2 - 1
            case FlickDirection.DOWN_LEFT:
                target_angle = -pi / 2 - 1
            case FlickDirection.DOWN_RIGHT:
                target_angle = -pi / 2 + 1
            case _:
                assert_never(self.direction)
        target_angle += (hitbox.br - hitbox.bl).angle
        angle_diff = abs((angle - target_angle + pi) % (2 * pi) - pi)
        return angle_diff <= leniency

    def judge(self, actual_time: float):
        judgment = self.judgment_window.judge(actual_time, self.target_time)
        error = self.judgment_window.good.clamp(actual_time - self.target_time)
        self.result.judgment = judgment
        self.result.accuracy = error
        if self.result.bucket.id != -1:
            self.result.bucket_value = error * WINDOW_SCALE
        self.despawn = True
        self.should_play_hit_effects = judgment != Judgment.MISS

    def judge_wrong_way(self, actual_time: float):
        judgment = self.judgment_window.judge(actual_time, self.target_time)
        if judgment == Judgment.PERFECT:
            judgment = Judgment.GREAT
        error = self.judgment_window.good.clamp(actual_time - self.target_time)
        self.result.judgment = judgment
        if error in self.judgment_window.perfect:
            self.result.accuracy = self.judgment_window.perfect.end
        else:
            self.result.accuracy = error
        if self.result.bucket.id != -1:
            self.result.bucket_value = error * WINDOW_SCALE
        self.despawn = True
        self.should_play_hit_effects = judgment != Judgment.MISS

    def complete(self):
        self.result.judgment = Judgment.PERFECT
        self.result.accuracy = 0
        if self.result.bucket.id != -1:
            self.result.bucket_value = 0
        self.despawn = True
        self.should_play_hit_effects = True

    def complete_wrong_way(self):
        self.result.judgment = Judgment.GREAT
        self.result.accuracy = self.judgment_window.good.end
        if self.result.bucket.id != -1:
            self.result.bucket_value = 0
        self.despawn = True
        self.should_play_hit_effects = True

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
        self.should_play_hit_effects = True

    def get_full_hitbox(self) -> Quad:
        leniency = get_leniency(self.kind)
        return layout_hitbox(self.lane - self.size - leniency, self.lane + self.size + leniency)

    @property
    def progress(self) -> float:
        if self.is_attached:
            attach_head = self.attach_head_ref.get()
            attach_tail = self.attach_tail_ref.get()
            head_progress = (
                progress_to(attach_head.target_scaled_time, group_scaled_time(attach_head.timescale_group))
                if time() < attach_head.target_time
                else 1.0
            )
            tail_progress = progress_to(attach_tail.target_scaled_time, group_scaled_time(attach_tail.timescale_group))
            head_frac = (
                0.0
                if time() < attach_head.target_time
                else unlerp_clamped(attach_head.target_time, attach_tail.target_time, time())
            )
            tail_frac = 1.0
            frac = unlerp_clamped(attach_head.target_time, attach_tail.target_time, self.target_time)
            return remap_clamped(head_frac, tail_frac, head_progress, tail_progress, frac)
        else:
            return progress_to(self.target_scaled_time, group_scaled_time(self.timescale_group))


@level_memory
class NoteMemory:
    active_tap_input_notes: VarArray[EntityRef[BaseNote], Dim[256]]
    active_release_input_notes: VarArray[EntityRef[BaseNote], Dim[256]]


NormalTapNote = BaseNote.derive(archetype_names.NORMAL_TAP_NOTE, is_scored=True, key=NoteKind.NORM_TAP)
CriticalTapNote = BaseNote.derive(archetype_names.CRITICAL_TAP_NOTE, is_scored=True, key=NoteKind.CRIT_TAP)
NormalFlickNote = BaseNote.derive(archetype_names.NORMAL_FLICK_NOTE, is_scored=True, key=NoteKind.NORM_FLICK)
CriticalFlickNote = BaseNote.derive(archetype_names.CRITICAL_FLICK_NOTE, is_scored=True, key=NoteKind.CRIT_FLICK)
NormalTraceNote = BaseNote.derive(archetype_names.NORMAL_TRACE_NOTE, is_scored=True, key=NoteKind.NORM_TRACE)
CriticalTraceNote = BaseNote.derive(archetype_names.CRITICAL_TRACE_NOTE, is_scored=True, key=NoteKind.CRIT_TRACE)
NormalTraceFlickNote = BaseNote.derive(
    archetype_names.NORMAL_TRACE_FLICK_NOTE, is_scored=True, key=NoteKind.NORM_TRACE_FLICK
)
CriticalTraceFlickNote = BaseNote.derive(
    archetype_names.CRITICAL_TRACE_FLICK_NOTE, is_scored=True, key=NoteKind.CRIT_TRACE_FLICK
)
NormalReleaseNote = BaseNote.derive(archetype_names.NORMAL_RELEASE_NOTE, is_scored=True, key=NoteKind.NORM_RELEASE)
CriticalReleaseNote = BaseNote.derive(archetype_names.CRITICAL_RELEASE_NOTE, is_scored=True, key=NoteKind.CRIT_RELEASE)
NormalHeadTapNote = BaseNote.derive(archetype_names.NORMAL_HEAD_TAP_NOTE, is_scored=True, key=NoteKind.NORM_HEAD_TAP)
CriticalHeadTapNote = BaseNote.derive(
    archetype_names.CRITICAL_HEAD_TAP_NOTE, is_scored=True, key=NoteKind.CRIT_HEAD_TAP
)
NormalHeadFlickNote = BaseNote.derive(
    archetype_names.NORMAL_HEAD_FLICK_NOTE, is_scored=True, key=NoteKind.NORM_HEAD_FLICK
)
CriticalHeadFlickNote = BaseNote.derive(
    archetype_names.CRITICAL_HEAD_FLICK_NOTE, is_scored=True, key=NoteKind.CRIT_HEAD_FLICK
)
NormalHeadTraceNote = BaseNote.derive(
    archetype_names.NORMAL_HEAD_TRACE_NOTE, is_scored=True, key=NoteKind.NORM_HEAD_TRACE
)
CriticalHeadTraceNote = BaseNote.derive(
    archetype_names.CRITICAL_HEAD_TRACE_NOTE, is_scored=True, key=NoteKind.CRIT_HEAD_TRACE
)
NormalHeadTraceFlickNote = BaseNote.derive(
    archetype_names.NORMAL_HEAD_TRACE_FLICK_NOTE, is_scored=True, key=NoteKind.NORM_HEAD_TRACE_FLICK
)
CriticalHeadTraceFlickNote = BaseNote.derive(
    archetype_names.CRITICAL_HEAD_TRACE_FLICK_NOTE, is_scored=True, key=NoteKind.CRIT_HEAD_TRACE_FLICK
)
NormalHeadReleaseNote = BaseNote.derive(
    archetype_names.NORMAL_HEAD_RELEASE_NOTE, is_scored=True, key=NoteKind.NORM_HEAD_RELEASE
)
CriticalHeadReleaseNote = BaseNote.derive(
    archetype_names.CRITICAL_HEAD_RELEASE_NOTE, is_scored=True, key=NoteKind.CRIT_HEAD_RELEASE
)
NormalTailTapNote = BaseNote.derive(archetype_names.NORMAL_TAIL_TAP_NOTE, is_scored=True, key=NoteKind.NORM_TAIL_TAP)
CriticalTailTapNote = BaseNote.derive(
    archetype_names.CRITICAL_TAIL_TAP_NOTE, is_scored=True, key=NoteKind.CRIT_TAIL_TAP
)
NormalTailFlickNote = BaseNote.derive(
    archetype_names.NORMAL_TAIL_FLICK_NOTE, is_scored=True, key=NoteKind.NORM_TAIL_FLICK
)
CriticalTailFlickNote = BaseNote.derive(
    archetype_names.CRITICAL_TAIL_FLICK_NOTE, is_scored=True, key=NoteKind.CRIT_TAIL_FLICK
)
NormalTailTraceNote = BaseNote.derive(
    archetype_names.NORMAL_TAIL_TRACE_NOTE, is_scored=True, key=NoteKind.NORM_TAIL_TRACE
)
CriticalTailTraceNote = BaseNote.derive(
    archetype_names.CRITICAL_TAIL_TRACE_NOTE, is_scored=True, key=NoteKind.CRIT_TAIL_TRACE
)
NormalTailTraceFlickNote = BaseNote.derive(
    archetype_names.NORMAL_TAIL_TRACE_FLICK_NOTE, is_scored=True, key=NoteKind.NORM_TAIL_TRACE_FLICK
)
CriticalTailTraceFlickNote = BaseNote.derive(
    archetype_names.CRITICAL_TAIL_TRACE_FLICK_NOTE, is_scored=True, key=NoteKind.CRIT_TAIL_TRACE_FLICK
)
NormalTailReleaseNote = BaseNote.derive(
    archetype_names.NORMAL_TAIL_RELEASE_NOTE, is_scored=True, key=NoteKind.NORM_TAIL_RELEASE
)
CriticalTailReleaseNote = BaseNote.derive(
    archetype_names.CRITICAL_TAIL_RELEASE_NOTE, is_scored=True, key=NoteKind.CRIT_TAIL_RELEASE
)
NormalTickNote = BaseNote.derive(archetype_names.NORMAL_TICK_NOTE, is_scored=True, key=NoteKind.NORM_TICK)
CriticalTickNote = BaseNote.derive(archetype_names.CRITICAL_TICK_NOTE, is_scored=True, key=NoteKind.CRIT_TICK)
DamageNote = BaseNote.derive(archetype_names.DAMAGE_NOTE, is_scored=True, key=NoteKind.DAMAGE)
AnchorNote = BaseNote.derive(archetype_names.ANCHOR_NOTE, is_scored=False, key=NoteKind.ANCHOR)
TransientHiddenTickNote = BaseNote.derive(
    archetype_names.TRANSIENT_HIDDEN_TICK_NOTE, is_scored=True, key=NoteKind.HIDE_TICK
)
FakeNormalTapNote = BaseNote.derive(archetype_names.FAKE_NORMAL_TAP_NOTE, is_scored=False, key=NoteKind.NORM_TAP)
FakeCriticalTapNote = BaseNote.derive(archetype_names.FAKE_CRITICAL_TAP_NOTE, is_scored=False, key=NoteKind.CRIT_TAP)
FakeNormalFlickNote = BaseNote.derive(archetype_names.FAKE_NORMAL_FLICK_NOTE, is_scored=False, key=NoteKind.NORM_FLICK)
FakeCriticalFlickNote = BaseNote.derive(
    archetype_names.FAKE_CRITICAL_FLICK_NOTE, is_scored=False, key=NoteKind.CRIT_FLICK
)
FakeNormalTraceNote = BaseNote.derive(archetype_names.FAKE_NORMAL_TRACE_NOTE, is_scored=False, key=NoteKind.NORM_TRACE)
FakeCriticalTraceNote = BaseNote.derive(
    archetype_names.FAKE_CRITICAL_TRACE_NOTE, is_scored=False, key=NoteKind.CRIT_TRACE
)
FakeNormalTraceFlickNote = BaseNote.derive(
    archetype_names.FAKE_NORMAL_TRACE_FLICK_NOTE, is_scored=False, key=NoteKind.NORM_TRACE_FLICK
)
FakeCriticalTraceFlickNote = BaseNote.derive(
    "FakeCriticalTraceFlickNote", is_scored=False, key=NoteKind.CRIT_TRACE_FLICK
)
FakeNormalReleaseNote = BaseNote.derive(
    archetype_names.FAKE_NORMAL_RELEASE_NOTE, is_scored=False, key=NoteKind.NORM_RELEASE
)
FakeCriticalReleaseNote = BaseNote.derive(
    archetype_names.FAKE_CRITICAL_RELEASE_NOTE, is_scored=False, key=NoteKind.CRIT_RELEASE
)
FakeNormalHeadTapNote = BaseNote.derive(
    archetype_names.FAKE_NORMAL_HEAD_TAP_NOTE, is_scored=False, key=NoteKind.NORM_HEAD_TAP
)
FakeCriticalHeadTapNote = BaseNote.derive(
    archetype_names.FAKE_CRITICAL_HEAD_TAP_NOTE, is_scored=False, key=NoteKind.CRIT_HEAD_TAP
)
FakeNormalHeadFlickNote = BaseNote.derive(
    archetype_names.FAKE_NORMAL_HEAD_FLICK_NOTE, is_scored=False, key=NoteKind.NORM_HEAD_FLICK
)
FakeCriticalHeadFlickNote = BaseNote.derive(
    archetype_names.FAKE_CRITICAL_HEAD_FLICK_NOTE, is_scored=False, key=NoteKind.CRIT_HEAD_FLICK
)
FakeNormalHeadTraceNote = BaseNote.derive(
    archetype_names.FAKE_NORMAL_HEAD_TRACE_NOTE, is_scored=False, key=NoteKind.NORM_HEAD_TRACE
)
FakeCriticalHeadTraceNote = BaseNote.derive(
    archetype_names.FAKE_CRITICAL_HEAD_TRACE_NOTE, is_scored=False, key=NoteKind.CRIT_HEAD_TRACE
)
FakeNormalHeadTraceFlickNote = BaseNote.derive(
    archetype_names.FAKE_NORMAL_HEAD_TRACE_FLICK_NOTE, is_scored=False, key=NoteKind.NORM_HEAD_TRACE_FLICK
)
FakeCriticalHeadTraceFlickNote = BaseNote.derive(
    archetype_names.FAKE_CRITICAL_HEAD_TRACE_FLICK_NOTE, is_scored=False, key=NoteKind.CRIT_HEAD_TRACE_FLICK
)
FakeNormalHeadReleaseNote = BaseNote.derive(
    archetype_names.FAKE_NORMAL_HEAD_RELEASE_NOTE, is_scored=False, key=NoteKind.NORM_HEAD_RELEASE
)
FakeCriticalHeadReleaseNote = BaseNote.derive(
    archetype_names.FAKE_CRITICAL_HEAD_RELEASE_NOTE, is_scored=False, key=NoteKind.CRIT_HEAD_RELEASE
)
FakeNormalTailTapNote = BaseNote.derive(
    archetype_names.FAKE_NORMAL_TAIL_TAP_NOTE, is_scored=False, key=NoteKind.NORM_TAIL_TAP
)
FakeCriticalTailTapNote = BaseNote.derive(
    archetype_names.FAKE_CRITICAL_TAIL_TAP_NOTE, is_scored=False, key=NoteKind.CRIT_TAIL_TAP
)
FakeNormalTailFlickNote = BaseNote.derive(
    archetype_names.FAKE_NORMAL_TAIL_FLICK_NOTE, is_scored=False, key=NoteKind.NORM_TAIL_FLICK
)
FakeCriticalTailFlickNote = BaseNote.derive(
    archetype_names.FAKE_CRITICAL_TAIL_FLICK_NOTE, is_scored=False, key=NoteKind.CRIT_TAIL_FLICK
)
FakeNormalTailTraceNote = BaseNote.derive(
    archetype_names.FAKE_NORMAL_TAIL_TRACE_NOTE, is_scored=False, key=NoteKind.NORM_TAIL_TRACE
)
FakeCriticalTailTraceNote = BaseNote.derive(
    archetype_names.FAKE_CRITICAL_TAIL_TRACE_NOTE, is_scored=False, key=NoteKind.CRIT_TAIL_TRACE
)
FakeNormalTailTraceFlickNote = BaseNote.derive(
    archetype_names.FAKE_NORMAL_TAIL_TRACE_FLICK_NOTE, is_scored=False, key=NoteKind.NORM_TAIL_TRACE_FLICK
)
FakeCriticalTailTraceFlickNote = BaseNote.derive(
    archetype_names.FAKE_CRITICAL_TAIL_TRACE_FLICK_NOTE, is_scored=False, key=NoteKind.CRIT_TAIL_TRACE_FLICK
)
FakeNormalTailReleaseNote = BaseNote.derive(
    archetype_names.FAKE_NORMAL_TAIL_RELEASE_NOTE, is_scored=False, key=NoteKind.NORM_TAIL_RELEASE
)
FakeCriticalTailReleaseNote = BaseNote.derive(
    archetype_names.FAKE_CRITICAL_TAIL_RELEASE_NOTE, is_scored=False, key=NoteKind.CRIT_TAIL_RELEASE
)
FakeNormalTickNote = BaseNote.derive(archetype_names.FAKE_NORMAL_TICK_NOTE, is_scored=False, key=NoteKind.NORM_TICK)
FakeCriticalTickNote = BaseNote.derive(archetype_names.FAKE_CRITICAL_TICK_NOTE, is_scored=False, key=NoteKind.CRIT_TICK)
FakeDamageNote = BaseNote.derive(archetype_names.FAKE_DAMAGE_NOTE, is_scored=False, key=NoteKind.DAMAGE)
FakeAnchorNote = BaseNote.derive(archetype_names.FAKE_ANCHOR_NOTE, is_scored=False, key=NoteKind.ANCHOR)
FakeTransientHiddenTickNote = BaseNote.derive(
    archetype_names.FAKE_TRANSIENT_HIDDEN_TICK_NOTE, is_scored=False, key=NoteKind.HIDE_TICK
)


NOTE_ARCHETYPES = (
    NormalTapNote,
    CriticalTapNote,
    NormalFlickNote,
    CriticalFlickNote,
    NormalTraceNote,
    CriticalTraceNote,
    NormalTraceFlickNote,
    CriticalTraceFlickNote,
    NormalReleaseNote,
    CriticalReleaseNote,
    NormalHeadTapNote,
    CriticalHeadTapNote,
    NormalHeadFlickNote,
    CriticalHeadFlickNote,
    NormalHeadTraceNote,
    CriticalHeadTraceNote,
    NormalHeadTraceFlickNote,
    CriticalHeadTraceFlickNote,
    NormalHeadReleaseNote,
    CriticalHeadReleaseNote,
    NormalTailTapNote,
    CriticalTailTapNote,
    NormalTailFlickNote,
    CriticalTailFlickNote,
    NormalTailTraceNote,
    CriticalTailTraceNote,
    NormalTailTraceFlickNote,
    CriticalTailTraceFlickNote,
    NormalTailReleaseNote,
    CriticalTailReleaseNote,
    NormalTickNote,
    CriticalTickNote,
    DamageNote,
    AnchorNote,
    TransientHiddenTickNote,
    FakeNormalTapNote,
    FakeCriticalTapNote,
    FakeNormalFlickNote,
    FakeCriticalFlickNote,
    FakeNormalTraceNote,
    FakeCriticalTraceNote,
    FakeNormalTraceFlickNote,
    FakeCriticalTraceFlickNote,
    FakeNormalReleaseNote,
    FakeCriticalReleaseNote,
    FakeNormalHeadTapNote,
    FakeCriticalHeadTapNote,
    FakeNormalHeadFlickNote,
    FakeCriticalHeadFlickNote,
    FakeNormalHeadTraceNote,
    FakeCriticalHeadTraceNote,
    FakeNormalHeadTraceFlickNote,
    FakeCriticalHeadTraceFlickNote,
    FakeNormalHeadReleaseNote,
    FakeCriticalHeadReleaseNote,
    FakeNormalTailTapNote,
    FakeCriticalTailTapNote,
    FakeNormalTailFlickNote,
    FakeCriticalTailFlickNote,
    FakeNormalTailTraceNote,
    FakeCriticalTailTraceNote,
    FakeNormalTailTraceFlickNote,
    FakeCriticalTailTraceFlickNote,
    FakeNormalTailReleaseNote,
    FakeCriticalTailReleaseNote,
    FakeNormalTickNote,
    FakeCriticalTickNote,
    FakeDamageNote,
    FakeAnchorNote,
    FakeTransientHiddenTickNote,
)


def derive_note_archetypes[T: type[AnyArchetype]](base: T) -> tuple[T, ...]:
    """Helper function to derive all note archetypes from a given base archetype for used in watch and preview."""
    return tuple(base.derive(str(a.name), is_scored=a.is_scored, key=a.key) for a in NOTE_ARCHETYPES)
