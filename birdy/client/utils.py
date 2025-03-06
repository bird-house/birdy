# noqa: D100, D101, D102

import datetime as dt
from pathlib import Path
from typing import Any, Optional, Union
from urllib.parse import urlparse

import dateutil.parser
from owslib.wps import ComplexDataInput, Process, WebProcessingService

from ..utils import is_file, sanitize


def filter_case_insensitive(
    names: Union[str, list[str]], complete_list: list[str]
) -> tuple[list[str], list[str]]:
    """
    Filter a sequence of process names into a `known` and `unknown` list.

    Parameters
    ----------
    names : str or list of str
        Process names.
    complete_list : list of str
        List of all available process names.

    Returns
    -------
    tuple
        Tuple of two lists: `contained` and `missing`.
    """
    contained = []
    missing = []
    complete_list_lower = {name.lower() for name in complete_list}

    if isinstance(names, str):
        names = [names]

    for name in names:
        if name.lower() in complete_list_lower:
            contained.append(name)
        else:
            missing.append(name)

    return contained, missing


def pretty_repr(obj: Any, linebreaks: bool = True):
    """
    Output pretty repr for an Output.

    Parameters
    ----------
    obj : Any
        An object.
    linebreaks : bool
        If True, split attributes with linebreaks.
    """
    class_name = obj.__class__.__name__

    try:
        obj = obj._asdict()  # convert namedtuple to dict
    except AttributeError:
        pass

    try:
        items = list(obj.items())
    except AttributeError:
        try:
            items = list(obj.__dict__.items())
        except AttributeError:
            return repr(obj)

    attributes = []
    indent = "    " if linebreaks else ""

    for key, value in items:
        value = pretty_repr(value, linebreaks=False)
        attributes.append(f"{indent}{key}={value}")

    attribute_joiner = ",\n" if linebreaks else ", "
    attributes = attribute_joiner.join(attributes)

    joiner = "\n" if linebreaks else ""
    return joiner.join([class_name + "(", attributes, ")"])


def build_wps_client_doc(
    wps: WebProcessingService, processes: dict[str, Process]
) -> str:
    """
    Create WPSClient docstring.

    Parameters
    ----------
    wps : owslib.wps.WebProcessingService
        A WPS service.
    processes : Dict[str, owslib.wps.Process]
        A dictionary of available processes.

    Returns
    -------
    str
        The formatted docstring for this WPSClient.
    """
    doc = [wps.identification.abstract or "", "", "Processes", "---------", ""]

    for process_name, process in list(processes.items()):
        sanitized_name = sanitize(process_name)
        description = "{name}\n    {abstract}".format(
            name=sanitized_name, abstract=process.abstract or "(No description)"
        )
        doc.append(description)
        doc.append("")

    if not processes:
        doc.append("There aren't any available processes.")

    doc.append("\n")

    return "\n".join(doc)


def build_process_doc(process: Process) -> str:
    """
    Create docstring from process metadata.

    Parameters
    ----------
    process : owslib.wps.Process
        A WPS process.

    Returns
    -------
    str
        The formatted docstring for this process.
    """
    doc = [process.abstract or "", ""]

    # Inputs
    if process.dataInputs:
        doc.append("Parameters")
        doc.append("----------")
        for i in process.dataInputs:
            doc.append(f"{sanitize(i.identifier)} : {format_type(i)}")
            doc.append(f"    {i.abstract or i.title}")
            # if i.metadata:
            #    doc[-1] += " ({})".format(', '.join(['`{} <{}>`_'.format(m.title, m.href) for m in i.metadata]))
        doc.append("")

    # Outputs
    if process.processOutputs:
        doc.append("Returns")
        doc.append("-------")
        for i in process.processOutputs:
            doc.append(f"{sanitize(i.identifier)} : {format_type(i)}")
            doc.append(f"    {i.abstract or i.title}")

    doc.append("")
    return "\n".join(doc)


def format_type(obj: Any) -> str:
    """
    Create docstring entry for input parameter from an OWSlib object.

    Parameters
    ----------
    obj : Any
        An OWSlib object.

    Returns
    -------
    str
        The formatted docstring entry for this object.
    """
    nmax = 10

    doc = ""
    try:
        if getattr(obj, "allowedValues", None):
            av = ", ".join([f"'{i}'" for i in obj.allowedValues[:nmax]])
            if len(obj.allowedValues) > nmax:
                av += ", ..."
            doc += "{" + av + "}"

        if getattr(obj, "dataType", None):
            doc += obj.dataType

        if getattr(obj, "supportedValues", None):
            doc += ", ".join(
                [
                    ":mimetype:`{}`".format(getattr(f, "mimeType", f))
                    for f in obj.supportedValues
                ]
            )

        if getattr(obj, "crss", None):
            crss = ", ".join(obj.crss[:nmax])
            if len(obj.crss) > nmax:
                crss += ", ..."
            doc += "[" + crss + "]"

        if getattr(obj, "minOccurs", None) and obj.minOccurs == 0:
            doc += ", optional"

        if getattr(obj, "default", None):
            doc += f", default:{obj.defaultValue}"

        if getattr(obj, "uoms", None):
            doc += ", units:[{}]".format(", ".join([u.uom for u in obj.uoms]))

    except Exception as e:
        raise type(e)(f"{e} (in {obj.identifier} docstring)")
    return doc


def is_embedded_in_request(url: str, value: Any) -> bool:
    """
    Whether to encode the value as raw data content.

    Parameters
    ----------
    url : str
        URL to the WPS server.
    value : Any
        Value to be sent to the WPS server.

    Returns
    -------
    bool
        True if:
        - value is a file:/// URI or a local path
        - value is a File-like instance
        - url is not localhost
        - value is a File object
        - value is already the string content
    """
    if hasattr(value, "read"):  # File-like
        return True

    u = urlparse(url)

    if isinstance(value, Path):  # pathlib.Path
        p = value
        scheme = "file"
    else:  # String-like
        v = urlparse(value)
        p = Path(v.path)
        scheme = v.scheme

    if scheme == "file":  # Explicit link to file
        if is_file(p):
            return "localhost" not in u.netloc
        else:
            raise OSError(f"{value} should be a local file but was not found on disk.")
    elif scheme == "":  # Could be a local path or just a string
        if is_file(p):
            return "localhost" not in u.netloc
        else:
            return True
    else:  # Other URL (http, https, ftp, ...)
        return False


def to_owslib(
    value: Any,
    data_type: str,
    encoding: Optional[Any] = None,
    mimetype: Optional[Any] = None,
    schema: Optional[Any] = None,
) -> Any:
    """
    Convert value into OWSlib objects.

    Parameters
    ----------
    value : Any
        Value to be converted.
    data_type : str
        The WPS dataType.
    encoding : Any, optional
        Encoding of the data.
    mimetype : Any, optional
        MIME type of the data.
    schema : Any, optional
        Schema of the data.

    Returns
    -------
    Any
        The converted value.
    """
    # owslib only accepts literaldata, complexdata and boundingboxdata

    if data_type == "ComplexData":
        return ComplexDataInput(
            value, encoding=encoding, mimeType=mimetype, schema=schema
        )
    if data_type == "BoundingBoxData":
        # TODO: return BoundingBoxDataInput(data=value, crs=crs, dimensions=2)
        return value
    else:  # LiteralData
        return str(value)


def from_owslib(value: Any, data_type: str) -> Any:
    """
    Convert a string into another data type.

    Parameters
    ----------
    value : Any
        Value to be converted.
    data_type : str
        The WPS dataType.

    Returns
    -------
    Any
        The converted value.
    """
    if value is None:
        return None

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
    elif "angle" in data_type:
        value = float(value)
    elif "ComplexData" in data_type:
        value = ComplexDataInput(value)
    elif "BoundingBoxData" in data_type:
        pass
        # value = BoundingBoxDataInput(value)
    return value


def py_type(data_type: str) -> Any:
    """
    Return the python data type matching the WPS dataType.

    Parameters
    ----------
    data_type : str
        The WPS dataType.

    Returns
    -------
    Any
        The python data type.
    """
    if data_type is None:
        return None
    if "string" in data_type:
        return str
    elif "integer" in data_type:
        return int
    elif "float" in data_type:
        return float
    elif "boolean" in data_type:
        return bool
    elif "dateTime" in data_type:
        return dt.datetime
    elif "time" in data_type:
        return dt.time
    elif "date" in data_type:
        return dt.date
    elif "angle" in data_type:
        return float
    elif "ComplexData" in data_type:
        return str
    elif "BoundingBoxData" in data_type:
        return str


def extend_instance(obj: Any, cls: Any) -> None:
    """
    Apply mixins to a class instance after creation.

    Parameters
    ----------
    obj : Any
        The object to be extended.
    cls : Any
        The class to be added.
    """
    base_cls = obj.__class__
    base_cls_name = obj.__class__.__name__
    obj.__class__ = type(base_cls_name, (cls, base_cls), {})


def add_output_format(
    output_dictionary: dict,
    output_identifier: str,
    as_ref: Optional[bool] = None,
    mimetype: Optional[str] = None,
) -> None:
    """
    Add an output format to an already existing dictionary.

    Parameters
    ----------
    output_dictionary : dict
        The dictionary (created with `create_output_dictionary()`) to which this
        output format will be added.
    output_identifier : str
        Identifier of the output.
    as_ref : bool, optional
        Determines if this output will be returned as a reference or not.
        None for process default.
    mimetype : str or None
        If the process supports multiple MIME types, it can be specified with this argument.
        None for process default.
    """
    output_dictionary[output_identifier] = {
        "as_ref": as_ref,
        "mimetype": mimetype,
    }


def create_output_dictionary(
    output_identifier: str,
    as_ref: Optional[bool] = None,
    mimetype: Optional[str] = None,
) -> dict:
    """
    Create an output format dictionary.

    Parameters
    ----------
    output_identifier : str
        Identifier of the output.
    as_ref : bool, optional
        Determines if this output will be returned as a reference or not.
        None for process default.
    mimetype : str, optional
        If the process supports multiple MIME types, it can be specified with this argument.
        None for process default.

    Returns
    -------
    dict
        Output dictionary.
    """
    output_dictionary = {
        output_identifier: {
            "as_ref": as_ref,
            "mimetype": mimetype,
        }
    }
    return output_dictionary
