from fastHistory.parser.bashlex import flags
from fastHistory.parser.bashlex import utils

parserstate = lambda: utils.typedset(flags.parser)
