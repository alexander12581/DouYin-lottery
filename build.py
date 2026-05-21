import PyInstaller.__main__

PyInstaller.__main__.run([
    'main.py',
    '--onefile',
    '--name=douyin_lottery',
    '--console',
    '--add-data=url_parser.py;.',
    '--add-data=api.py;.',
    '--add-data=browser.py;.',
    '--add-data=lottery.py;.',
    '--add-data=models.py;.',
])
