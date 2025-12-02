__version__ = "0.1.1"


def versions():
    import platform

    vers = {}
    vers["expense_tracker"] = __version__
    vers["python"] = platform.python_version()
    vers["platform"] = platform.platform()

    message = "\n".join(f"{k}: {v}" for k, v in vers.items())
    print(message)
