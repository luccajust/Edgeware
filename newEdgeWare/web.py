import webbrowser
from random import choice, randrange

#TODO: Add config
webbrowser.register('firefox', None, webbrowser.BackgroundBrowser("C:\\Program Files\\Mozilla Firefox\\firefox.exe"),preferred=True)


def web(web: list):
    """Opens random webpage from resource/web.json"""
    site = choice(web)
    url = site['url'] + choice(site['args'])
    webbrowser.open_new(url)