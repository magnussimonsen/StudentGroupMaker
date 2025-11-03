#!/bin/bash
# Convenience wrapper - runs the actual script in dev-scripts/
exec "$(dirname "$0")/dev-scripts/run-dev.py" "$@"
