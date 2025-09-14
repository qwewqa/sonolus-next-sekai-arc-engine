from collections.abc import Iterator
from math import ceil, floor, pi
from typing import Literal, assert_never

from sonolus.script.array import Dim
from sonolus.script.containers import VarArray
from sonolus.script.globals import level_data
from sonolus.script.interval import clamp, lerp, remap
from sonolus.script.printing import PrintColor, PrintFormat, print_number
from sonolus.script.quad import Quad, Rect
from sonolus.script.runtime import HorizontalAlign, ScrollDirection, canvas, screen
from sonolus.script.vec import Vec2

from sekai.lib.layout import NOTE_EDGE_W, NOTE_SLIM_EDGE_W, FlickDirection
from sekai.lib.options import Options

PREVIEW_COLUMN_SECS = 2

PREVIEW_MARGIN_Y = 0.15
PREVIEW_MARGIN_X = 0.4
PREVIEW_EXTEND_MARGIN_X = 0.05
PREVIEW_TEXT_MARGIN_X = 0.015
PREVIEW_TEXT_MARGIN_Y = 0
PREVIEW_TEXT_H = 0.12
PREVIEW_TEXT_W = PREVIEW_MARGIN_X - 2 * PREVIEW_TEXT_MARGIN_X

PREVIEW_LANE_W = 0.02
PREVIEW_STAGE_BORDER_W = 0.25 * PREVIEW_LANE_W
PREVIEW_NOTE_H = PREVIEW_LANE_W / 2
PREVIEW_BAR_LINE_H = 0.002
PREVIEW_BAR_LINE_ALPHA = 0.8

PREVIEW_COVER_ALPHA = 1.0

PREVIEW_Y_MIN = -1 + PREVIEW_MARGIN_Y
PREVIEW_Y_MAX = 1 - PREVIEW_MARGIN_Y

PREVIEW_BAR_EXTEND_W = 3 * PREVIEW_LANE_W


@level_data
class PreviewData:
    max_time: float
    max_beat: float


@level_data
class PreviewLayout:
    column_count: int
    column_width: float


def init_preview_layout():
    PreviewLayout.column_count = ceil(PreviewData.max_time / PREVIEW_COLUMN_SECS)
    PreviewLayout.column_width = 2 * PREVIEW_MARGIN_X + PREVIEW_LANE_W * 12

    canvas().update(
        scroll_direction=ScrollDirection.LEFT_TO_RIGHT,
        size=PreviewLayout.column_width * PreviewLayout.column_count,
    )


def time_to_preview_col(time: float) -> int:
    return floor(time / PREVIEW_COLUMN_SECS)


def time_to_preview_y(time: float) -> float:
    return lerp(PREVIEW_Y_MIN, PREVIEW_Y_MAX, time % PREVIEW_COLUMN_SECS / PREVIEW_COLUMN_SECS)


def lane_to_preview_x(lane: float, col: int) -> float:
    return (col + 0.5) * PreviewLayout.column_width + lane * PREVIEW_LANE_W - screen().w / 2


def layout_preview_lane_by_edges(l: float, r: float, col: int) -> Rect:
    return Rect(
        l=lane_to_preview_x(l, col),
        r=lane_to_preview_x(r, col),
        b=-1,
        t=1,
    )


def layout_preview_lane(lane: float, size: float, col: int) -> Rect:
    return layout_preview_lane_by_edges(lane - size, lane + size, col)


def layout_preview_note_body_by_edges(l: float, r: float, h: float, col: int, y: float) -> Rect:
    return Rect(
        l=lane_to_preview_x(l, col),
        r=lane_to_preview_x(r, col),
        b=y - h,
        t=y + h,
    )


def layout_preview_note_body_slices_by_edges(
    l: float, r: float, h: float, edge_w: float, col: int, y: float
) -> tuple[Rect, Rect, Rect]:
    m = (l + r) / 2
    if r < l:
        # Make the note 0 width; shouldn't normally happen, but in case, we want to handle it gracefully
        l = r = m
    ml = min(l + edge_w, m)
    mr = max(r - edge_w, m)
    return (
        layout_preview_note_body_by_edges(l=l, r=ml, h=h, col=col, y=y),
        layout_preview_note_body_by_edges(l=ml, r=mr, h=h, col=col, y=y),
        layout_preview_note_body_by_edges(l=mr, r=r, h=h, col=col, y=y),
    )


def layout_preview_regular_note_body(lane: float, size: float, col: int, y: float) -> tuple[Rect, Rect, Rect]:
    return layout_preview_note_body_slices_by_edges(
        l=lane - size + Options.note_margin,
        r=lane + size - Options.note_margin,
        h=PREVIEW_NOTE_H,
        edge_w=NOTE_EDGE_W,
        col=col,
        y=y,
    )


def layout_preview_regular_note_body_fallback(lane: float, size: float, col: int, y: float) -> Rect:
    return layout_preview_note_body_by_edges(
        l=lane - size + Options.note_margin,
        r=lane + size - Options.note_margin,
        h=PREVIEW_NOTE_H,
        col=col,
        y=y,
    )


def layout_preview_slim_note_body(lane: float, size: float, col: int, y: float) -> tuple[Rect, Rect, Rect]:
    return layout_preview_note_body_slices_by_edges(
        l=lane - size + Options.note_margin,
        r=lane + size - Options.note_margin,
        h=PREVIEW_NOTE_H,  # Height is handled by the sprite rather than being changed here
        edge_w=NOTE_SLIM_EDGE_W,
        col=col,
        y=y,
    )


def layout_preview_slim_note_body_fallback(lane: float, size: float, col: int, y: float) -> Rect:
    return layout_preview_note_body_by_edges(
        l=lane - size + Options.note_margin,
        r=lane + size - Options.note_margin,
        h=PREVIEW_NOTE_H / 2,  # For fallback, we need to halve the height manually engine-side
        col=col,
        y=y,
    )


def layout_preview_tick(lane: float, col: int, y: float) -> Rect:
    center = Vec2(lane_to_preview_x(lane, col), y)
    return Rect.from_center(center, Vec2(PREVIEW_NOTE_H, PREVIEW_NOTE_H) * 2)


def layout_preview_flick_arrow(lane: float, size: float, direction: FlickDirection, col: int, y: float) -> Rect:
    match direction:
        case FlickDirection.UP_OMNI:
            is_down = False
            reverse = False
        case FlickDirection.DOWN_OMNI:
            is_down = True
            reverse = False
        case FlickDirection.UP_LEFT:
            is_down = False
            reverse = False
        case FlickDirection.UP_RIGHT:
            is_down = False
            reverse = True
        case FlickDirection.DOWN_LEFT:
            is_down = True
            reverse = False
        case FlickDirection.DOWN_RIGHT:
            is_down = True
            reverse = True
        case _:
            assert_never(direction)
    w = clamp(size, 0, 3) / 2
    result = Rect(
        l=lane_to_preview_x(lane - w, col),
        r=lane_to_preview_x(lane + w, col),
        b=y,
        t=y + 2 * w * PREVIEW_NOTE_H,
    )
    if is_down:
        result.t, result.b = result.b, result.t
    if reverse:
        result.l, result.r = result.r, result.l
    return result


def layout_flick_arrow_fallback(lane: float, size: float, direction: FlickDirection, col: int, y: float) -> Quad:
    match direction:
        case FlickDirection.UP_OMNI:
            rotation = 0
        case FlickDirection.DOWN_OMNI:
            rotation = pi
        case FlickDirection.UP_LEFT:
            rotation = pi / 6
        case FlickDirection.UP_RIGHT:
            rotation = -pi / 6
        case FlickDirection.DOWN_LEFT:
            rotation = pi * 5 / 6
            lane -= 0.25  # Note: backwards from the regular skin due to how the sprites are designed
        case FlickDirection.DOWN_RIGHT:
            rotation = -pi * 5 / 6
            lane += 0.25
        case _:
            assert_never(direction)

    w = clamp(size / 2, 1, 2)
    return (
        Rect(l=-1, r=1, t=1, b=-1)
        .as_quad()
        .rotate(rotation)
        .scale(Vec2(w, w) * PREVIEW_LANE_W)
        .translate(Vec2(lane_to_preview_x(lane, col), y + PREVIEW_NOTE_H / 2))
    )


def layout_preview_slide_connector_segment(
    start_lane: float,
    start_size: float,
    start_y: float,
    end_lane: float,
    end_size: float,
    end_y: float,
    col: int,
) -> Iterator[Quad]:
    mx = lane_to_preview_x(0, col)
    x_min = mx - PreviewLayout.column_width / 2 + PREVIEW_EXTEND_MARGIN_X
    x_max = mx + PreviewLayout.column_width / 2 - PREVIEW_EXTEND_MARGIN_X
    bl = Vec2(lane_to_preview_x(start_lane - start_size, col), start_y)
    br = Vec2(lane_to_preview_x(start_lane + start_size, col), start_y)
    tl = Vec2(lane_to_preview_x(end_lane - end_size, col), end_y)
    tr = Vec2(lane_to_preview_x(end_lane + end_size, col), end_y)
    endpoints = VarArray[float, Dim[5]].new()
    endpoints.append(end_y)
    l_x_min = min(bl.x, tl.x)
    l_x_max = max(bl.x, tl.x)
    r_x_min = min(br.x, tr.x)
    r_x_max = max(br.x, tr.x)
    if l_x_min < x_min < l_x_max:
        endpoints.append(remap(l_x_min, l_x_max, bl.y, tl.y, x_min))
    if l_x_min < x_max < l_x_max:
        endpoints.append(remap(l_x_min, l_x_max, bl.y, tl.y, x_max))
    if r_x_min < x_min < r_x_max:
        endpoints.append(remap(r_x_min, r_x_max, br.y, tr.y, x_min))
    if r_x_min < x_max < r_x_max:
        endpoints.append(remap(r_x_min, r_x_max, br.y, tr.y, x_max))
    prev_y = start_y
    prev_l_x = bl.x
    prev_r_x = br.x
    endpoints.sort()
    for next_y in endpoints:
        next_l_x = clamp(remap(start_y, end_y, bl.x, tl.x, next_y), x_min, x_max)
        next_r_x = clamp(remap(start_y, end_y, br.x, tr.x, next_y), x_min, x_max)
        yield Quad(
            bl=Vec2(prev_l_x, prev_y),
            br=Vec2(prev_r_x, prev_y),
            tr=Vec2(next_r_x, next_y),
            tl=Vec2(next_l_x, next_y),
        )
        prev_y = next_y
        prev_l_x = next_l_x
        prev_r_x = next_r_x


def layout_preview_sim_line(
    left_lane: float,
    right_lane: float,
    col: int,
    y: float,
) -> Quad:
    if left_lane > right_lane:
        left_lane, right_lane = right_lane, left_lane
    return Rect(
        l=lane_to_preview_x(left_lane, col),
        r=lane_to_preview_x(right_lane, col),
        b=y - PREVIEW_NOTE_H,
        t=y + PREVIEW_NOTE_H,
    ).as_quad()


def layout_preview_bar_line(
    time: float,
    extend: Literal["left", "right", "both", "none", "left_only", "right_only"] = "none",
) -> Quad:
    col = time_to_preview_col(time)
    left_lane = -6
    right_lane = 6
    left_x = lane_to_preview_x(left_lane, col)
    right_x = lane_to_preview_x(right_lane, col)
    match extend:
        case "left":
            left_x -= PREVIEW_BAR_EXTEND_W
        case "right":
            right_x += PREVIEW_BAR_EXTEND_W
        case "both":
            left_x -= PREVIEW_BAR_EXTEND_W
            right_x += PREVIEW_BAR_EXTEND_W
        case "left_only":
            right_x = left_x
            left_x -= PREVIEW_BAR_EXTEND_W
        case "right_only":
            left_x = right_x
            right_x += PREVIEW_BAR_EXTEND_W
        case _:
            pass
    y = time_to_preview_y(time)
    return Quad(
        bl=Vec2(left_x, y - PREVIEW_BAR_LINE_H),
        br=Vec2(right_x, y - PREVIEW_BAR_LINE_H),
        tr=Vec2(right_x, y + PREVIEW_BAR_LINE_H),
        tl=Vec2(left_x, y + PREVIEW_BAR_LINE_H),
    )


def print_at_time(
    value: float,
    time: float,
    *,
    fmt: PrintFormat,
    decimal_places: int = -1,
    color: PrintColor,
    side: Literal["left", "right"],
):
    print_number(
        value=value,
        fmt=fmt,
        decimal_places=decimal_places,
        anchor=Vec2(
            lane_to_preview_x(
                -7 if side == "left" else 7,
                time_to_preview_col(time),
            )
            + (-PREVIEW_TEXT_MARGIN_X if side == "left" else PREVIEW_TEXT_MARGIN_X),
            time_to_preview_y(time) + PREVIEW_TEXT_MARGIN_Y,
        ),
        pivot=Vec2(1 if side == "left" else 0, 0),
        dimensions=Vec2(PREVIEW_TEXT_W, PREVIEW_TEXT_H),
        color=color,
        horizontal_align=HorizontalAlign.RIGHT if side == "left" else HorizontalAlign.LEFT,
        background=False,
    )


def print_at_bottom(
    value: float,
    col: int,
    *,
    fmt: PrintFormat = PrintFormat.TIME,
    decimal_places: int = 0,
    color: PrintColor = PrintColor.CYAN,
):
    print_number(
        value=value,
        fmt=fmt,
        decimal_places=decimal_places,
        anchor=Vec2(lane_to_preview_x(0, col), PREVIEW_Y_MIN - PREVIEW_TEXT_MARGIN_Y),
        pivot=Vec2(0.5, 1),
        dimensions=Vec2(PREVIEW_TEXT_W, PREVIEW_TEXT_H),
        color=color,
        horizontal_align=HorizontalAlign.CENTER,
        background=False,
    )
