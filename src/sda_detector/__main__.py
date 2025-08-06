"""Main entry point for SDA detector when run as a module - Clean Module Execution.

PURPOSE:
This file enables the SDA detector to be run as a Python module using the -m flag,
following Python packaging best practices.

SDA PRINCIPLES DEMONSTRATED:
1. **Single Responsibility**: This file has ONE job - module execution
2. **Delegation Pattern**: Immediately delegates to service.main()
3. **Clean Boundaries**: Separates execution concern from business logic
4. **No Business Logic**: Pure orchestration, zero intelligence

LEARNING GOALS:
- Understand Python's __main__.py convention
- Learn the -m flag execution pattern
- See how to structure packages for both import and execution
- Recognize the importance of minimal entry points

ARCHITECTURE NOTES:
This file is intentionally minimal. It exists only to enable:
    python -m sda_detector <module_path> [module_name]
    
All actual logic lives in service.main(), keeping this file pure.

Teaching Example:
    >>> # These are equivalent:
    >>> python -m sda_detector src/models  # Uses this __main__.py
    >>> python src/sda_detector/__main__.py src/models  # Direct execution
    >>> 
    >>> # But -m is preferred because:
    >>> # 1. Works from any directory
    >>> # 2. Adds package to sys.path correctly
    >>> # 3. Follows Python conventions

Key Insight:
__main__.py is the 'main method' of a Python package. Keep it minimal
and delegate immediately to avoid mixing concerns.
"""

from .service import main

if __name__ == "__main__":
    main()
