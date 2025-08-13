from __future__ import annotations

from collections.abc import Iterator
from typing import Protocol, cast

from sonolus.script.archetype import EntityRef, get_archetype_by_name
from sonolus.script.interval import remap
from sonolus.script.record import Record
from sonolus.script.timing import beat_to_time

TIMESCALE_CHANGE_NAME = "TimeScaleChange"
TIMESCALE_GROUP_NAME = "TimeScaleGroup"


class TimescaleChangeLike(Protocol):
    beat: float
    timescale: float
    next: EntityRef

    @classmethod
    def at(cls, index: int) -> TimescaleChangeLike: ...

    @property
    def index(self) -> int: ...


class TimescaleGroupLike(Protocol):
    first: EntityRef
    current_scaled_time: float

    @classmethod
    def at(cls, index: int) -> TimescaleGroupLike: ...


class CachedTimescaleGroupState(Record):
    last_timescale: float
    last_time: float
    last_scaled_time: float
    first_change_index: int
    next_change_index: int

    def init(self, next_index: int):
        self.last_timescale = 1.0
        self.last_time = 0.0
        self.last_scaled_time = 0.0
        self.first_change_index = next_index
        self.next_change_index = next_index

    def get(self, time: float) -> float:
        if time < self.last_time:
            self.init(self.first_change_index)
        for change in iter_timescale_changes(self.next_change_index):
            next_timescale = change.timescale
            next_time = beat_to_time(change.beat)
            next_scaled_time = self.last_scaled_time + (next_time - self.last_time) * self.last_timescale
            if time <= next_time:
                if (next_time - self.last_time) < 1e-6:
                    return self.last_scaled_time
                return remap(self.last_time, next_time, self.last_scaled_time, next_scaled_time, time)
            self.last_timescale = next_timescale
            self.last_time = next_time
            self.last_scaled_time = next_scaled_time
            self.next_change_index = change.next.index
        return self.last_scaled_time + (time - self.last_time) * self.last_timescale


def timescale_change_archetype() -> type[TimescaleChangeLike]:
    return cast(type[TimescaleChangeLike], get_archetype_by_name(TIMESCALE_CHANGE_NAME))


def timescale_group_archetype() -> type[TimescaleGroupLike]:
    return cast(type[TimescaleGroupLike], get_archetype_by_name(TIMESCALE_GROUP_NAME))


def iter_timescale_changes(index: int) -> Iterator[TimescaleChangeLike]:
    while True:
        if index <= 0:
            return
        change = timescale_change_archetype().at(index)
        yield change
        index = change.next.index


def extended_scaled_time(group: int | EntityRef):
    if isinstance(group, EntityRef):
        group = group.index
    return timescale_group_archetype().at(group).current_scaled_time


def extended_time_to_scaled_time(
    group: int | EntityRef,
    time: float,
) -> float:
    if isinstance(group, EntityRef):
        group = group.index
    if group == 0:
        return time
    if time < 0:
        return time
    last_timescale = 1.0
    last_time = 0.0
    last_scaled_time = 0.0
    first_index = timescale_group_archetype().at(group).first.index
    for change in iter_timescale_changes(first_index):
        next_timescale = change.timescale
        next_time = beat_to_time(change.beat)
        next_scaled_time = last_scaled_time + (next_time - last_time) * last_timescale
        if time <= next_time:
            if (next_time - last_time) < 1e-6:
                return last_scaled_time
            return remap(last_time, next_time, last_scaled_time, next_scaled_time, time)
        last_timescale = next_timescale
        last_time = next_time
        last_scaled_time = next_scaled_time
    return last_scaled_time + (time - last_time) * last_timescale


def extended_scaled_time_to_first_time(
    group: int | EntityRef,
    scaled_time: float,
) -> float:
    if isinstance(group, EntityRef):
        group = group.index
    if group == 0:
        return scaled_time
    if scaled_time < 0:
        # Since timescale is initialized to 1.0 at time 0, the first time we reach a negative scaled time
        # is equal to the scaled time itself.
        return scaled_time
    last_timescale = 1.0
    last_time = 0.0
    last_scaled_time = 0.0
    first_index = timescale_group_archetype().at(group).first.index
    for change in iter_timescale_changes(first_index):
        next_timescale = change.timescale
        next_time = beat_to_time(change.beat)
        next_scaled_time = last_scaled_time + (next_time - last_time) * last_timescale
        if (scaled_time <= next_scaled_time and last_timescale > 0) or (
            scaled_time >= next_scaled_time and last_timescale < 0
        ):
            if (next_scaled_time - last_scaled_time) < 1e-6:
                return last_time
            return remap(last_scaled_time, next_scaled_time, last_time, next_time, scaled_time)
        last_timescale = next_timescale
        last_time = next_time
        last_scaled_time = next_scaled_time
    # Assumes we won't run into a case where a scaled time is unreachable.
    # E.g. if timescale starts positive and ends negative, there may be some values that are unreachable.
    return last_time + (scaled_time - last_scaled_time) / last_timescale
