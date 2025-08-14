from __future__ import annotations

from typing import cast

from sonolus.script.archetype import EntityRef, PlayArchetype, callback, entity_data, imported
from sonolus.script.interval import unlerp_clamped
from sonolus.script.runtime import time
from sonolus.script.timing import beat_to_time

from sekai.lib.connector import (
    GuideColor,
    GuideFadeType,
    SlideConnectorKind,
    SlideVisualState,
    draw_connector,
    draw_guide,
    get_attached,
)
from sekai.lib.ease import EaseType
from sekai.lib.layout import preempt_time, progress_to
from sekai.lib.options import Options
from sekai.lib.timescale import group_scaled_time, group_scaled_time_to_first_time, group_time_to_scaled_time
from sekai.play import note
from sekai.play.timescale import TimescaleGroup


class BaseSlideConnector(PlayArchetype):
    start_ref: EntityRef[note.BaseNote] = imported(name="start")
    head_ref: EntityRef[note.BaseNote] = imported(name="head")
    tail_ref: EntityRef[note.BaseNote] = imported(name="tail")
    end_ref: EntityRef[note.BaseNote] = imported(name="end")
    ease: EaseType = imported(name="ease")
    start_type: SlideConnectorKind = imported(name="startType")

    spawn_time: float = entity_data()

    @callback(order=1)  # After note preprocessing is done
    def preprocess(self):
        self.spawn_time = min(self.head.spawn_time, self.tail.spawn_time)

    def spawn_order(self) -> float:
        return self.spawn_time

    def should_spawn(self) -> bool:
        return time() >= self.spawn_time

    def update_parallel(self):
        # TODO: despawn time accounting for offset rather than doing it here
        if time() >= self.tail.target_time:
            self.despawn = True
            return

        draw_connector(
            kind=self.kind,
            visual_state=SlideVisualState.WAITING,
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

    def get_attached(self, target_time: float) -> tuple[float, float]:
        self.head.init_data()
        self.tail.init_data()
        return get_attached(
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

ALL_CONNECTOR_ARCHETYPES = (
    NormalSlideConnector,
    CriticalSlideConnector,
    Guide,
)
