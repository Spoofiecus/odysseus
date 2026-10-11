"""Issue #6288: fire_event() must hold a strong reference to its task.

asyncio keeps only a weak reference to tasks from ``create_task``, so an
unreferenced handler task could be garbage-collected before it ran and the
event would silently never fire.
"""
import asyncio

import src.event_bus as event_bus


def test_fire_event_holds_strong_reference_until_done():
    async def main():
        release = asyncio.Event()

        async def slow_handler(name, owner):
            await release.wait()

        original = event_bus._handle_event
        event_bus._handle_event = slow_handler
        try:
            event_bus.fire_event("message_sent", "alice")
            assert len(event_bus._BG_TASKS) == 1, "task must be strongly referenced"

            release.set()
            await asyncio.sleep(0.05)
            assert len(event_bus._BG_TASKS) == 0, "finished task must be released"
        finally:
            event_bus._handle_event = original

    asyncio.run(main())
