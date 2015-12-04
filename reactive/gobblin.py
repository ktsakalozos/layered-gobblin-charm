from charms.reactive import when, when_not
from charms.reactive import set_state, remove_state, is_state
from charmhelpers.core import hookenv

def dist_config():
    from jujubigdata.utils import DistConfig  # no available until after bootstrap

    if not getattr(dist_config, 'value', None):
        hive_reqs = ['hadoop_version', 'groups', 'users', 'dirs']
        dist_config.value = DistConfig(filename='dist.yaml', required_keys=hive_reqs)
    return dist_config.value

@when('bootstrapped')
@when_not('gobblin.installed')
def install_gobblin(*args):
    from charms.gobblin import Gobblin  # in lib/charms; not available until after bootstrap

    gobblin = Gobblin(dist_config())
    if gobblin.verify_resources():
        hookenv.status_set('maintenance', 'Installing Gobblin')
        gobblin.install()
        set_state('gobblin.installed')

@when('bootstrapped')
@when_not('hadoop.connected')
def missing_hadoop():
    hookenv.status_set('blocked', 'Waiting for relation to Hadoop')

@when('bootstrapped', 'hadoop.connected')
@when_not('hadoop.ready')
def waiting_hadoop(hadoop):
    hookenv.status_set('waiting', 'Waiting for Hadoop to become ready')


@when('gobblin.installed', 'hadoop.ready')
@when_not('gobblin.started')
def configure_gobblin(*args):
    from charms.gobblin import Gobblin  # in lib/charms; not available until after bootstrap

    hookenv.status_set('maintenance', 'Setting up Gobblin')
    gobblin = Gobblin(dist_config())
    gobblin.setup_gobblin()
    set_state('gobblin.started')
    hookenv.status_set('active', 'Ready')


@when('gobblin.started')
@when_not('hadoop.ready')
def stop_hive():
    remove_state('gobblin.started')
    hookenv.status_set('blocked', 'Waiting for Haddop connection')

