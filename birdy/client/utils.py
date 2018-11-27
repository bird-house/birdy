import dateutil.parser
import six
from owslib.wps import ComplexDataInput


def filter_case_insensitive(names, complete_list):
    """Filter a sequence of process names into a `known` and `unknown` list."""
    contained = []
    missing = []
    complete_list_lower = set(map(str.lower, complete_list))

    for name in names:
        if name.lower() in complete_list_lower:
            contained.append(name)
        else:
            missing.append(name)

    return contained, missing


def build_doc(process):
    """Create docstring from process metadata."""
    doc = [process.abstract, ""]

    # Inputs
    if process.dataInputs:
        doc.append("Parameters")
        doc.append("----------")
        for i in process.dataInputs:
            doc.append("{} : {}".format(i.identifier, format_type(i)))
            doc.append("    {}".format(i.abstract or i.title))
            # if i.metadata:
            #    doc[-1] += " ({})".format(', '.join(['`{} <{}>`_'.format(m.title, m.href) for m in i.metadata]))
        doc.append("")

    # Outputs
    if process.processOutputs:
        doc.append("Returns")
        doc.append("-------")
        for i in process.processOutputs:
            doc.append("{} : {}".format(i.identifier, format_type(i)))
            doc.append("    {}".format(i.abstract or i.title))

    doc.append("")
    return "\n".join(doc)


def format_type(obj):
    """Create docstring entry for input parameter from an OWSlib object."""
    nmax = 10

    doc = ""
    try:
        if getattr(obj, "allowedValues", None):
            av = ", ".join(["'{}'".format(i) for i in obj.allowedValues[:nmax]])
            if len(obj.allowedValues) > nmax:
                av += ", ..."
            doc += "{" + av + "}"

        if getattr(obj, "dataType", None):
            doc += obj.dataType

        if getattr(obj, "supportedValues", None):
            doc += ", ".join([":mimetype:`{}`".format(getattr(f, 'mimeType', f)) for f in obj.supportedValues])

        if getattr(obj, "crss", None):
            crss = ", ".join(obj.crss[:nmax])
            if len(obj.crss) > nmax:
                crss += ", ..."
            doc += "[" + crss + "]"

        if getattr(obj, "minOccurs", None) and obj.minOccurs == 0:
            doc += ", optional"

        if getattr(obj, "default", None):
            doc += ", default:{0}".format(obj.defaultValue)

        if getattr(obj, "uoms", None):
            doc += ", units:[{}]".format(", ".join([u.uom for u in obj.uoms]))

    except Exception as e:
        raise type(e)("{0} (in {1} docstring)".format(e, obj.identifier))
    return doc


def convert_input_value(param, value):
    """Convert value into OWSlib objects."""
    # owslib only accepts literaldata, complexdata and boundingboxdata
    if param.dataType:
        if param.dataType == "ComplexData":
            return ComplexDataInput(value)
        if param.dataType == "BoundingBoxData":
            # todo: boundingbox
            return value
    return str(value)


def convert_output_value(value, data_type):
    """Convert a string into another data type."""
    if "string" in data_type:
        pass
    elif "integer" in data_type:
        value = int(value)
    elif "float" in data_type:
        value = float(value)
    elif "boolean" in data_type:
        value = bool(value)
    elif "dateTime" in data_type:
        value = dateutil.parser.parse(value)
    elif "time" in data_type:
        value = dateutil.parser.parse(value).time()
    elif "date" in data_type:
        value = dateutil.parser.parse(value).date()
    elif "ComplexData" in data_type:
        value = ComplexDataInput(value)
    elif "BoundingBoxData" in data_type:
        # todo: boundingbox
        pass
    return value


def delist(data):
    """If data is a sequence with a single element, returns this element, otherwise return a namedtuple."""
    from collections import Iterable

    if (isinstance(data, Iterable) and not isinstance(data, six.string_types) and len(data) == 1):
        return data[0]

    return data


def is_notebook():
    """Return whether or not this function is executed in a notebook environment."""
    try:
        from IPython import get_ipython
    except ImportError:
        return False

    try:
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            return True   # Jupyter notebook or qtconsole
        elif shell == 'TerminalInteractiveShell':
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False      # Probably standard Python interpreter
