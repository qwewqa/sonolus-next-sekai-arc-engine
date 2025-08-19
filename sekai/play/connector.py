from __future__ import annotations

from typing import cast

from sonolus.script.archetype import EntityRef, PlayArchetype, callback, entity_data, entity_memory, imported
from sonolus.script.effect import LoopedEffectHandle
from sonolus.script.interval import Interval, remap, unlerp_clamped
from sonolus.script.particle import ParticleHandle
from sonolus.script.runtime import input_offset, is_preprocessing, offset_adjusted_time, time, touches
from sonolus.script.timing import beat_to_time

from sekai.lib.connector import (
    ActiveConnectorInfo,
    GuideColor,
    GuideFadeType,
    SlideConnectorKind,
    SlideVisualState,
    destroy_looped_particle,
    destroy_looped_sfx,
    draw_connector,
    draw_guide,
    get_attached_params,
    update_circular_connector_particle,
    update_connector_sfx,
    update_linear_connector_particle,
)
from sekai.lib.ease import EaseType
from sekai.lib.layout import preempt_time, progress_to
from sekai.lib.note import draw_slide_note_head
from sekai.lib.options import Options
from sekai.lib.timescale import group_scaled_time, group_scaled_time_to_first_time, group_time_to_scaled_time
from sekai.play import note
from sekai.play.timescale import TimescaleGroup

CONNECTOR_LENIENCY = 1
START_LENIENCY_BEATS = 0.5


class BaseSlideConnector(PlayArchetype):
    start_ref: EntityRef[note.BaseNote] = imported(name="start")
    head_ref: EntityRef[note.BaseNote] = imported(name="head")
    tail_ref: EntityRef[note.BaseNote] = imported(name="tail")
    end_ref: EntityRef[note.BaseNote] = imported(name="end")
    ease: EaseType = imported(name="ease")

    spawn_time: float = entity_data()
    end_time: float = entity_data()
    visual_active_interval: Interval = entity_data()
    input_active_interval: Interval = entity_data()

    @callback(order=1)  # After note preprocessing is done
    def preprocess(self):
        self.visual_active_interval.start = min(self.head.target_time, self.tail.target_time)
        self.visual_active_interval.end = max(self.head.target_time, self.tail.target_time)
        self.input_active_interval = self.visual_active_interval + input_offset()
        self.spawn_time = min(
            self.visual_active_interval.start,
            self.input_active_interval.start,
            self.head.spawn_time,
            self.tail.spawn_time,
        )
        self.end_time = max(self.visual_active_interval.end, self.input_active_interval.end)

    def initialize(self):
        if self.head_ref.index == self.start.index:
            # This is the first connector, so it's in charge of spawning the SlideManager.
            SlideManager.spawn(start_ref=self.start_ref, end_ref=self.end_ref)

    def spawn_order(self) -> float:
        return self.spawn_time

    def should_spawn(self) -> bool:
        return time() >= self.spawn_time

    @callback(order=-1)
    def update_sequential(self):
        if time() >= self.end_time:
            self.despawn = True
            return

        if time() in self.input_active_interval:
            input_lane, input_size = self.get_attached_params(offset_adjusted_time())
            self.active_connector_info.input_lane = input_lane
            self.active_connector_info.input_size = input_size
            hitbox = self.active_connector_info.get_hitbox(CONNECTOR_LENIENCY)
            for touch in touches():
                if hitbox.contains_point(touch.position):
                    self.active_connector_info.is_active = True
                    break
            else:
                self.active_connector_info.is_active = False
        if time() in self.visual_active_interval:
            visual_lane, visual_size = self.get_attached_params(time())
            self.active_connector_info.visual_lane = visual_lane
            self.active_connector_info.visual_size = visual_size
            self.active_connector_info.connector_kind = self.kind
        if time() < self.visual_active_interval.end:
            if time() < self.start.target_time:
                visual_state = SlideVisualState.WAITING
            elif (
                offset_adjusted_time() < beat_to_time(self.start.beat + START_LENIENCY_BEATS)
                or self.active_connector_info.is_active
            ):
                visual_state = SlideVisualState.ACTIVE
            else:
                visual_state = SlideVisualState.INACTIVE
            draw_connector(
                kind=self.kind,
                visual_state=visual_state,
                ease_type=self.ease,
                quality=Options.slide_quality,
                lane_a=self.head.lane,
                size_a=self.head.size,
                progress_a=self.head.progress,
                target_time_a=self.head.target_time,
                lane_b=self.tail.lane,
                size_b=self.tail.size,
                progress_b=self.tail.progress,
                target_time_b=self.tail.target_time,
            )

    def get_attached_params(self, target_time: float) -> tuple[float, float]:
        if is_preprocessing():
            self.head.init_data()
            self.tail.init_data()
        return get_attached_params(
            ease_type=self.ease,
            lane_a=self.head.lane,
            size_a=self.head.size,
            progress_a=progress_to(
                self.head.target_scaled_time, group_time_to_scaled_time(self.head.timescale_group_ref, target_time)
            ),
            lane_b=self.tail.lane,
            size_b=self.tail.size,
            progress_b=progress_to(
                self.tail.target_scaled_time, group_time_to_scaled_time(self.tail.timescale_group_ref, target_time)
            ),
        )

    def get_attached_progress(self, target_time: float) -> float:
        head_progress = progress_to(self.head.target_scaled_time, group_scaled_time(self.head.timescale_group_ref))
        tail_progress = progress_to(self.tail.target_scaled_time, group_scaled_time(self.tail.timescale_group_ref))
        if abs(self.head.target_time - self.tail.target_time) < 1e-6:
            return (head_progress + tail_progress) / 2
        else:
            return remap(self.head.target_time, self.tail.target_time, head_progress, tail_progress, target_time)

    @property
    def kind(self) -> SlideConnectorKind:
        return cast(SlideConnectorKind, self.key)

    @property
    def start(self) -> note.BaseNote:
        return self.start_ref.get()

    @property
    def head(self) -> note.BaseNote:
        return self.head_ref.get()

    @property
    def tail(self) -> note.BaseNote:
        return self.tail_ref.get()

    @property
    def end(self) -> note.BaseNote:
        return self.end_ref.get()

    @property
    def active_connector_info(self) -> ActiveConnectorInfo:
        return self.start.active_connector_info


class Guide(PlayArchetype):
    name = "Guide"

    start_lane: float = imported(name="startLane")
    start_size: float = imported(name="startSize")
    start_beat: float = imported(name="startBeat")
    start_timescale_group: EntityRef[TimescaleGroup] = imported(name="startTimeScaleGroup")

    head_lane: float = imported(name="headLane")
    head_size: float = imported(name="headSize")
    head_beat: float = imported(name="headBeat")
    head_timescale_group: EntityRef[TimescaleGroup] = imported(name="headTimeScaleGroup")

    tail_lane: float = imported(name="tailLane")
    tail_size: float = imported(name="tailSize")
    tail_beat: float = imported(name="tailBeat")
    tail_timescale_group: EntityRef[TimescaleGroup] = imported(name="tailTimeScaleGroup")

    end_lane: float = imported(name="endLane")
    end_size: float = imported(name="endSize")
    end_beat: float = imported(name="endBeat")
    end_timescale_group: EntityRef[TimescaleGroup] = imported(name="endTimeScaleGroup")

    ease: EaseType = imported(name="ease")
    fade: GuideFadeType = imported(name="fade")
    color: GuideColor = imported(name="color")

    start_time: float = entity_data()
    start_scaled_time: float = entity_data()

    head_time: float = entity_data()
    head_scaled_time: float = entity_data()

    tail_time: float = entity_data()
    tail_scaled_time: float = entity_data()

    end_time: float = entity_data()
    end_scaled_time: float = entity_data()

    spawn_time: float = entity_data()

    def preprocess(self):
        self.start_time = beat_to_time(self.start_beat)
        self.start_scaled_time = group_time_to_scaled_time(self.start_timescale_group, self.start_time)

        self.head_time = beat_to_time(self.head_beat)
        self.head_scaled_time = group_time_to_scaled_time(self.head_timescale_group, self.head_time)

        self.tail_time = beat_to_time(self.tail_beat)
        self.tail_scaled_time = group_time_to_scaled_time(self.tail_timescale_group, self.tail_time)

        self.end_time = beat_to_time(self.end_beat)
        self.end_scaled_time = group_time_to_scaled_time(self.end_timescale_group, self.end_time)

        self.spawn_time = min(
            group_scaled_time_to_first_time(self.head_timescale_group, self.head_scaled_time - preempt_time()),
            group_scaled_time_to_first_time(self.tail_timescale_group, self.tail_scaled_time - preempt_time()),
        )

    def spawn_order(self) -> float:
        return self.spawn_time

    def should_spawn(self) -> bool:
        return time() >= self.spawn_time

    def update_parallel(self):
        if time() >= self.tail_time:
            self.despawn = True
            return

        draw_guide(
            color=self.color,
            fade_type=self.fade,
            ease_type=self.ease,
            quality=Options.guide_quality,
            lane_a=self.head_lane,
            size_a=self.head_size,
            progress_a=progress_to(self.head_scaled_time, group_scaled_time(self.head_timescale_group)),
            overall_progress_a=unlerp_clamped(self.start_scaled_time, self.end_scaled_time, self.head_scaled_time),
            target_time_a=self.head_time,
            lane_b=self.tail_lane,
            size_b=self.tail_size,
            progress_b=progress_to(self.tail_scaled_time, group_scaled_time(self.tail_timescale_group)),
            overall_progress_b=unlerp_clamped(self.start_scaled_time, self.end_scaled_time, self.tail_scaled_time),
            target_time_b=self.tail_time,
        )


NormalSlideConnector = BaseSlideConnector.derive("NormalSlideConnector", is_scored=False, key=SlideConnectorKind.NORMAL)
CriticalSlideConnector = BaseSlideConnector.derive(
    "CriticalSlideConnector", is_scored=False, key=SlideConnectorKind.CRITICAL
)


class SlideManager(PlayArchetype):
    name = "SlideManager"

    start_ref: EntityRef[note.BaseNote] = entity_memory()
    end_ref: EntityRef[note.BaseNote] = entity_memory()

    last_kind: SlideConnectorKind = entity_memory()
    circular_particle: ParticleHandle = entity_memory()
    linear_particle: ParticleHandle = entity_memory()
    sfx: LoopedEffectHandle = entity_memory()

    def update_parallel(self):
        if time() >= self.end.target_time:
            destroy_looped_particle(self.circular_particle)
            destroy_looped_particle(self.linear_particle)
            destroy_looped_sfx(self.sfx)
            self.despawn = True
            return
        if time() < self.start.target_time:
            return
        info = self.start.active_connector_info
        draw_slide_note_head(
            self.start.kind,
            info.visual_lane,
            info.visual_size,
        )
        if info.is_active:
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

    @property
    def start(self) -> note.BaseNote:
        return self.start_ref.get()

    @property
    def end(self) -> note.BaseNote:
        return self.end_ref.get()


CONNECTOR_ARCHETYPES = (
    NormalSlideConnector,
    CriticalSlideConnector,
    Guide,
    SlideManager,
)
