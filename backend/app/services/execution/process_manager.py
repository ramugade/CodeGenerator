"""Process manager for tracking and cancelling running code executions (Directive 07)."""
import asyncio
from typing import Dict, Optional
from dataclasses import dataclass
import signal


@dataclass
class RunningProcess:
    """Information about a running subprocess."""

    session_id: str
    process: asyncio.subprocess.Process
    started_at: float


class ProcessManager:
    """Manages running subprocesses for cancellation support (Directive 07).

    Tracks active code execution processes by session_id, allowing users
    to cancel long-running generations via the /api/cancel endpoint.
    """

    def __init__(self):
        """Initialize process manager."""
        self._active_processes: Dict[str, RunningProcess] = {}

    def register_process(
        self,
        session_id: str,
        process: asyncio.subprocess.Process,
    ) -> None:
        """Register a running process.

        Args:
            session_id: Unique session identifier
            process: The subprocess instance
        """
        import time

        self._active_processes[session_id] = RunningProcess(
            session_id=session_id,
            process=process,
            started_at=time.time(),
        )

    def unregister_process(self, session_id: str) -> None:
        """Unregister a completed process.

        Args:
            session_id: Session identifier to remove
        """
        self._active_processes.pop(session_id, None)

    async def cancel_process(self, session_id: str) -> bool:
        """Cancel a running process (Directive 07).

        Sends SIGTERM first, then SIGKILL if process doesn't stop.

        Args:
            session_id: Session to cancel

        Returns:
            True if process was cancelled, False if not found
        """
        running_process = self._active_processes.get(session_id)
        if not running_process:
            return False

        process = running_process.process

        try:
            # Try graceful termination first (SIGTERM)
            process.terminate()

            # Wait up to 2 seconds for graceful shutdown
            try:
                await asyncio.wait_for(process.wait(), timeout=2.0)
            except asyncio.TimeoutError:
                # If still running, force kill (SIGKILL)
                process.kill()
                await process.wait()

            # Unregister
            self.unregister_process(session_id)
            return True

        except Exception as e:
            # Process might have already exited
            self.unregister_process(session_id)
            return True

    def get_active_sessions(self) -> list[str]:
        """Get list of active session IDs.

        Returns:
            List of session IDs with running processes
        """
        return list(self._active_processes.keys())

    def is_running(self, session_id: str) -> bool:
        """Check if a session has a running process.

        Args:
            session_id: Session to check

        Returns:
            True if session has active process
        """
        return session_id in self._active_processes


# Global process manager instance
process_manager = ProcessManager()
