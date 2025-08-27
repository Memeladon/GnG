import sys
import datetime
import inspect
from colorama import Fore, Style, init

init(autoreset=True)

LEVEL_COLORS = {
    'DEBUG': Fore.CYAN,
    'INFO': Fore.GREEN,
    'WARNING': Fore.YELLOW,
    'ERROR': Fore.RED,
    'CRITICAL': Fore.MAGENTA + Style.BRIGHT,
}

LAYER_COLORS = {
    'DAO': Fore.BLUE,
    'SERVICE': Fore.MAGENTA,
    'ROUTER': Fore.CYAN,
    'SCHEMA': Fore.WHITE,
    'UTIL': Fore.LIGHTBLACK_EX,
    'OTHER': Fore.WHITE,
}

def _guess_layer_and_component():
    stack = inspect.stack()
    # stack[2] — это вызов логгера из кода пользователя
    if len(stack) < 3:
        return 'OTHER', 'unknown'
    frame = stack[2]
    filename = frame.filename.lower()
    # Определяем слой по пути файла
    if '/dao/' in filename:
        layer = 'DAO'
    elif '/service' in filename:
        layer = 'SERVICE'
    elif '/router' in filename:
        layer = 'ROUTER'
    elif '/schema' in filename:
        layer = 'SCHEMA'
    elif '/util' in filename:
        layer = 'UTIL'
    else:
        layer = 'OTHER'
    # Имя компонента: класс.метод или просто функция/файл
    func = frame.function
    cls = None
    if 'self' in frame.frame.f_locals:
        cls = type(frame.frame.f_locals['self']).__name__
    if cls:
        component = f'{cls}.{func}'
    else:
        # Имя файла без пути и расширения
        component = filename.split('/')[-1].split('\\')[-1].split('.')[0]
    return layer, component

class Logger:
    def _log(self, level, layer=None, component=None, message=None):
        if layer is None or component is None:
            auto_layer, auto_component = _guess_layer_and_component()
            layer = layer or auto_layer
            component = component or auto_component
        color = LEVEL_COLORS.get(level, Fore.WHITE)
        layer_color = LAYER_COLORS.get(layer.upper(), Fore.WHITE)
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"{color}{level}{Style.RESET_ALL} | "
              f"{layer_color}{layer.upper()}{Style.RESET_ALL} "
              f"{Fore.WHITE}\"{component}\"{Style.RESET_ALL} | "
              f"{now} | {message}", file=sys.stderr)

    def debug(self, layer=None, component=None, message=None):
        self._log('DEBUG', layer, component, message)
    def info(self, layer=None, component=None, message=None):
        self._log('INFO', layer, component, message)
    def warning(self, layer=None, component=None, message=None):
        self._log('WARNING', layer, component, message)
    def error(self, layer=None, component=None, message=None):
        self._log('ERROR', layer, component, message)
    def critical(self, layer=None, component=None, message=None):
        self._log('CRITICAL', layer, component, message)

log = Logger() 