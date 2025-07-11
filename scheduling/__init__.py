"""
Scheduling Module

This module handles the creation and management of production schedules,
optimizing for location, crew availability, and other constraints.
"""

from .coordinator import SchedulingCoordinator

# Expose key classes at the module level
__all__ = ['SchedulingCoordinator'] 