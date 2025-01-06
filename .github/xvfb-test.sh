xrandr || { exit 1; }
xvfb-run -a poetry run python .github/info.py || { exit 1; }
xvfb-run -a poetry run pytest $@
