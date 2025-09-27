from sonolus.script.archetype import PlayArchetype, callback
from sonolus.script.array import Dim
from sonolus.script.containers import VarArray
from sonolus.script.interval import clamp
from sonolus.script.runtime import offset_adjusted_time, touches

from sekai.lib import archetype_names
from sekai.lib.layout import layout_hitbox, vec_to_lane
from sekai.lib.stage import draw_stage_and_accessories, play_lane_hit_effects
from sekai.lib.streams import Streams
from sekai.play.input_manager import is_allowed_empty


class Stage(PlayArchetype):
    name = archetype_names.STAGE

    def spawn_order(self) -> float:
        return -1e8

    def should_spawn(self) -> bool:
        return True

    @callback(order=2)
    def touch(self):
        total_hitbox = layout_hitbox(-7, 7)
        empty_lanes = VarArray[float, Dim[16]].new()
        for touch in touches():
            if not total_hitbox.contains_point(touch.position):
                continue
            if not is_allowed_empty(touch):
                continue
            lane = vec_to_lane(touch.position)
            rounded_lane = clamp(round(lane - 0.5) + 0.5, -5.5, 5.5)
            if touch.started:
                play_lane_hit_effects(rounded_lane)
                if not empty_lanes.is_full():
                    empty_lanes.append(rounded_lane)
            else:
                prev_lane = vec_to_lane(touch.prev_position)
                prev_rounded_lane = clamp(round(prev_lane - 0.5) + 0.5, -5.5, 5.5)
                if rounded_lane != prev_rounded_lane:
                    play_lane_hit_effects(rounded_lane)
                    if not empty_lanes.is_full():
                        empty_lanes.append(rounded_lane)
        if len(empty_lanes) > 0:
            Streams.empty_input_lanes[offset_adjusted_time()] = empty_lanes

    def update_parallel(self):
        draw_stage_and_accessories()
