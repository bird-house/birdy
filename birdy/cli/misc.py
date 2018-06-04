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
