"""Workflow orchestration module"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Callable, Any
from datetime import datetime


class TaskStatus(Enum):
    """Task status enum"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    """Represents a task in a workflow"""
    id: str
    name: str
    status: TaskStatus
    dependencies: List[str]
    result: Optional[Any] = None
    error: Optional[str] = None

    def can_execute(self, completed_tasks: set[str]) -> bool:
        """Check if task can execute based on dependencies"""
        return all(dep in completed_tasks for dep in self.dependencies)


@dataclass
class Workflow:
    """Represents a workflow of tasks"""
    id: str
    name: str
    tasks: List[Task]
    created_at: datetime

    def add_task(self, task: Task) -> None:
        """Add a task to the workflow"""
        self.tasks.append(task)

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def get_ready_tasks(self) -> List[Task]:
        """Get tasks that are ready to execute"""
        completed = {t.id for t in self.tasks if t.status == TaskStatus.COMPLETED}
        return [
            t for t in self.tasks
            if t.status == TaskStatus.PENDING and t.can_execute(completed)
        ]
