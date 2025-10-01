from sonolus.script.archetype import EntityRef, PreviewArchetype, imported

from sekai.lib import archetype_names
from sekai.lib.layer import LAYER_SIM_LINE, get_z
from sekai.lib.options import Options
from sekai.lib.skin import Skin
from sekai.preview.layout import layout_preview_sim_line, time_to_preview_col, time_to_preview_y
from sekai.preview.note import PreviewBaseNote


class PreviewSimLine(PreviewArchetype):
    name = archetype_names.SIM_LINE

    left_ref: EntityRef[PreviewBaseNote] = imported(name="left")
    right_ref: EntityRef[PreviewBaseNote] = imported(name="right")

    def render(self):
        target_time = self.left.target_time
        col = time_to_preview_col(target_time)
        y = time_to_preview_y(target_time, col)
        layout = layout_preview_sim_line(
            left_lane=self.left.lane,
            right_lane=self.right.lane,
            col=col,
            y=y,
        )
        Skin.sim_line.draw(layout, z=get_z(LAYER_SIM_LINE), a=Options.sim_line_alpha)

    @property
    def left(self) -> PreviewBaseNote:
        return self.left_ref.get()

    @property
    def right(self) -> PreviewBaseNote:
        return self.right_ref.get()
