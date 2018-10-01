import os
import click


def monitor(execution):
    with click.progressbar(length=100, label=execution.status) as bar:
        while not execution.isComplete():
            execution.checkStatus(sleepSecs=1)
            bar.label = execution.status
            bar.update(max(execution.percentCompleted, 1))
    if execution.isSucceded():
        click.echo('Output:')
        for output in execution.processOutputs:
            click.echo('{}={}'.format(output.identifier, output.data or output.reference))
    else:
        click.echo('Process execution failed.')


def get_ssl_verify():
    value = os.environ.get('WPS_SSL_VERIFY', 'True')
    if value.lower() == 'true':
        verify = True
    elif value.lower() == 'false':
        import urllib3
        urllib3.disable_warnings()
        click.echo('Warning: Unverified HTTPS request is being made.'
                   ' Adding certificate verification is strongly advised.\n')
        verify = False
    else:
        verify = value
    return verify
