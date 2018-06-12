import types
import inspect
import wrapt
import funcsigs
from birdy import Birdy
from birdy import wpsparser
import functools

"""
The idea is to be able to do something like

from birdy import native_client

fp = native_client('http://pavics.ouranos.ca/twitcher/ows/proxy/flyingpigeon/wps')

out = fp.subset_countries('CAN', ...)

"""


def with_arguments(self):
    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwds):
        sig = funcsigs.signature(wrapped)
        ba = sig.bind(*args, **kwds)
        out = self.call(wrapped.__name__, **ba.arguments)
        return out
    return wrapper




# TODO: Deal with authorizations
def native_client(url):
    """Return an automatically generated module with the processes from given WPS service.

    Parameters
    ----------
    url : str
      Link to WPS provider.

    """
    gen = BirdModule(url)

    mod = types.ModuleType(gen.wps.identification.title.split()[0].lower(), gen.wps.identification.abstract)

    # Fill mod.__dict__ with the processes
    for name, func in gen.build_module():
        mod.__dict__[name] = func

    return mod

class BirdModule(Birdy):
    """
    This is a metaprogramming class to generate python objects behaving like regular python functions but actually
    executing a remote WPS process.
    """
    processes = {}
    def build_module(self):
        for process in self.wps.processes:
            yield process.identifier, self.build_function(process.identifier)


    def build_function(self, pid):
        """Create a custom function signature with docstring, instantiate it
        and pass it to a wrapper which will actually call the process."""
        self.processes[pid] = self.wps.describeprocess(pid)
        sig = self.build_function_sig(pid)
        #print(sig)
        exec (sig)
        f = locals()[pid]
        return with_arguments(self)(f)


    def call(self, identifier, *args, **kwds):
        from owslib.wps import SYNC, ASYNC
        frame = inspect.currentframe()
        args = inspect.getargvalues(frame)


        inputs = []
        for key, values in args.locals['kwds'].items():
            if not isinstance(values, list):
                values = [values]
            for value in values:
                in_value = self._input_value(key, value)
                if in_value is not None:
                    inputs.append((str(key), in_value))

        outputs = self.build_output(self.processes[identifier])

        resp = self.wps.execute(identifier=identifier, inputs=inputs, output=outputs, mode=SYNC)
        out = []
        for o in resp.processOutputs:
            if len(o.data) == 1:
                out.append(o.data[0])
            else:
                out.append(o.data)

        if len(out) == 1:
            return out[0]
        else:
            return out


    def build_function_sig(self, pid):
        proc = self.processes[pid]
        args, kwds = self.get_args(proc)
        doc = self.build_doc(proc)

        template="\ndef {}({}):\n{}\n    pass"
        return template.format(pid, ', '.join(args + ['{}={}'.format(k,repr(v)) for k,v in kwds.iteritems()]), doc)

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
        return args, kwds

    def build_output(self, process):
        outputs = []
        for o in process.processOutputs:
            outputs.append( (o.identifier, True ))

        return outputs

    def build_doc(self, process):

        doc = ['    '+3*'\"']
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
        return '\n    '.join(doc)


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







