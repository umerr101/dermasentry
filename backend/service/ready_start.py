"""Block server startup until the verified model is ready for traffic.

This supports hosts whose service-creation connector provides only TCP checks.
The ordinary local entry point retains its asynchronous loading/503 behavior.
"""
from contextlib import asynccontextmanager

from .main import create_app


def create_ready_app():
    app = create_app()
    original_lifespan = app.router.lifespan_context

    @asynccontextmanager
    async def ready_lifespan(instance):
        async with original_lifespan(instance):
            await instance.state.model_task
            if instance.state.classifier is None:
                raise RuntimeError("The verified model failed to initialize")
            yield

    app.router.lifespan_context = ready_lifespan
    return app
