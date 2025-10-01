from __future__ import annotations

from typing import cast

from sonolus.script.archetype import (
    EntityRef,
    StandardImport,
    WatchArchetype,
    entity_data,
    imported,
    shared_memory,
)
from sonolus.script.bucket import Judgment
from sonolus.script.interval import remap_clamped, unlerp_clamped
from sonolus.script.runtime import is_replay, is_skip, time
from sonolus.script.timing import beat_to_time

from sekai.lib.connector import ActiveConnectorInfo, ConnectorKind
from sekai.lib.ease import EaseType
from sekai.lib.layout import FlickDirection, progress_to
from sekai.lib.note import (
    NoteKind,
    draw_note,
    get_attach_params,
    get_note_bucket,
    get_visual_spawn_time,
    is_head,
    map_flick_direction,
    map_note_kind,
    mirror_flick_direction,
    play_note_hit_effects,
    schedule_note_auto_sfx,
    schedule_note_sfx,
    schedule_note_slot_effects,
)
from sekai.lib.options import Options
from sekai.lib.timescale import group_hide_notes, group_scaled_time, group_time_to_scaled_time
from sekai.play.note import derive_note_archetypes


class WatchBaseNote(WatchArchetype):
    beat: StandardImport.BEAT
    timescale_group: StandardImport.TIMESCALE_GROUP
    lane: float = imported()
    size: float = imported()
    direction: FlickDirection = imported()
    active_head_ref: EntityRef[WatchBaseNote] = imported(name="activeHead")
    is_attached: bool = imported(name="isAttached")
    connector_ease: EaseType = imported(name="connectorEase")
    segment_kind: ConnectorKind = imported(name="segmentKind")
    segment_alpha: float = imported(name="segmentAlpha")
    attach_head_ref: EntityRef[WatchBaseNote] = imported(name="attachHead")
    attach_tail_ref: EntityRef[WatchBaseNote] = imported(name="attachTail")

    kind: NoteKind = entity_data()
    data_init_done: bool = entity_data()
    target_time: float = entity_data()
    visual_start_time: float = entity_data()
    start_time: float = entity_data()
    target_scaled_time: float = entity_data()

    active_connector_info: ActiveConnectorInfo = shared_memory()

    end_time: float = imported()
    played_hit_effects: bool = imported()

    judgment: StandardImport.JUDGMENT = imported()
    accuracy: StandardImport.ACCURACY = imported()

    def init_data(self):
        if self.data_init_done:
            return

        self.kind = map_note_kind(cast(NoteKind, self.key))

        self.data_init_done = True

        self.direction = map_flick_direction(self.direction, self.index)

        if Options.mirror:
            self.lane *= -1
            self.direction = mirror_flick_direction(self.direction)

        self.target_time = beat_to_time(self.beat)

        if not self.is_attached:
            self.target_scaled_time = group_time_to_scaled_time(self.timescale_group, self.target_time)
            self.visual_start_time = get_visual_spawn_time(self.timescale_group, self.target_scaled_time)
            self.start_time = self.visual_start_time

    def preprocess(self):
        self.init_data()

        self.result.bucket = get_note_bucket(self.kind)

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
            self.start_time = self.visual_start_time

        if is_replay():
            if self.played_hit_effects:
                if Options.auto_sfx:
                    schedule_note_auto_sfx(self.kind, self.target_time)
                else:
                    schedule_note_sfx(self.kind, self.judgment, self.end_time)
                schedule_note_slot_effects(self.kind, self.lane, self.size, self.end_time)
            self.result.bucket_value = self.accuracy * 1000
        else:
            self.judgment = Judgment.PERFECT
            if self.is_scored:
                schedule_note_sfx(self.kind, Judgment.PERFECT, self.target_time)
                schedule_note_slot_effects(self.kind, self.lane, self.size, self.target_time)

        self.result.target_time = self.target_time

    def spawn_time(self) -> float:
        if self.kind == NoteKind.ANCHOR:
            return 1e8
        return self.start_time

    def despawn_time(self) -> float:
        if is_replay():
            return self.end_time
        else:
            return self.target_time

    def update_parallel(self):
        if time() < self.visual_start_time:
            return
        if is_head(self.kind) and time() > self.target_time:
            return
        if group_hide_notes(self.timescale_group):
            return
        draw_note(self.kind, self.lane, self.size, self.progress, self.direction, self.target_time)

    def terminate(self):
        if is_skip():
            return
        if time() < self.target_time:
            return
        if (not is_replay() or self.played_hit_effects) and self.is_scored:
            play_note_hit_effects(self.kind, self.lane, self.size, self.direction, self.judgment)

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


WATCH_NOTE_ARCHETYPES = derive_note_archetypes(WatchBaseNote)
