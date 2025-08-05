"""Main entry point for SDA detector when run as a module.

This allows the package to be executed with:
    python -m sda_detector <module_path> [module_name]
"""

from .service import main

if __name__ == "__main__":
    main()
