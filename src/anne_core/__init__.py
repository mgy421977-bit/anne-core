"""ANNE Core — Open Cognitive Architecture.

Executable research prototype demonstrating that outputs from heterogeneous
AI systems can be discovered, compared, evaluated, structured, and turned
into persistent cognitive memory that is reusable on later related tasks.
"""

__version__ = "0.1.0"

from anne_core.core import ANNECore, LoopResult
from anne_core.memory.models import CognitiveStructure
from anne_core.memory.sqlite import CognitiveMemory

__all__ = [
    "ANNECore",
    "LoopResult",
    "CognitiveStructure",
    "CognitiveMemory",
    "__version__",
]
