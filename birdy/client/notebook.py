import threading
from owslib.wps import Input

from . import utils
from birdy.dependencies import ipywidgets as widgets
from birdy.dependencies import IPython
from birdy.utils import sanitize


def is_notebook():
    """Return whether or not this function is executed in a notebook environment."""
    if not IPython:
        return False

    try:
        shell = IPython.get_ipython().__class__.__name__
        if shell == "ZMQInteractiveShell":
            return True  # Jupyter notebook or qtconsole
        elif shell == "TerminalInteractiveShell":
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False  # Probably standard Python interpreter


def interact(func, inputs):
    """Return a Notebook form to enter input values and launch process.

    The output is stored in the `widget.result` attribute of the response.
    """
    ws = {sanitize(key): input2widget(inpt) for key, inpt in inputs}
    out = widgets.interact_manual(func, **ws)
    out.widget.children[-2].description = "Launch process"
    # IPython.display.display(out)
    return out


def monitor(execution, sleep=3):
    """Monitor the execution of a process using a notebook progress bar widget.

    Parameters
    ----------
    execution : WPSExecution instance
      The execute response to monitor.
    sleep: float
      Number of seconds to wait before each status check.
    """
    progress = widgets.IntProgress(
        value=0,
        min=0,
        max=100,
        step=1,
        description="Processing:",
        bar_style="info",
        orientation="horizontal",
    )

    cancel = widgets.Button(
        description="Cancel",
        button_style="danger",
        disabled=False,
        tooltip="Send `dismiss` request to WPS server.",
    )

    def cancel_handler(b):
        b.value = True
        b.disabled = True
        progress.description = "Interrupted"
        # TODO: Send dismiss signal to server

    cancel.value = False
    cancel.on_click(cancel_handler)

    box = widgets.HBox(
        [progress, cancel], layout=widgets.Layout(justify_content="space-between")
    )
    IPython.display.display(box)

    def check(execution, progress, cancel):
        while not execution.isComplete() and not cancel.value:
            execution.checkStatus(sleepSecs=sleep)
            progress.value = execution.percentCompleted

        if execution.isSucceded():
            progress.value = 100
            cancel.disabled = True
            progress.bar_style = "success"
            progress.description = "Complete"

        else:
            progress.bar_style = "danger"

    thread = threading.Thread(target=check, args=(execution, progress, cancel))
    thread.start()


def input2widget(inpt):
    """Return a Notebook widget to enter values for the input."""
    if not isinstance(inpt, Input):
        raise ValueError

    typ = inpt.dataType
    opt = inpt.allowedValues

    # String default
    default = inpt.defaultValue

    # Object default
    odefault = utils.from_owslib(inpt.defaultValue, inpt.dataType)

    kwds = dict(description=inpt.title)
    if opt:
        vopt = [utils.from_owslib(o, typ) for o in opt]
        if inpt.maxOccurs == 1:
            if len(opt) < 3:
                out = widgets.RadioButtons(options=vopt, **kwds)
            else:
                out = widgets.Dropdown(options=vopt, **kwds)
        else:
            out = widgets.SelectMultiple(
                options=vopt, value=[inpt.defaultValue], description=inpt.title
            )
    elif typ.endswith("float"):
        out = widgets.FloatText(value=odefault, **kwds)
    elif typ.endswith("boolean"):
        out = widgets.Checkbox(value=odefault, **kwds)
    elif typ.endswith("integer"):
        out = widgets.IntText(value=odefault, **kwds)
    elif typ.endswith("positiveInteger"):
        out = widgets.BoundedIntText(value=odefault, min=1e-16, **kwds)
    elif typ.endswith("nonNegativeInteger"):
        out = widgets.BoundedIntText(value=odefault, min=0, **kwds)
    elif typ.endswith("string"):
        out = widgets.Text(value=odefault, placeholder=inpt.abstract, **kwds)
    elif typ.endswith("anyURI"):
        out = widgets.Text(value=odefault, placeholder=inpt.abstract, **kwds)
    elif typ.endswith("time"):
        out = widgets.Text(value=default, placeholder="YYYY-MM-DD", **kwds)
    elif typ.endswith("date"):
        out = widgets.Text(value=default, placeholder="hh-mm-ss", **kwds)
    elif typ.endswith("dateTime"):
        out = widgets.Text(value=default, placeholder="YYYY-MM-DDThh-mm-ss", **kwds)
    elif typ.endswith("angle"):
        out = widgets.BoundedFloatText(min=0, max=360, **kwds)
    elif typ.endswith("ComplexData"):
        out = widgets.Text(description=inpt.title)
    else:
        raise AttributeError("Data type not recognized {}".format(typ))

    return out


def output2widget(output):
    """Return notebook widget based on output mime-type."""
    pass
