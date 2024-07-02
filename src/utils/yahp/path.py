import os


def update_file_name(fl: str, prefix: str = None, suffix: str = None, sep: str = "_") -> str:
    basename = os.path.basename(fl)
    dirname = os.path.dirname(fl)
    if prefix:
        basename = f"{prefix}{sep}{basename}"

    elif suffix:
        filename = fl.split(".")[0]
        extensions = fl.split(".")[1:]
        basename = f"{filename}{sep}{suffix}{'.'.join(extensions)}"

    return os.path.join(dirname, basename)
