import jujuresources
from charms.reactive import when, when_not
from charms.reactive import set_state, remove_state, is_state
from charmhelpers.core import hookenv
from subprocess import check_call
from charmhelpers.fetch import apt_install
from jujubigdata.handlers import HadoopBase
from charms.hadoop import get_hadoop_base
from jujubigdata.handlers import HDFS


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
@when_not('hdfs.related')
def missing_hadoop():
    hookenv.status_set('blocked', 'Waiting for relation to HDFS')


@when('bootstrapped', 'hdfs.related')
@when_not('hdfs.ready')
def waiting_hadoop(hdfs):
    base_config = get_hadoop_base()
    hdfs.set_spec(base_config.spec())
    hookenv.status_set('waiting', "Waiting for HDFS to become ready at {}:{}".format(hdfs.ip_addr(), hdfs.port()))


@when('gobblin.installed', 'hdfs.ready')
@when_not('gobblin.started')
def configure_gobblin(hdfs):
    from charms.gobblin import Gobblin  # in lib/charms; not available until after bootstrap

    hookenv.status_set('maintenance', 'Setting up Hadoop base files')
    base_config = get_hadoop_base()
    hadoop = HDFS(base_config)
    hadoop.configure_hdfs_base(hdfs.ip_addr(), hdfs.port())
    hookenv.status_set('maintenance', 'Setting up Gobblin')
    gobblin = Gobblin(dist_config())
    gobblin.setup_gobblin(hdfs.ip_addr(), hdfs.port())
    set_state('gobblin.started')
    hookenv.status_set('active', 'Ready')


@when('gobblin.started')
@when_not('hdfs.ready')
def stop_gobblin():
    remove_state('gobblin.started')
    hookenv.status_set('blocked', 'Waiting for HDFS connection')

