import os
import shutil
import PyInstaller.__main__

# Clean previous builds
for d in ['build', 'dist']:
    if os.path.exists(d):
        shutil.rmtree(d)

PyInstaller.__main__.run([
    'douyin_lottery.spec',
])
