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


@wrapt.decorator
def wrapper(wrapped, instance, args, kwargs):
    instance.call(wrapped.name, *args, **kwds)
    return wrapped(*args, **kwargs)



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
        break

    return mod

class BirdModule(Birdy):
    """
    This is a metaprogramming class to generate python objects behaving like regular python functions but actually
    executing a remote WPS process.
    """

    def build_module(self):
        for process in self.wps.processes:
            yield process.identifier, self.build_function(process.identifier)


    def build_function(self, pid):
        """Create a custom function signature with docstring, instantiate it
        and pass it to a wrapper which will actually call the process."""
        sig = self.build_function_sig(pid)
        exec(sig)
        return wrapper(locals()[pid], self)


    def call(self, identifier, *args, **kwds):
        frame = inspect.currentframe()
        args = inspect.getargvalues(frame)
        cargs = inspect.getcallargs(self.call, args.locals['args'], args.locals['kwds'])


        inputs = []
        for key, value in cargs['named'].items():
            if not isinstance(values, list):
                values = [values]
            for value in values:
                in_value = self._input_value(key, value)
                if in_value is not None:
                    inputs.append((str(key), in_value))

        return self.wps.execute(identifier=identifier, inputs=inputs, mode='sync')

    def build_function_sig(self, pid):
        proc = self.wps.describeprocess(pid)
        args, kwds = self.get_args(proc)
        doc = self.build_doc(proc)

        template="\ndef {}({}):\n{}\n    pass"
        return template.format(pid, ', '.join(args + ['{}={}'.format(k,v) for k,v in kwds.iteritems()]), doc)



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

    def build_doc(self, proc):

        doc = ['    '+3*'\"']
        doc.append(proc.abstract)
        doc.append('')

        # Inputs
        doc.append('Parameters')
        doc.append('----------')
        for i in proc.dataInputs:
            doc.append("{} : {}".format(i.identifier, self.fmt_type(i)))
            doc.append("    {}".format(i.abstract or i.title))
            #if i.metadata:
            #    doc[-1] += " ({})".format(', '.join(['`{} <{}>`_'.format(m.title, m.href) for m in i.metadata]))
        doc.append('')

        # Outputs
        doc.append("Returns")
        doc.append("-------")
        for i in proc.processOutputs:
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







