from charms.reactive import when, when_not
from charms.reactive import set_state, remove_state
from charmhelpers.core import hookenv
from jujubigdata.handlers import HadoopBase
from charms.gobblin import Gobblin
from charms.hadoop import get_hadoop_base
from jujubigdata.handlers import HDFS
from jujubigdata.utils import DistConfig

DIST_KEYS = ['hadoop_version', 'groups', 'users', 'dirs']

def get_dist_config(keys):
    '''
    Read the dist.yaml. Soon this method will be moved to hadoop base layer.
    '''
    if not getattr(get_dist_config, 'value', None):
        get_dist_config.value = DistConfig(filename='dist.yaml', required_keys=keys)
    return get_dist_config.value


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
def waiting_hadoop(hdfs):
    base_config = get_hadoop_base()
    hdfs.set_spec(base_config.spec())
    hookenv.status_set('waiting', "Waiting for HDFS to become ready")


@when('hadoop.installed', 'hdfs.related', 'hdfs.spec.mismatch')
@when_not('hdfs.ready')
def spec_mismatch_hadoop(*args):
    hookenv.status_set('blocked', "Hadoop and charm specifications mismatch")


@when('gobblin.installed', 'hdfs.ready')
@when_not('gobblin.started')
def configure_gobblin(hdfs):
    hookenv.status_set('maintenance', 'Setting up Hadoop base files')
    base_config = get_hadoop_base()
    hadoop = HDFS(base_config)
    hadoop.configure_hdfs_base(hdfs.ip_addr(), hdfs.port())
    hookenv.status_set('maintenance', 'Setting up Gobblin')
    gobblin = Gobblin(get_dist_config(DIST_KEYS))
    gobblin.setup_gobblin(hdfs.ip_addr(), hdfs.port())
    set_state('gobblin.started')
    hookenv.status_set('active', 'Ready')


@when('gobblin.started')
@when_not('hdfs.ready')
def stop_gobblin():
    remove_state('gobblin.started')
    hookenv.status_set('blocked', 'Waiting for HDFS to be reconnection')
