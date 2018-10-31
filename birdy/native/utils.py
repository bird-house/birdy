import collections

import dateutil.parser
import six
from owslib.wps import ComplexDataInput


def build_doc(process):
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
    nmax = 10

    doc = ""
    try:
        if hasattr(obj, "allowedValues") and len(obj.allowedValues):
            av = ", ".join(["'{}'".format(i) for i in obj.allowedValues[:nmax]])
            if len(obj.allowedValues) > nmax:
                av += ", ..."
            doc += "{" + av + "}"

        if hasattr(obj, "dataType"):
            doc += obj.dataType

        if hasattr(obj, "supportedValues"):
            doc += ", ".join([":mimetype:`{}`".format(f) for f in obj.supportedValues])

        if hasattr(obj, "crss"):
            crss = ", ".join(obj.crss[:nmax])
            if len(obj.crss) > nmax:
                crss += ", ..."
            doc += "[" + crss + "]"

        if hasattr(obj, "minOccurs") and obj.minOccurs == 0:
            doc += ", optional"

        if hasattr(obj, "default"):
            doc += ", default:{0}".format(obj.defaultValue)

        if hasattr(obj, "uoms"):
            doc += ", units:[{}]".format(", ".join([u.uom for u in obj.uoms]))

    except Exception as e:
        raise type(e)("{0} (in {1} docstring)".format(e, obj.identifier))
    return doc


def convert_input_value(param, value):
    # owslib only accepts literaldata, complexdata and boundingboxdata
    if param.dataType:
        if param.dataType == "ComplexData":
            return ComplexDataInput(value)
        if param.dataType == "BoundingBoxData":
            # todo: boundingbox
            return value
    return str(value)


def convert_output_value(value, data_type):
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
    if (
        isinstance(data, collections.Iterable)
        and not isinstance(data, six.string_types)
        and len(data) == 1
    ):
        return data[0]
    return data
