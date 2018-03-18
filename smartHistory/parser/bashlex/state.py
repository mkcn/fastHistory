from parser.bashlex import flags
from parser.bashlex import utils

parserstate = lambda: utils.typedset(flags.parser)
