# specify colors for different logging levels
import copy
import logging

import colorama

LOG_COLORS = {
    logging.ERROR: colorama.Fore.YELLOW,
    logging.WARNING: colorama.Fore.YELLOW
}

MODULE_COLORS = {
    "3d-reconstruction-service.reconstruction": colorama.Fore.GREEN,
    "3d-reconstruction-service": colorama.Fore.BLUE,
    "3d-reconstruction-service.log_parser": colorama.Fore.WHITE,
    "3d-reconstruction-service.scheduler": colorama.Fore.LIGHTYELLOW_EX
}


class ColorFormatter(logging.Formatter):
    def format(self, record, *args, **kwargs):
        # if the corresponding logger has children, they may receive modified
        # record, so we want to keep it intact
        new_record = copy.copy(record)
        if new_record.levelno in LOG_COLORS:
            # we want levelname to be in different color, so let's modify it
            new_record.levelname = "{color_begin}{level}{color_end}".format(
                level=new_record.levelname,
                color_begin=LOG_COLORS[new_record.levelno],
                color_end=colorama.Style.RESET_ALL,
            )
        if new_record.name in MODULE_COLORS:
            new_record.name = "{color_begin}{name}{color_end}".format(
                name=new_record.name,
                color_begin=MODULE_COLORS[new_record.name],
                color_end=colorama.Style.RESET_ALL,
            )
        # now we can let standart formatting take care of the rest
        return super(ColorFormatter, self).format(new_record, *args, **kwargs)
