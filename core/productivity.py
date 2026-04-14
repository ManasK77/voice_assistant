# core/productivity.py
"""
Productivity tools — calculator, to-do list, reminders.
"""

import datetime
import json
import logging
import os
import re
import threading

from config import TODOS_FILE, REMINDERS_FILE

logger = logging.getLogger("VoiceAssist.Productivity")


# =============================================================================
# Calculator
# =============================================================================

def calculate(expression: str) -> str:
    """Evaluate a math expression spoken in natural language."""
    try:
        expr = expression.lower()

        # Remove conversational words
        for word in ["what is", "calculate", "compute", "evaluate", "what's", "equals"]:
            expr = expr.replace(word, "")

        # Replace spoken math words with operators
        replacements = {
            "plus": "+",
            "minus": "-",
            "times": "*",
            "multiplied by": "*",
            "x": "*",
            "divided by": "/",
            "over": "/",
            "percent": "/100",
            "squared": "**2",
            "cubed": "**3",
            "to the power of": "**",
            "power": "**",
        }
        for word, symbol in replacements.items():
            expr = expr.replace(word, symbol)

        # Strip whitespace
        expr = expr.strip()

        # Remove any remaining non-math characters (speech recognition noise like "on", "and", etc.)
        expr = re.sub(r'[a-zA-Z]+', '', expr).strip()

        # Remove extra whitespace
        expr = re.sub(r'\s+', ' ', expr).strip()

        if not expr:
            return "Could not calculate that. Please try rephrasing."

        # Security: only allow digits, operators, parentheses, decimal points, spaces
        if not re.match(r'^[\d\s\+\-\*/\.\(\)\*]+$', expr):
            return "Could not calculate that. Please use numbers and basic math operations."

        # Evaluate with restricted builtins
        result = eval(expr, {"__builtins__": {}})

        # Format result
        if isinstance(result, float):
            if result == int(result):
                result = int(result)
            else:
                result = round(result, 4)

        return f"The answer is {result}"

    except ZeroDivisionError:
        return "Cannot divide by zero"
    except Exception as e:
        logger.warning(f"Calculate error: {e}")
        return "Could not calculate that. Please try rephrasing."


# =============================================================================
# To-Do List
# =============================================================================

def _load_todos() -> list:
    """Load the to-do list from JSON file."""
    try:
        if os.path.isfile(TODOS_FILE):
            with open(TODOS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.warning(f"Error loading todos: {e}")
    return []


def _save_todos(todos: list) -> None:
    """Save the to-do list to JSON file."""
    try:
        with open(TODOS_FILE, "w", encoding="utf-8") as f:
            json.dump(todos, f, indent=2)
    except IOError as e:
        logger.error(f"Error saving todos: {e}")


def add_todo(task: str) -> str:
    """Add a task to the to-do list."""
    try:
        task = task.strip()
        if not task:
            return "Please specify a task to add"

        todos = _load_todos()
        todos.append(task)
        _save_todos(todos)
        return f"Done. Task has been added successfully: {task}"
    except Exception as e:
        logger.error(f"Add todo error: {e}", exc_info=True)
        return "Sorry, could not add that task"


def show_todos() -> str:
    """Show all tasks in the to-do list."""
    try:
        todos = _load_todos()
        if not todos:
            return "Your to-do list is empty"

        items = [f"{i+1}. {task}" for i, task in enumerate(todos)]
        task_list = ", ".join(items)
        return f"You have {len(todos)} tasks: {task_list}"
    except Exception as e:
        logger.error(f"Show todos error: {e}", exc_info=True)
        return "Sorry, could not read your to-do list"


def clear_todos() -> str:
    """Clear all tasks from the to-do list."""
    try:
        _save_todos([])
        return "Done. All tasks have been cleared successfully."
    except Exception as e:
        logger.error(f"Clear todos error: {e}", exc_info=True)
        return "Sorry, could not clear tasks"


# =============================================================================
# Reminders
# =============================================================================

def _load_reminders() -> list:
    """Load reminders from JSON file."""
    try:
        if os.path.isfile(REMINDERS_FILE):
            with open(REMINDERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.warning(f"Error loading reminders: {e}")
    return []


def _save_reminders(reminders: list) -> None:
    """Save reminders to JSON file."""
    try:
        with open(REMINDERS_FILE, "w", encoding="utf-8") as f:
            json.dump(reminders, f, indent=2, default=str)
    except IOError as e:
        logger.error(f"Error saving reminders: {e}")


def set_reminder(text: str, minutes: int = None, speak_fn: callable = None) -> str:
    """Set a reminder that fires after the specified number of minutes."""
    try:
        # Parse minutes from text: look for a number before "minute(s)"
        if minutes is None:
            match = re.search(r'(\d+)\s*minute', text)
            if match:
                minutes = int(match.group(1))
            else:
                minutes = 1

        # Clean up reminder text — remove time-related parts
        reminder_text = text
        for phrase in ["remind me to", "remind me", "set reminder", "set an alarm",
                        f"in {minutes} minutes", f"in {minutes} minute",
                        f"{minutes} minutes", f"{minutes} minute"]:
            reminder_text = reminder_text.replace(phrase, "")
        reminder_text = reminder_text.strip()

        if not reminder_text:
            reminder_text = "Time's up!"

        # Store the reminder
        trigger_time = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
        reminder = {
            "text": reminder_text,
            "time": trigger_time.isoformat(),
            "done": False,
        }
        reminders = _load_reminders()
        reminders.append(reminder)
        _save_reminders(reminders)

        # Start a timer thread if speak_fn is provided
        if speak_fn:
            seconds = minutes * 60
            timer = threading.Timer(seconds, _fire_reminder, args=[reminder_text, speak_fn])
            timer.daemon = True
            timer.start()

        return f"Done. Reminder set successfully for {minutes} minute{'s' if minutes != 1 else ''}: {reminder_text}"

    except Exception as e:
        logger.error(f"Set reminder error: {e}", exc_info=True)
        return "Sorry, could not set that reminder"


def _fire_reminder(text: str, speak_fn: callable) -> None:
    """Fire a reminder — speak it and mark as done."""
    try:
        speak_fn(f"Reminder: {text}")

        # Mark as done in file
        reminders = _load_reminders()
        for reminder in reminders:
            if reminder.get("text") == text and not reminder.get("done"):
                reminder["done"] = True
                break
        _save_reminders(reminders)

    except Exception as e:
        logger.error(f"Fire reminder error: {e}", exc_info=True)


def check_reminders(speak_fn: callable) -> None:
    """Check for past-due reminders and fire them."""
    try:
        reminders = _load_reminders()
        now = datetime.datetime.now()
        updated = False

        for reminder in reminders:
            if reminder.get("done"):
                continue

            trigger_time = datetime.datetime.fromisoformat(reminder["time"])
            if now >= trigger_time:
                speak_fn(f"Reminder: {reminder['text']}")
                reminder["done"] = True
                updated = True

        if updated:
            _save_reminders(reminders)

    except Exception as e:
        logger.error(f"Check reminders error: {e}", exc_info=True)
