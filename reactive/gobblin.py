# pylint: disable=unused-argument
from charms.reactive import when, when_not
from charms.reactive import set_state, remove_state
from charmhelpers.core import hookenv
from charms.gobblin import Gobblin
from charms.hadoop import get_dist_config


@when('hadoop.installed')
@when_not('gobblin.installed')
def install_gobblin(hadoop):
    gobblin = Gobblin(hadoop.version(), get_dist_config())
    if gobblin.verify_resources():
        hookenv.status_set('maintenance', 'Installing Gobblin')
        gobblin.install()
        set_state('gobblin.installed')


@when('gobblin.installed', 'hadoop.hdfs.ready')
@when_not('gobblin.started')
def configure_gobblin(hadoop):
    hookenv.status_set('maintenance', 'Setting up Gobblin')
    gobblin = Gobblin(hadoop.version(), get_dist_config())
    gobblin.setup_gobblin(hadoop.namenodes()[0], hadoop.hdfs_port())
    set_state('gobblin.started')
    hookenv.status_set('active', 'Ready')


@when('gobblin.started')
@when_not('hadoop.hdfs.ready')
def stop_gobblin():
    remove_state('gobblin.started')


@when_not('hadoop.related')
def report_blocked():
    hookenv.status_set('blocked', 'Waiting for relation to Hadoop Plugin')


@when('hadoop.related')
@when_not('hadoop.hdfs.ready')
def report_waiting(hadoop):
    hookenv.status_set('waiting', 'Waiting for HDFS')
