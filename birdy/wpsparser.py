import logging
LOGGER = logging.getLogger("BIRDY")


def is_complex_data(inoutput):
    if inoutput.dataType is None:
        return False
    else:
        return 'ComplexData' in inoutput.dataType


def is_bbox_data(inoutput):
    if inoutput.dataType is None:
        return False
    else:
        return 'BoundingBoxData' in inoutput.dataType


def parse_default(input):
    default = None
    if hasattr(input, 'defaultValue'):
        default = input.defaultValue
        if default is not None:
            if is_complex_data(input):
                # TODO: get default value of complex type
                default = None  # input.defaultValue.mimeType
            elif is_bbox_data(input):
                # TODO: get default value of bbox
                default = None
            else:
                default = str(input.defaultValue)
    return default


def parse_description(input):
    description = ''
    if hasattr(input, 'title') and input.title is not None:
        description = str(input.title)
    if hasattr(input, 'abstract'):
        description = description + ": " + str(input.abstract)
    default = parse_default(input)
    # LOGGER.debug("id=%s, datatype=%s", input.identifier, input.dataType)
    if is_complex_data(input):
        if len(input.supportedValues) > 0:
            mime_types = ",".join([str(value.mimeType) for value in input.supportedValues])
            description = description + ", mime types=" + mime_types
    elif is_bbox_data(input):
        LOGGER.debug("bounding box input")
        if len(input.supportedValues) > 0:
            crs_list = ",".join(input.supportedValues)
            description = description + ", supported CRS=" + crs_list
    if default is not None:
        description = description + " (default: " + str(default) + ")"
    return str(description)


def parse_type(input):
    # TODO: see https://docs.python.org/2/library/argparse.html#type
    if 'boolean' in input.dataType:
        parsed_type = type(True)
    elif 'integer' in input.dataType:
        parsed_type = type(1)
    elif 'float' in input.dataType:
        parsed_type = type(1.0)
    elif 'ComplexData' in input.dataType:
        parsed_type = type('http://')
    else:
        parsed_type = type('')
    return parsed_type


def parse_choices(input):
    choices = None
    if len(input.allowedValues) > 0 and not input.allowedValues[0] == 'AnyValue':
        choices = input.allowedValues
    return choices


def parse_required(input):
    required = True
    if input.minOccurs == 0:
        required = False
    return required


def parse_nargs(input):
    nargs = '?'
    if input.maxOccurs > 1:
        if input.minOccurs > 0:
            nargs = '+'
        else:
            nargs = '*'
    elif input.minOccurs == 1:
        nargs == 1
    return nargs


def parse_process_help(process):
    help = "{}: {}".format(process.title or process.identifier, process.abstract or '')
    # escape "%" with "%%" in argparse help
    help = help.replace(r"%", r"%%")
    return help


def parse_wps_description(wps):
    description = "{0.title}: {0.abstract}".format(wps.identification)
    return description
