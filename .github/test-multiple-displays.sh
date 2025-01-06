xrandr
xrandr --setmonitor screen0 800/211x600/159+0+0 screen
xrandr --setmonitor screen1 800/212x600/159+800+0 none
xrandr --listmonitors
poetry run python .github/info.py
poetry run pytest $@
