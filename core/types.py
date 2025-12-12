"""Shared data types for the core modules."""

from typing import Dict, List, Any, Tuple, Optional


class ArgumentState:
    """Class representing the state of an argument in a tool call."""

    def __init__(
        self,
        tool_name: str,
        arg_name: str,
        value: Any = "<UNK>",
        certainty: float = 0.0
    ):
        """
        Initialize an argument state.

        Args:
            tool_name: Name of the tool this argument belongs to
            arg_name: Name of the argument
            value: Current value of the argument (or <UNK> if unknown)
            certainty: Certainty probability (0-1)
        """
        self.tool_name = tool_name
        self.arg_name = arg_name
        self.value = value
        self.certainty = certainty

    def to_dict(self) -> Dict:
        """Convert the argument state to a dictionary."""
        return {
            "tool_name": self.tool_name,
            "arg_name": self.arg_name,
            "value": self.value,
            "certainty": self.certainty
        }


class ToolCall:
    """Class representing a tool call with argument states."""

    def __init__(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ):
        """
        Initialize a tool call.

        Args:
            tool_name: Name of the tool to call
            arguments: Dictionary of argument names to values
        """
        self.tool_name = tool_name
        self.arguments = arguments
        self.arg_states: Dict[str, ArgumentState] = {}

    def to_dict(self) -> Dict:
        """Convert the tool call to a dictionary."""
        return {
            "tool_name": self.tool_name,
            "arguments": self.arguments,
            "arg_states": {name: state.to_dict() for name, state in self.arg_states.items()}
        }

    def to_execution_dict(self) -> Dict:
        """Convert the tool call to a dictionary suitable for execution."""
        return {
            "tool_name": self.tool_name,
            "parameters": {k: v for k, v in self.arguments.items() if v != "<UNK>"}
        }

    def __str__(self):
        args_str = ", ".join(f"{k}:{v}" for k, v in self.arguments.items() if v != "<UNK>")
        return f"{self.tool_name}({args_str})"

    def __repr__(self):
        return repr(self.to_dict())


class ClarificationQuestion:
    """Class representing a clarification question."""

    def __init__(
        self,
        question_id: str,
        question_text: str
    ):
        """
        Initialize a clarification question.

        Args:
            question_id: Unique identifier for the question
            question_text: Text of the question to ask the user
        """
        self.question_id = question_id
        self.question_text = question_text

    def to_dict(self) -> Dict:
        """Convert the question to a dictionary."""
        return {
            "question_id": self.question_id,
            "question_text": self.question_text
        }
