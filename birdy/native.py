import types
import inspect
import wrapt
from funcsigs import signature #Py2 Py3 would be from inspect import signature
from collections import OrderedDict
from birdy import Birdy
from birdy import wpsparser, utils


"""
To test, launch emu, then


from birdy import native_client
emu = native_client('http://127.0.0.1:5000/')
emu.hello('Carsten')


---
emu.wordcounter('http://www.gutenberg.org/cache/epub/19033/pg19033.txt')

Fails with 
owslib.wps.WPSException : {'locator': None, 'code': 'NoApplicableCode', 'text': 'Process error: wps_wordcounter.py._handler Line 55 cannot use a string pattern on a bytes-like object'}
"""


# TODO: Deal with authorizations
def native_client(url):
    """Return a module with functions calling the WPS processes
     available at the given url.

    Parameters
    ----------
    url : str
      Link to WPS provider.


    Returns
    -------
    out : module
      A module where WPS processes can be called using normal python functions.


    Example
    -------
    >>> emu = native_client('<url for emu wps server>')
    >>> emu.hello('stranger')
    'Hello stranger'

    """
    bm = BirdModule(url)

    # Create module with name from WPS identification.
    mod = types.ModuleType(bm.wps.identification.title.split()[0].lower(), bm.wps.identification.abstract)


    for name, func in bm.build_module():
        mod.__dict__[name] = func

    return mod

class BirdModule(Birdy):
    """
    Construct functions out of WPS processes so they behave as native python functions.
    """
    # Store the process description returned by wps.describeprocess.
    processes = {}

    def build_module(self):
        """Yield the sequence of functions representing WPS processes. """
        for process in self.wps.processes:
            yield process.identifier, self.build_function(process.identifier)


    def build_function(self, pid):
        """Create a custom function signature with docstring, instantiate it
        and pass it to a wrapper which will actually call the process."""

        # Get the process metadata.
        self.processes[pid] = proc = self.wps.describeprocess(pid)
        self.complex_inputs[pid] = OrderedDict()
        self.outputs[pid] = OrderedDict()

        # Create a dummy signature and docstring for the function.
        sig = self.build_function_sig(proc)
        doc = self.build_doc(proc)

        #print(sig)
        # Create function in the local scope and assign docstring.
        exec (sig)
        f = locals()[pid]
        f.__doc__ = doc

        # Decorate, note that it's the decorator who's calling `execute`.
        return self.decorate()(f)


    def decorate(self):
        """Decorator calling the WPS, using the arguments passed to the wrapped function.
        The wrapped function is a dummy used only for its signature and docstring.

        The wrapt.decorator is used to retain the dummy function name and docstring.
        """

        @wrapt.decorator
        def wrapper(wrapped, instance, args, kwds):
            """Bind the function's arguments to the signature."""
            sig = signature(wrapped)
            ba = sig.bind(*args, **kwds)
            out = self.execute(wrapped.__name__, **ba.arguments)
            return out

        return wrapper

    def execute(self, identifier, *args, **kwds):
        """

        """
        from owslib.wps import SYNC, ASYNC
        frame = inspect.currentframe()
        args = inspect.getargvalues(frame)


        inputs = []
        for key, values in args.locals['kwds'].items():
            if not isinstance(values, list):
                values = [values]
            for value in values:
                in_value = self._input_value(key, value, identifier)
                if in_value is not None:
                    inputs.append((str(key), in_value))

        outputs = self.build_output(self.processes[identifier])

        # Execute request in synchronous mode
        print(inputs)
        resp = self.wps.execute(identifier=identifier, inputs=inputs, output=outputs, mode=SYNC)

        # Parse output
        out = []
        for o in resp.processOutputs:
            if o.reference is not None:
                out.append(o.retrieveData())
            else:
                if len(o.data) == 1:
                    out.append(o.data[0])
                else:
                    out.append(o.data)

        if len(out) == 1:
            return out[0]
        else:
            return out


    def build_function_sig(self, process):
        """Return the process function signature."""

        template="\ndef {}({}):\n    pass"

        args, kwds = self.get_args(process)

        return template.format(process.identifier, ', '.join(args + ['{}={}'.format(k,repr(v)) for k,v in kwds.iteritems()]))

    def get_args(self, process):
        """Return a list of positional arguments and a dictionary of optional keyword arguments
        with their default values."""

        args = []
        kwds = {}
        for input in process.dataInputs:
            if wpsparser.parse_required(input):
                args.append(input.identifier)
            else:
                kwds[input.identifier] = wpsparser.parse_default(input)

            if wpsparser.is_complex_data(input):
                mimetypes = ([str(value.mimeType) for value in input.supportedValues])
                self.complex_inputs[process.identifier][input.identifier] = mimetypes

        return args, kwds

    def build_output(self, process):
        """Return output list."""
        for output in process.processOutputs:
            self.outputs[process.identifier][output.identifier] = wpsparser.is_complex_data(output)

        return self.outputs[process.identifier].items()

    def build_doc(self, process):
        """Return function docstring built from WPS metadata."""

        doc = [3*'\"']
        doc.append(process.abstract)
        doc.append('')

        # Inputs
        doc.append('Parameters')
        doc.append('----------')
        for i in process.dataInputs:
            doc.append("{} : {}".format(i.identifier, self.fmt_type(i)))
            doc.append("    {}".format(i.abstract or i.title))
            #if i.metadata:
            #    doc[-1] += " ({})".format(', '.join(['`{} <{}>`_'.format(m.title, m.href) for m in i.metadata]))
        doc.append('')

        # Outputs
        doc.append("Returns")
        doc.append("-------")
        for i in process.processOutputs:
            doc.append("{} : {}".format(i.identifier, self.fmt_type(i)))
            doc.append("    {}".format(i.abstract or i.title))
        doc.extend(['', ''])
        doc.append(3 * '\"')
        return '\n'.join(doc)


    def fmt_type(self, obj):
        """Input and output type formatting (type, default and allowed
        values).
        """
        nmax = 10

        doc = ''
        try:
            if getattr(obj, 'allowedValues', None):
                av = ', '.join(["'{}'".format(i) for i in obj.allowedValues[:nmax]])
                if len(obj.allowedValues) > nmax:
                    av += ', ...'

                doc += "{" + av + "}"

            elif getattr(obj, 'dataType', None):
                doc += obj.dataType

            elif getattr(obj, 'supportedValues', None):
                doc += ', '.join([':mimetype:`{}`'.format(f.mimeType) for f in obj.supportedValues])

            elif getattr(obj, 'crss', None):
                doc += "[" + ', '.join(obj.crss[:nmax])
                if len(obj.crss) > nmax:
                    doc += ', ...'
                doc += "]"

            if getattr(obj, 'minOccurs', None) is not None:
                if obj.minOccurs == 0:
                    doc += ', optional'
                    if getattr(obj, 'default', None):
                        doc += ', default:{0}'.format(obj.defaultValue)

            if getattr(obj, 'uoms', None):
                doc += ', units:[{}]'.format(', '.join([u.uom for u in obj.uoms]))

        except Exception as e:
            raise type(e)(e.message + ' in {0} docstring'.format(obj.identifier))
        return doc







