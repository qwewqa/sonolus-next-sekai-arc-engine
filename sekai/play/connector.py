from __future__ import annotations

from typing import assert_never

from sonolus.script.archetype import EntityRef, PlayArchetype, callback, entity_data, entity_memory, imported
from sonolus.script.effect import LoopedEffectHandle
from sonolus.script.interval import Interval
from sonolus.script.particle import ParticleHandle
from sonolus.script.runtime import input_offset, offset_adjusted_time, time, touches
from sonolus.script.timing import beat_to_time

from sekai.lib import archetype_names
from sekai.lib.connector import (
    CONNECTOR_SLOT_SPAWN_PERIOD,
    CONNECTOR_TRAIL_SPAWN_PERIOD,
    ActiveConnectorInfo,
    ConnectorKind,
    ConnectorVisualState,
    destroy_looped_particle,
    destroy_looped_sfx,
    draw_connector,
    draw_connector_slot_glow_effect,
    schedule_connector_sfx,
    spawn_connector_slot_particles,
    spawn_linear_connector_trail_particle,
    update_circular_connector_particle,
    update_connector_sfx,
    update_linear_connector_particle,
)
from sekai.lib.ease import EaseType
from sekai.lib.note import draw_slide_note_head, get_attach_params
from sekai.lib.options import Options
from sekai.lib.streams import Streams
from sekai.lib.timescale import group_hide_notes
from sekai.play import note

CONNECTOR_LENIENCY = 1
START_LENIENCY_BEATS = 0.5


class Connector(PlayArchetype):
    name = archetype_names.CONNECTOR

    head_ref: EntityRef[note.BaseNote] = imported(name="head")
    tail_ref: EntityRef[note.BaseNote] = imported(name="tail")
    segment_head_ref: EntityRef[note.BaseNote] = imported(name="segmentHead")
    segment_tail_ref: EntityRef[note.BaseNote] = imported(name="segmentTail")
    active_head_ref: EntityRef[note.BaseNote] = imported(name="activeHead")
    active_tail_ref: EntityRef[note.BaseNote] = imported(name="activeTail")

    kind: ConnectorKind = entity_data()
    ease_type: EaseType = entity_data()
    start_time: float = entity_data()
    end_time: float = entity_data()
    visual_active_interval: Interval = entity_data()
    input_active_interval: Interval = entity_data()

    last_visual_state: ConnectorVisualState = entity_memory()

    @callback(order=1)  # After note preprocessing is done
    def preprocess(self):
        head = self.head
        tail = self.tail
        self.kind = self.segment_head.segment_kind
        self.ease_type = head.connector_ease
        self.visual_active_interval.start = min(head.target_time, tail.target_time)
        self.visual_active_interval.end = max(head.target_time, tail.target_time)
        self.input_active_interval = self.visual_active_interval + input_offset()
        self.start_time = min(
            self.visual_active_interval.start,
            self.input_active_interval.start,
            head.start_time,
            tail.start_time,
        )
        self.end_time = max(self.visual_active_interval.end, self.input_active_interval.end)
        self.last_visual_state = ConnectorVisualState.WAITING

        if Options.auto_sfx and self.head_ref.index == self.segment_head_ref.index:
            match self.kind:
                case (
                    ConnectorKind.ACTIVE_NORMAL
                    | ConnectorKind.ACTIVE_CRITICAL
                    | ConnectorKind.ACTIVE_FAKE_NORMAL
                    | ConnectorKind.ACTIVE_FAKE_CRITICAL
                ):
                    schedule_connector_sfx(
                        self.kind,
                        self.segment_head.timescale_group,
                        self.segment_head.target_time,
                        self.segment_tail.target_time,
                    )
                case (
                    ConnectorKind.NONE
                    | ConnectorKind.GUIDE_NEUTRAL
                    | ConnectorKind.GUIDE_RED
                    | ConnectorKind.GUIDE_GREEN
                    | ConnectorKind.GUIDE_BLUE
                    | ConnectorKind.GUIDE_YELLOW
                    | ConnectorKind.GUIDE_PURPLE
                    | ConnectorKind.GUIDE_CYAN
                    | ConnectorKind.GUIDE_BLACK
                ):
                    pass
                case _:
                    assert_never(self.kind)

    def initialize(self):
        if self.head_ref.index == self.active_head_ref.index:
            # This is the first connector, so it's in charge of spawning the SlideManager.
            SlideManager.spawn(active_head_ref=self.active_head_ref, active_tail_ref=self.active_tail_ref)
        Streams.connector_visual_states[self.index][-2] = ConnectorVisualState.WAITING

    def spawn_order(self) -> float:
        return self.start_time

    def should_spawn(self) -> bool:
        return time() >= self.start_time

    @callback(order=-1)
    def update_sequential(self):
        if time() >= self.end_time:
            self.despawn = True
            return

        if self.active_head_ref.index > 0:
            if time() in self.input_active_interval:
                input_lane, input_size = self.get_attached_params(offset_adjusted_time())
                self.active_connector_info.prev_input_lane = self.active_connector_info.input_lane
                self.active_connector_info.prev_input_size = self.active_connector_info.input_size
                self.active_connector_info.input_lane = input_lane
                self.active_connector_info.input_size = input_size
                hitbox = self.active_connector_info.get_hitbox(CONNECTOR_LENIENCY)
                for touch in touches():
                    if not touch.ended and hitbox.contains_point(touch.position):
                        if not self.active_connector_info.is_active:
                            self.active_connector_info.active_start_time = time()
                        self.active_connector_info.is_active = True
                        break
                else:
                    self.active_connector_info.is_active = False
            if time() in self.visual_active_interval:
                visual_lane, visual_size = self.get_attached_params(time())
                self.active_connector_info.visual_lane = visual_lane
                self.active_connector_info.visual_size = visual_size
                self.active_connector_info.connector_kind = self.kind
            if group_hide_notes(self.segment_head.timescale_group):
                self.active_connector_info.connector_kind = ConnectorKind.NONE

    def update_parallel(self):
        if time() < self.visual_active_interval.end:
            head = self.head
            tail = self.tail
            segment_head = self.segment_head
            segment_tail = self.segment_tail
            if self.active_head_ref.index > 0:
                active_head = self.active_head
                if time() < active_head.target_time:
                    visual_state = ConnectorVisualState.WAITING
                elif (
                    offset_adjusted_time() < beat_to_time(active_head.beat + START_LENIENCY_BEATS)
                    or self.active_connector_info.is_active
                ):
                    visual_state = ConnectorVisualState.ACTIVE
                else:
                    visual_state = ConnectorVisualState.INACTIVE
            else:
                visual_state = ConnectorVisualState.WAITING
            if visual_state != self.last_visual_state:
                self.last_visual_state = visual_state
                Streams.connector_visual_states[self.index][offset_adjusted_time()] = visual_state
            if group_hide_notes(segment_head.timescale_group):
                return
            draw_connector(
                kind=self.kind,
                visual_state=visual_state,
                ease_type=self.ease_type,
                head_lane=head.lane,
                head_size=head.size,
                head_progress=head.progress,
                head_target_time=head.target_time,
                head_is_segment_head=abs(head.progress - segment_head.progress) < 1e-3,
                tail_lane=tail.lane,
                tail_size=tail.size,
                tail_progress=tail.progress,
                tail_target_time=tail.target_time,
                tail_is_segment_tail=abs(tail.progress - segment_tail.progress) < 1e-3,
                segment_head_target_time=segment_head.target_time,
                segment_head_lane=segment_head.lane,
                segment_head_alpha=segment_head.segment_alpha,
                segment_tail_target_time=segment_tail.target_time,
                segment_tail_alpha=segment_tail.segment_alpha,
            )

    def get_attached_params(self, target_time: float) -> tuple[float, float]:
        head = self.head_ref.get()
        tail = self.tail_ref.get()
        return get_attach_params(
            ease_type=self.ease_type,
            head_lane=head.lane,
            head_size=head.size,
            head_target_time=head.target_time,
            tail_lane=tail.lane,
            tail_size=tail.size,
            tail_target_time=tail.target_time,
            target_time=target_time,
        )

    @property
    def head(self):
        return self.head_ref.get()

    @property
    def tail(self):
        return self.tail_ref.get()

    @property
    def segment_head(self):
        return self.segment_head_ref.get()

    @property
    def segment_tail(self):
        return self.segment_tail_ref.get()

    @property
    def active_head(self):
        return self.active_head_ref.get()

    @property
    def active_tail(self):
        return self.active_tail_ref.get()

    @property
    def active_connector_info(self) -> ActiveConnectorInfo:
        return self.active_head_ref.get().active_connector_info


class SlideManager(PlayArchetype):
    name = archetype_names.SLIDE_MANAGER

    active_head_ref: EntityRef[note.BaseNote] = entity_memory()
    active_tail_ref: EntityRef[note.BaseNote] = entity_memory()

    last_kind: ConnectorKind = entity_memory()
    circular_particle: ParticleHandle = entity_memory()
    linear_particle: ParticleHandle = entity_memory()
    sfx: LoopedEffectHandle = entity_memory()
    next_trail_spawn_time: float = entity_memory()
    next_slot_spawn_time: float = entity_memory()
    last_effect_kind: ConnectorKind = entity_memory()

    def initialize(self):
        self.next_trail_spawn_time = -1e8
        self.next_slot_spawn_time = -1e8
        Streams.connector_effect_kinds[self.active_head.index][-2] = ConnectorKind.NONE
        self.last_effect_kind = ConnectorKind.NONE

    def update_parallel(self):
        connector_effect_kind_stream = Streams.connector_effect_kinds[self.active_head.index]
        if time() >= self.active_tail.target_time:
            destroy_looped_particle(self.circular_particle)
            destroy_looped_particle(self.linear_particle)
            destroy_looped_sfx(self.sfx)
            connector_effect_kind_stream[offset_adjusted_time()] = ConnectorKind.NONE
            self.last_effect_kind = ConnectorKind.NONE
            self.despawn = True
            return
        if time() < self.active_head.target_time:
            return
        info = self.active_head.active_connector_info
        match info.connector_kind:
            case (
                ConnectorKind.ACTIVE_NORMAL
                | ConnectorKind.ACTIVE_CRITICAL
                | ConnectorKind.ACTIVE_FAKE_NORMAL
                | ConnectorKind.ACTIVE_FAKE_CRITICAL
            ) if info.is_active:
                replace = info.connector_kind != self.last_kind
                self.last_kind = info.connector_kind
                update_circular_connector_particle(
                    self.circular_particle,
                    info.connector_kind,
                    info.visual_lane,
                    replace,
                )
                update_linear_connector_particle(
                    self.linear_particle,
                    info.connector_kind,
                    info.visual_lane,
                    replace,
                )
                update_connector_sfx(self.sfx, info.connector_kind, replace)
                if self.last_effect_kind != info.connector_kind:
                    connector_effect_kind_stream[offset_adjusted_time()] = info.connector_kind
                    self.last_effect_kind = info.connector_kind
                if time() >= self.next_trail_spawn_time:
                    self.next_trail_spawn_time = max(
                        self.next_trail_spawn_time + CONNECTOR_TRAIL_SPAWN_PERIOD,
                        time() + CONNECTOR_TRAIL_SPAWN_PERIOD / 2,
                    )
                    spawn_linear_connector_trail_particle(info.connector_kind, info.visual_lane)
                if time() >= self.next_slot_spawn_time:
                    self.next_slot_spawn_time = max(
                        self.next_slot_spawn_time + CONNECTOR_SLOT_SPAWN_PERIOD,
                        time() + CONNECTOR_SLOT_SPAWN_PERIOD / 2,
                    )
                    spawn_connector_slot_particles(info.connector_kind, info.visual_lane, info.visual_size)
                draw_connector_slot_glow_effect(
                    info.connector_kind, info.active_start_time, info.visual_lane, info.visual_size
                )
            case _:
                destroy_looped_sfx(self.sfx)
                destroy_looped_particle(self.circular_particle)
                destroy_looped_particle(self.linear_particle)
                if self.last_effect_kind != ConnectorKind.NONE:
                    connector_effect_kind_stream[offset_adjusted_time()] = ConnectorKind.NONE
                    self.last_effect_kind = ConnectorKind.NONE
        match info.connector_kind:
            case (
                ConnectorKind.ACTIVE_NORMAL
                | ConnectorKind.ACTIVE_CRITICAL
                | ConnectorKind.ACTIVE_FAKE_NORMAL
                | ConnectorKind.ACTIVE_FAKE_CRITICAL
            ):
                draw_slide_note_head(
                    self.active_head.kind,
                    info.visual_lane,
                    info.visual_size,
                    self.active_head.target_time,
                )
            case _:
                pass

    @property
    def active_head(self) -> note.BaseNote:
        return self.active_head_ref.get()

    @property
    def active_tail(self) -> note.BaseNote:
        return self.active_tail_ref.get()


CONNECTOR_ARCHETYPES = (
    Connector,
    SlideManager,
)
