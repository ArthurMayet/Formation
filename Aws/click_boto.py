import boto3
import click

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
def instances():
    """ Commands for instances """
@instances.command('list')
@click.option('--project', default=None,
              help="Only instances for project (tag Project:<name>)")

def list_instances(project):
    "List EC2 Instances"
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
    "Stop EC2 Instances"
    instances = filter_instances(project)

    for instance in instances:
        tags = {t['Key']: t['Value'] for t in instance.tags or []}
        print("Stopping {0} instance ....".format(instance.id))
        instance.stop()
        print(', '.join((
            instance.id,
            instance.instance_type,
            instance.placement['AvailabilityZone'],
            instance.state['Name'],
            tags.get('Project', '<no_project>')
        )))

    return

@instances.command('start')
@click.option('--project', default=None,
              help="Only instances for project (tag Project:<name>)")
def start_instances(project):
    "Start EC2 Instances"
    instances = filter_instances(project)

    for instance in instances:
        tags = {t['Key']: t['Value'] for t in instance.tags or []}
        print("Starting {0} instance ....".format(instance.id))
        instance.start()
        print(', '.join((
            instance.id,
            instance.instance_type,
            instance.placement['AvailabilityZone'],
            instance.state['Name'],
            instance.public_dns_name,
            tags.get('Project', '<no_project>')
        )))

    return

if __name__ == '__main__':
    instances()
