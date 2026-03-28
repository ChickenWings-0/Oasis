"""Video engine entry interface.

Provides a single stable API surface for UI integration.
"""

from typing import Any, List, Optional

from .effect import Effect
from .renderer import Renderer
from .text_overlay import TextOverlay
from .timeline import Timeline
from .transition import Transition


class VideoEngine:
    """Single entry-point wrapper around the core renderer.

    Purpose:
    - Expose one stable render method for UI and service layers.

    Inputs:
    - timeline: Source timeline for rendering.
    - t: Timeline time to render.
    - transitions: Optional transition definitions.
    - effects: Optional effect definitions.
    - overlays: Optional text overlay definitions.

    Output:
    - Rendered frame object for time t, or None when no clip is active.
    """

    def __init__(self, renderer: Optional[Renderer] = None) -> None:
        """Create the engine with an optional renderer dependency."""
        self._renderer: Renderer = renderer if renderer is not None else Renderer()

    def render(
        self,
        timeline: Timeline,
        t: int,
        transitions: Optional[List[Transition]] = None,
        effects: Optional[List[Effect]] = None,
        overlays: Optional[List[TextOverlay]] = None,
    ) -> Any:
        """Render a frame at timeline time t using the core pipeline.

        Inputs:
        - timeline: Timeline to evaluate.
        - t: Timeline time.
        - transitions: Optional transition list.
        - effects: Optional effect list.
        - overlays: Optional text overlay list.

        Output:
        - Final frame value from the renderer.
        """
        return self._renderer.render_frame(
            timeline=timeline,
            t=t,
            transitions=transitions,
            effects=effects,
            overlays=overlays,
        )
