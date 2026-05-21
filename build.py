import PyInstaller.__main__

PyInstaller.__main__.run([
    'main.py',
    '--onefile',
    '--name=douyin_lottery',
    '--console',
    '--paths=.',
    '--hidden-import=url_parser',
    '--hidden-import=api',
    '--hidden-import=browser',
    '--hidden-import=lottery',
    '--hidden-import=models',
])
