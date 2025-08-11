from __future__ import annotations

from collections.abc import Iterator
from typing import Protocol

from sonolus.script.archetype import get_archetype_by_name
from sonolus.script.interval import remap
from sonolus.script.timing import beat_to_time

TIMESCALE_CHANGE_NAME = "TimeScaleChange"
TIMESCALE_GROUP_NAME = "TimeScaleGroup"


class TimescaleChangeLike(Protocol):
    beat: float
    timescale: float
    next_index: int

    @classmethod
    def at(cls, index: int) -> TimescaleChangeLike: ...


class TimescaleGroupLike(Protocol):
    first_index: int
    current_scaled_time: float

    @classmethod
    def at(cls, index: int) -> TimescaleGroupLike: ...


def timescale_change_archetype() -> type[TimescaleChangeLike]:
    return get_archetype_by_name(TIMESCALE_CHANGE_NAME)  # type: ignore


def timescale_group_archetype() -> type[TimescaleGroupLike]:
    return get_archetype_by_name(TIMESCALE_GROUP_NAME)  # type: ignore


def iter_timescale_changes(group_index: int) -> Iterator[TimescaleChangeLike]:
    index = timescale_group_archetype().at(group_index).first_index
    while True:
        if index <= 0:
            return
        change = timescale_change_archetype().at(index)
        yield change
        index = change.next_index


def extended_scaled_time(group_index: int):
    return timescale_group_archetype().at(group_index).current_scaled_time


def extended_time_to_scaled_time(
    group_index: int,
    time: float,
) -> float:
    if group_index == 0:
        return time
    if time < 0:
        return time
    last_timescale = 1.0
    last_time = 0.0
    last_scaled_time = 0.0
    for change in iter_timescale_changes(group_index):
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
    group_index: int,
    scaled_time: float,
) -> float:
    if group_index == 0:
        return scaled_time
    if scaled_time < 0:
        # Since timescale is initialized to 1.0 at time 0, the first time we reach a negative scaled time
        # is equal to the scaled time itself.
        return scaled_time
    last_timescale = 1.0
    last_time = 0.0
    last_scaled_time = 0.0
    for change in iter_timescale_changes(group_index):
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
