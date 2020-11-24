import boto3
import click
import botocore

session = boto3.Session(profile_name='arthur')
ec2 = session.resource('ec2')

def filter_instances(project):

    instances = []
    if project:
        filters = [{'Name': 'tag:Project', 'Values': [project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()

    return instances

@click.group()
def cli():
    """ Manage Snapshots """

@cli.group("snapshots")
def snapshots():
    """ Command for snapshots"""

@snapshots.command('list')
@click.option('--project', default=None,
              help="Only Snapshots for project (tag Project:<name>)")
def list_snapshots(project):
    """ List EC2 snapshots """
    instances = filter_instances(project)

    for instance in instances:
        for volume in instance.volumes.all():
            for snapshot in volume.snapshots.all():
                print(', '.join((
                    snapshot.id,
                    volume.id,
                    instance.id,
                    snapshot.state,
                    snapshot.progress,
                    snapshot.start_time.strftime("%c")
                )))
    return

@cli.group("volumes")
def volumes():
    """ Command for volumes"""

@volumes.command('list')
@click.option('--project', default=None,
              help="Only volumes for project (tag Project:<name>)")
def list_volumes(project):
    """ List EC2 Volumes """
    instances = filter_instances(project)

    for instance in instances:
        for volume in instance.volumes.all():
            print(', '.join((
                volume.id,
                instance.id,
                str(volume.size) + 'GiB',
                volume.state,
                volume.encrypted and "Encrypted" or "Not Encrypted"
                )))
    return

@cli.group("instances")
def instances():
    """ Commands for instances """

@instances.command('snapshot')
@click.option('--project', default=None,
              help="Only instances for project (tag Project:<name>)")
def snapshots_instances(project):
    """ Commands to create Snapshots """

    instances = filter_instances(project)

    for instance in instances:
        if instance.state('pending') or instance.state('running'):
            print("Stopping {0} instance ....".format(instance.id))
            instance.stop()
            instance.wait_until_stopped()
            for volume in instance.volumes.all():
                print ("Creating Snapshots of {0} Volume".format(volume.id))
                volume.create_snapshots(Description='Create by Arthur')
            print("Starting {0} instance ....".format(instance.id))
            instance.start()
            instance.wait_until_starting()
    return
@instances.command('list')
@click.option('--project', default=None,
              help="Only instances for project (tag Project:<name>)")

def list_instances(project):
    """ List EC2 Instances """
    instances = filter_instances(project)

    for instance in instances:
        tags = {t['Key']: t['Value'] for t in instance.tags or []}
        print(', '.join((
            instance.id,
            instance.instance_type,
            instance.placement['AvailabilityZone'],
            instance.state['Name'],
            instance.public_dns_name,
            tags.get('Project', '<no_project>')
        )))

    return


@instances.command('stop')
@click.option('--project', default=None,
              help="Only instances for project (tag Project:<name>)")
def stop_instances(project):
    """ Stop EC2 Instances """
    instances = filter_instances(project)

    for instance in instances:
        tags = {t['Key']: t['Value'] for t in instance.tags or []}
        print("Stopping {0} instance ....".format(instance.id))
        try:
            instance.stop()
        except botocore.exceptions.ClientError as e:
            print("Could not stop {0} instances".format(instance.id) + str(e))
            continue

    return

@instances.command('start')
@click.option('--project', default=None,
              help="Only instances for project (tag Project:<name>)")
def start_instances(project):
    """ Start EC2 Instances """
    instances = filter_instances(project)

    for instance in instances:
        tags = {t['Key']: t['Value'] for t in instance.tags or []}
        print("Starting {0} instance ....".format(instance.id))
        try:
            instance.start()
        except botocore.exceptions.ClientError as e:
            print("Could not start {0} instances. ".format(instance.id) + str(e))
            continue

    return

if __name__ == '__main__':
    cli()
