"""Renderer registry. Each module exports a single ``render_<fmt>`` callable.

Renderers are pure functions of IR. They MUST NOT call out to the network,
read additional files, or mutate the dashboard.
"""
