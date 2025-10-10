from sonolus.script.archetype import PlayArchetype, callback
from sonolus.script.array import Array, Dim
from sonolus.script.containers import VarArray
from sonolus.script.quad import Quad
from sonolus.script.runtime import offset_adjusted_time, touches

from sekai.lib import archetype_names
from sekai.lib.layout import layout_hitbox, refresh_layout
from sekai.lib.stage import draw_stage_and_accessories, play_lane_hit_effects
from sekai.lib.streams import Streams
from sekai.play.input_manager import is_allowed_empty


class Stage(PlayArchetype):
    name = archetype_names.STAGE

    def spawn_order(self) -> float:
        return -1e8

    def should_spawn(self) -> bool:
        return True

    @callback(order=-2)
    def update_sequential(self):
        refresh_layout()

    @callback(order=2)
    def touch(self):
        hitboxes = +Array[Quad, Dim[12]]
        for i in range(1, 11):
            hitboxes[i] = layout_hitbox(-6 + i, -5 + i)
        hitboxes[0] = layout_hitbox(-7, -5)
        hitboxes[11] = layout_hitbox(5, 7)
        empty_lanes = VarArray[float, Dim[16]].new()
        for touch in touches():
            if not is_allowed_empty(touch):
                continue
            for i in range(12):
                if hitboxes[i].contains_point(touch.position):
                    lane = -5.5 + i
                    break
            else:
                continue
            if touch.started:
                play_lane_hit_effects(lane)
                if not empty_lanes.is_full():
                    empty_lanes.append(lane)
            else:
                for i in range(12):
                    if hitboxes[i].contains_point(touch.prev_position):
                        prev_rounded_lane = -5.5 + i
                        break
                else:
                    continue
                if lane != prev_rounded_lane:
                    play_lane_hit_effects(lane)
                    if not empty_lanes.is_full():
                        empty_lanes.append(lane)
        if len(empty_lanes) > 0:
            Streams.empty_input_lanes[offset_adjusted_time()] = empty_lanes

    def update_parallel(self):
        draw_stage_and_accessories()
