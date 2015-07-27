
import __builtin__ as builtins
import sys
from ctypes import pythonapi, c_char_p, c_void_p, py_object

from .streams import check_stream, STDIN_FILENO, STDOUT_FILENO
from .readline_hook import check_encodings, stdio_readline
from .info import assure_PY2


assure_PY2()


original_raw_input = builtins.raw_input
original_input = builtins.input


PyOS_Readline = pythonapi.PyOS_Readline
PyOS_Readline.restype = c_char_p
PyOS_Readline.argtypes = [c_void_p, c_void_p, c_char_p]

PyFile_AsFile = pythonapi.PyFile_AsFile
PyFile_AsFile.restype = c_void_p
PyFile_AsFile.argtypes = [py_object]

STDIN_FILE_POINTER = PyFile_AsFile(py_object(sys.stdin))
STDOUT_FILE_POINTER = PyFile_AsFile(py_object(sys.stdout))


def stdout_encode(s):
	if isinstance(s, bytes):
		return s
	encoding = sys.stdout.encoding
	errors = sys.stdout.errors
	if errors is not None:
		return s.encode(encoding, errors)
	else:
		return s.encode(encoding)

def stdin_decode(b):
	if isinstance(b, unicode):
		return b
	encoding = sys.stdin.encoding
	errors = sys.stdin.errors
	if errors is not None:
		return b.decode(encoding, errors)
	else:
		return b.decode(encoding)

def readline(prompt):
	check_encodings()
	prompt_bytes = stdout_encode(prompt)
	line_bytes = PyOS_Readline(STDIN_FILE_POINTER, STDOUT_FILE_POINTER, prompt_bytes)
	line = stdin_decode(line_bytes)
	return line


def raw_input(prompt=""):
	"""raw_input([prompt]) -> string

Read a string from standard input.  The trailing newline is stripped.
If the user hits EOF (Unix: Ctl-D, Windows: Ctl-Z+Return), raise EOFError.
On Unix, GNU readline is used if enabled.  The prompt string, if given,
is printed without a trailing newline before reading."""
	
	sys.stderr.flush()
	
	tty = check_stream(sys.stdin, STDIN_FILENO) and check_stream(sys.stdout, STDOUT_FILENO)
	
	if tty:
		line = readline(prompt)
	else:
		line = stdio_readline(prompt)
	
	if line:
		return line[:-1] # strip strailing "\n"
	else:
		raise EOFError

def input(prompt=""):
	"""input([prompt]) -> value

Equivalent to eval(raw_input(prompt))."""
	
	return eval(raw_input(prompt))


def enable():
	builtins.raw_input = raw_input
	builtins.input = input

def disable():
	builtins.raw_input = original_raw_input
	builtins.input = original_input
