import jujuresources
from charms.reactive import when, when_not
from charms.reactive import set_state, remove_state, is_state
from charmhelpers.core import hookenv
from subprocess import check_call
from charmhelpers.fetch import apt_install

def dist_config():
    from jujubigdata.utils import DistConfig  # no available until after bootstrap

    if not getattr(dist_config, 'value', None):
        gobblin_reqs = ['hadoop_version', 'groups', 'users', 'dirs']
        dist_config.value = DistConfig(filename='dist.yaml', required_keys=gobblin_reqs)
    return dist_config.value


@when_not('bootstrapped')
def bootstrap():
    hookenv.status_set('maintenance', 'Installing base resources')
    apt_install(['python-pip', 'git'])  # git used for testing unreleased version of libs
    check_call(['pip', 'install', '-U', 'pip'])  # 1.5.1 (trusty) pip fails on --download with git repos
    mirror_url = hookenv.config('resources_mirror')
    if not jujuresources.fetch(mirror_url=mirror_url):
        missing = jujuresources.invalid()
        hookenv.status_set('blocked', 'Unable to fetch required resource%s: %s' % (
            's' if len(missing) > 1 else '',
            ', '.join(missing),
        ))
        return
    set_state('bootstrapped')

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
def stop_gobblin():
    remove_state('gobblin.started')
    hookenv.status_set('blocked', 'Waiting for Haddop connection')

