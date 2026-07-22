"""Tests for workflow module"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from datetime import datetime
from workflow import Task, TaskStatus, Workflow


def test_task_creation():
    """Test task creation"""
    task = Task(
        id="task-1",
        name="Test Task",
        status=TaskStatus.PENDING,
        dependencies=[],
    )
    assert task.id == "task-1"
    assert task.status == TaskStatus.PENDING


def test_task_can_execute():
    """Test task execution dependency check"""
    task = Task(
        id="task-2",
        name="Task 2",
        status=TaskStatus.PENDING,
        dependencies=["task-1"],
    )
    assert not task.can_execute(set())
    assert task.can_execute({"task-1"})


def test_workflow():
    """Test workflow operations"""
    workflow = Workflow(
        id="wf-1",
        name="Test Workflow",
        tasks=[],
        created_at=datetime.now(),
    )
    task = Task(
        id="task-1",
        name="Task 1",
        status=TaskStatus.PENDING,
        dependencies=[],
    )
    workflow.add_task(task)
    assert len(workflow.tasks) == 1
    assert workflow.get_task("task-1") == task


def test_get_ready_tasks():
    """Test getting ready tasks"""
    workflow = Workflow(
        id="wf-1",
        name="Test Workflow",
        tasks=[],
        created_at=datetime.now(),
    )
    task1 = Task(
        id="task-1",
        name="Task 1",
        status=TaskStatus.PENDING,
        dependencies=[],
    )
    task2 = Task(
        id="task-2",
        name="Task 2",
        status=TaskStatus.PENDING,
        dependencies=["task-1"],
    )
    workflow.add_task(task1)
    workflow.add_task(task2)
    
    ready = workflow.get_ready_tasks()
    assert len(ready) == 1
    assert ready[0].id == "task-1"
