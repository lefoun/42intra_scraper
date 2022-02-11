from os import makedirs

COLORS = {
    'HEADER': '\033[95m',
    'OKBLUE': '\033[94m',
    'OKCYAN': '\033[96m',
    'SUCCESS': '\033[92m',
    'WARNING': '\033[93m',
    'FAIL': '\033[91m',
    'ENDC': '\033[0m',
    'BOLD': '\033[1m',
    'UNDERLINE': '\033[4m',
}

def create_dir(path):
    try:
        print(f"Creating dir {path}")
        makedirs(path + '/', exist_ok=True)
    except OSError as error:
        print(error)