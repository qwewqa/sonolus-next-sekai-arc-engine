from enum import IntEnum

from sonolus.script.easing import ease_in_out_quad, ease_in_quad, ease_out_in_quad, ease_out_quad, linstep


class EaseType(IntEnum):
    OUT_IN = -2
    OUT = -2
    LINEAR = 0
    IN = 1
    IN_OUT = 2


def ease(ease_type: EaseType, x: float) -> float:
    match ease_type:
        case EaseType.OUT_IN:
            return ease_out_in_quad(x)
        case EaseType.OUT:
            return ease_out_quad(x)
        case EaseType.IN:
            return ease_in_quad(x)
        case EaseType.IN_OUT:
            return ease_in_out_quad(x)
        case _:
            return linstep(x)
