[app]
title = Runic Row
package.name = runicrow
package.domain = org.runicrow

source.dir = .
source.include_exts = py,png,jpg,mp3,json

version = 0.1
requirements = python3,kivy,pygame

[buildozer]
log_level = 2

[android]
api = 27
minapi = 21
android.permissions = INTERNET

[python]
python.version = 3.9
