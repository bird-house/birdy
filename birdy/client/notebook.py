# noqa: D100

import threading

from owslib.wps import Input

from birdy.dependencies import IPython
from birdy.dependencies import ipywidgets as widgets
from birdy.utils import sanitize

from . import utils

# from traitlets import Dict, Unicode


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


def gui(func):
    """Return a Notebook form to enter input values and launch process."""
    if func.__self__._notebook:
        return Form(func)
    else:
        raise NotImplementedError(
            "The interactive notebook form is only available in a notebook."
        )


class Form:
    """Create notebook form to launch WPS process."""

    def __init__(self, func):
        self.result = None
        wps = func.__self__
        pid = self.pid = [
            k for k in wps._processes.keys() if sanitize(k) == func.__name__
        ][0]

        self.process = wps._processes[pid]
        inputs = list(wps._inputs[pid].items())
        outputs = list(wps._outputs[pid].items())

        # Create widgets
        iw = self.input_widgets(inputs)
        ofw = self.output_formats_widgets(outputs)
        go = widgets.Button(
            description="Launch process",
            layout=widgets.Layout(width="100%"),
            button_style="success",
        )
        out = widgets.Output()

        # Interaction logic
        def execute(change):
            """Execute callback when "Launch process" button is clicked."""
            go.disabled = True
            of = self.output_format_widget_values(ofw)
            if of:
                of = {"output_formats": of}
            kwargs = {**self.input_widget_values(iw), **of}

            with out:
                self.result = func(**kwargs)

        # Connect callback to button
        go.on_click(execute)

        # Create GUI
        ui = self.build_ui(iw, ofw, go)
        IPython.display(ui, out)

    def get(self, asobj=False):
        """Return the process response outputs.

        Parameters
        ----------
        asobj: bool
          If True, object_converters will be used.
        """
        # Mimicks the `WPSResult.get` method, to provide a consistent look and feel to all user interfaces.
        if self.result is None:
            raise ValueError("The process has not yet been executed.")
        return self.result.get(asobj)

    def input_widgets(self, inputs):
        """Return input parameter widgets."""
        return {sanitize(key): input2widget(inpt) for key, inpt in inputs}

    def input_widget_values(self, widgets):
        """Return values from input widgets."""
        return {k: v.value for (k, v) in widgets.items()}

    def output_formats_widgets(self, outputs):
        """Return output formats parameter widgets for ComplexData outputs that have multiple supported formats."""
        of = {}
        style = {"description_width": "initial"}
        if any(
            [
                o.dataType == "ComplexData" and len(o.supportedValues) > 1
                for (key, o) in outputs
            ]
        ):
            for key, output in outputs:
                if hasattr(output, "supportedValues"):
                    of[key] = widgets.RadioButtons(
                        options=[o.mimeType for o in output.supportedValues],
                        description=output.title,
                        description_tooltip=output.abstract,
                        style=style,
                    )

        return of

    def output_format_widget_values(self, widgets):
        """Return the `output_formats` dict from output_formats widgets."""
        out = {}
        for key, val in widgets.items():
            utils.add_output_format(
                out, output_identifier=sanitize(key), mimetype=val.value, as_ref=True
            )
        if out:
            return out
        return {}

    def build_ui(self, input_widgets, of_widgets, go):
        """Create the form."""
        iw = list(input_widgets.values())
        ofw = list(of_widgets.values())

        header = widgets.Button(
            description=self.process.abstract or self.process.identifier,
            layout=widgets.Layout(width="100%"),
        )
        header = widgets.HTML(
            value=f"<h3>{self.process.abstract or self.process.identifier}</h3>"
        )
        input_header = widgets.HTML(value="<h4>Input parameters</h4>")
        widgets.Label("Input parameters")
        inputs = widgets.VBox([input_header, widgets.VBox(iw)])

        if len(ofw) > 0:
            widgets.Label("Complex outputs format")
            outputs_header = widgets.HTML(value="<h4>Complex outputs format</h4>")
            outputs = widgets.VBox([outputs_header, widgets.VBox(ofw)])
        else:
            outputs = None

        ui = widgets.AppLayout(
            header=header, left_sidebar=inputs, right_sidebar=outputs, footer=go
        )

        return ui


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
    style = {"description_width": "initial"}
    layout = {}
    kwds = dict(
        description=inpt.title,
        description_tooltip=inpt.abstract,
        style=style,
        layout=layout,
    )
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
        raise AttributeError(f"Data type not recognized {typ}")

    return out


def output2widget(output):
    """Return notebook widget based on output mime-type."""
    pass
