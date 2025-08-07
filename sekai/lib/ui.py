from sonolus.script.ui import (
    UiConfig, 
    UiMetric, 
    UiVisibility, 
    UiAnimation, 
    UiAnimationTween, 
    EaseType,
    UiJudgmentErrorStyle,
    UiJudgmentErrorPlacement,
)

ui_config = UiConfig(
    scope="Sekai",
    primary_metric=UiMetric.ARCADE,
    secondary_metric=UiMetric.LIFE,
    menu_visibility=UiVisibility(scale=1, alpha=1),
    judgment_visibility=UiVisibility(scale=1, alpha=1),
    combo_visibility=UiVisibility(scale=1, alpha=1),
    progress_visibility=UiVisibility(scale=1, alpha=1),
    primary_metric_visibility=UiVisibility(scale=1, alpha=1),
    secondary_metric_visibility=UiVisibility(scale=1, alpha=1),
    tutorial_navigation_visibility=UiVisibility(scale=1, alpha=1),
    tutorial_instruction_visibility=UiVisibility(scale=1, alpha=1),
    judgment_animation=UiAnimation(
        scale=UiAnimationTween(
            start=0,
            end=1,
            duration=0.075,
            ease=EaseType.LINEAR,
        ),
        alpha=UiAnimationTween(
            start=1,
            end=0,
            duration=0.3,
            ease=EaseType.NONE,
        ),
    ),
    combo_animation=UiAnimation(
        scale=UiAnimationTween(
            start=0.6,
            end=1,
            duration=0.15,
            ease=EaseType.LINEAR,
        ),
        alpha=UiAnimationTween(
            start=1,
            end=1,
            duration=0,
            ease=EaseType.LINEAR,
        ),
    ),
    judgment_error_style=UiJudgmentErrorStyle.LATE,
    judgment_error_placement=UiJudgmentErrorPlacement.TOP,
    judgment_error_min=20,
)
