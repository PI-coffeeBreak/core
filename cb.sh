#!/bin/sh

set -e

show_help() {
  cat <<EOF
Usage: cb.sh [dev|build|start] [options]

Commands:
  start         Start the application, skipping plugin dependency installation if --optimized flag exists
  build         Install plugin dependencies only
  dev           Run in development mode (with plugin monitoring and reload)

Options:
  --workers=N   Number of Gunicorn workers (default: 1)
  --host=ADDR   Bind address (default: 0.0.0.0)
  --port=PORT   Bind port (default: 8080)
  -h, --help    Show this help message and exit
EOF
}

# Parse command
CMD="$1"
if [ -z "$CMD" ]; then
  echo "No command provided."
  echo
  echo "Usage: cb.sh [dev|build|start] [options]"
  echo "-h, --help    Show help message"
  exit 1
fi
shift

if [ "$CMD" = "-h" ] || [ "$CMD" = "--help" ]; then
  show_help
  exit 0
fi

PLUGINS_DIR="./plugins"
OPTIMIZED_FLAG="./--optimized"

# Default values
WORKERS=1
HOST="0.0.0.0"
PORT="8080"

# Parse options
while [ $# -gt 0 ]; do
  case "$1" in
    --workers=*)
      WORKERS="${1#*=}"
      ;;
    --host=*)
      HOST="${1#*=}"
      ;;
    --port=*)
      PORT="${1#*=}"
      ;;
    -h|--help)
      show_help
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo
      show_help
      exit 1
      ;;
  esac
  shift
done

install_plugin_requirements() {
  if [ ! -d "$PLUGINS_DIR" ]; then
    echo "Plugin directory not found, skipping plugin dependency installation."
    return
  fi

  echo "Installing plugin dependencies..."
  find "$PLUGINS_DIR" -name requirements.txt -exec pip install --no-cache-dir -r {} \;
}

start_app() {
  echo "Starting Gunicorn with $WORKERS worker(s) on $HOST:$PORT..."
  exec gunicorn main:app \
    -k uvicorn.workers.UvicornWorker \
    -w "$WORKERS" \
    -b "$HOST:$PORT" \
    --log-config-json logging_config.json
}

case "$CMD" in
  build)
    echo "Build mode"
    install_plugin_requirements
    ;;

  start)
    echo "Start mode"
    if [ -f "$OPTIMIZED_FLAG" ]; then
      echo "Optimized mode detected. Skipping plugin dependency installation."
    else
      install_plugin_requirements
    fi
    start_app
    ;;

  dev)
    echo "Dev mode"
    install_plugin_requirements
    start_app &
    GUNICORN_PID=$!

    echo "Watching for plugin requirement changes..."
    command -v inotifywait >/dev/null || apk add --no-cache inotify-tools > /dev/null

    watch_plugins() {
      while inotifywait -e modify,create,move,delete -r "$PLUGINS_DIR" --include 'requirements.txt'; do
        echo "Plugin requirements changed. Reinstalling..."
        install_plugin_requirements
        echo "Reloading Gunicorn workers..."
        kill -HUP "$GUNICORN_PID"
      done
    }

    watch_plugins &
    WATCHER_PID=$!

    cleanup() {
      echo "Shutting down..."
      kill "$GUNICORN_PID" "$WATCHER_PID" 2>/dev/null || true
      wait "$GUNICORN_PID" "$WATCHER_PID" 2>/dev/null || true
      exit 0
    }

    trap cleanup INT TERM

    wait "$GUNICORN_PID" "$WATCHER_PID"
    ;;

  *)
    echo "Unknown command: $CMD"
    echo
    show_help
    exit 1
    ;;
esac
