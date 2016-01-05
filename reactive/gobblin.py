from charms.reactive import when, when_not
from charms.reactive import set_state, remove_state
from charmhelpers.core import hookenv
from charms.gobblin import Gobblin
from charms.hadoop import get_dist_config


DIST_KEYS = ['hadoop_version', 'groups', 'users', 'dirs']


@when('hadoop.installed')
@when_not('gobblin.installed')
def install_gobblin():
    gobblin = Gobblin(get_dist_config(DIST_KEYS))
    if gobblin.verify_resources():
        hookenv.status_set('maintenance', 'Installing Gobblin')
        gobblin.install()
        set_state('gobblin.installed')


@when('hadoop.installed')
@when_not('hdfs.related')
def missing_hadoop():
    hookenv.status_set('blocked', 'Waiting for relation to HDFS')


@when('hadoop.installed', 'hdfs.related')
@when_not('hdfs.spec.mismatch', 'hdfs.ready')
def waiting_hadoop(hdfs):  # pylint: disable=unused-argument
    hookenv.status_set('waiting', "Waiting for HDFS to become ready")


@when('gobblin.installed', 'hdfs.ready', 'hadoop.hdfs.configured')
@when_not('gobblin.started')
def configure_gobblin(hdfs):
    hookenv.status_set('maintenance', 'Setting up Gobblin')
    gobblin = Gobblin(get_dist_config(DIST_KEYS))
    gobblin.setup_gobblin(hdfs.ip_addr(), hdfs.port())
    set_state('gobblin.started')
    hookenv.status_set('active', 'Ready')


@when('gobblin.started')
@when_not('hdfs.ready')
def stop_gobblin():
    remove_state('gobblin.started')
    hookenv.status_set('blocked', 'Waiting for HDFS to be reconnected')
