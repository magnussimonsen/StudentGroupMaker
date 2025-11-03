#!/bin/bash
# Convenience wrapper - runs the actual build script in dev-scripts/
exec "$(dirname "$0")/dev-scripts/build.sh" "$@"
