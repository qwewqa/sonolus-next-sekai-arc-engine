from sekai.lib.layer import LAYER_BACKGROUND_COVER, LAYER_PREVIEW_COVER, LAYER_STAGE, get_z
from sekai.lib.options import Options
from sekai.lib.skin import Skin
from sekai.preview.layout import (
    PreviewLayout,
    layout_preview_background_dim,
    layout_preview_bottom_cover,
    layout_preview_lane,
    layout_preview_lane_by_edges,
    layout_preview_top_cover,
)


def draw_preview_stage():
    for col in range(PreviewLayout.column_count):
        left_border_layout = layout_preview_lane_by_edges(-6.5, -6, col)
        right_border_layout = layout_preview_lane_by_edges(6, 6.5, col)
        Skin.stage_left_border.draw(left_border_layout, z=get_z(LAYER_STAGE))
        Skin.stage_right_border.draw(right_border_layout, z=get_z(LAYER_STAGE))
        for lane in (-5, -3, -1, 1, 3, 5):
            layout = layout_preview_lane(lane, 1, col)
            Skin.lane.draw(layout, z=get_z(LAYER_STAGE))


def draw_preview_background_dim():
    if Options.background_brightness >= 1.0:
        return

    sprite = +Skin.background_dim
    if not sprite.is_available:
        sprite @= Skin.cover

    layout = layout_preview_background_dim()
    sprite.draw(layout, z=get_z(LAYER_BACKGROUND_COVER), a=1 - Options.background_brightness)


def draw_preview_cover():
    bottom_layout = layout_preview_bottom_cover()
    top_layout = layout_preview_top_cover()
    z = get_z(LAYER_PREVIEW_COVER)
    Skin.cover.draw(
        bottom_layout,
        z=z,
    )
    Skin.cover.draw(
        top_layout,
        z=z,
    )
