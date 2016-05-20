import jujuresources

from jujubigdata import utils
from charmhelpers.core import unitdata
from shutil import copy


class Gobblin(object):
    """
    This class manages the Gobblin deployment steps.

    :param DistConfig dist_config: The configuration container object needed.
    """
    def __init__(self, hadoop_version, dist_config):
        self.dist_config = dist_config
        self.hadoop_version = hadoop_version
        self.cpu_arch = utils.cpu_arch()

        self.resources = {
            'gobblin': 'gobblin-hadoop_%s-%s' % (hadoop_version, self.cpu_arch),
        }
        self.verify_resources = utils.verify_resources(*self.resources.values())

    def is_installed(self):
        return unitdata.kv().get('gobblin.installed')

    def install(self, force=False):
        '''
        Create the users and directories. This method is to be called only once.

        :param bool force: Force the execution of the installation even if this is not the first installation attempt.
        '''
        if not force and self.is_installed():
            return
        jujuresources.install(self.resources['gobblin'],
                              destination=self.dist_config.path('gobblin'),
                              skip_top_level=True)
        self.dist_config.add_users()
        self.dist_config.add_dirs()

        unitdata.kv().set('gobblin.installed', True)
        unitdata.kv().flush(True)

    def setup_gobblin(self, host, port):
        '''
        Configure Gobblin. Each time something changes (eg) a new Haddop endpoint is present this method must be called.

        :param str ip: IP of the HDFS endpoint.
        :param str port: Port of the HDFS endpoint.
        '''

        # Setup the environment
        gobblin_bin = self.dist_config.path('gobblin') / 'bin'
        with utils.environment_edit_in_place('/etc/environment') as env:
            if gobblin_bin not in env['PATH']:
                env['PATH'] = ':'.join([env['PATH'], gobblin_bin])
            env['HADOOP_BIN_DIR'] = env['HADOOP_HOME'] + '/bin'
            env['GOBBLIN_WORK_DIR'] = "/user/gobblin/work"

        hdfs_endpoint = ''.join([host, ':', port])

        # Setup gobblin configuration
        conf_dir = self.dist_config.path('gobblin') / 'conf'
        gobblin_config_template = conf_dir / 'gobblin-mapreduce.properties.template'
        gobblin_config = conf_dir / 'gobblin-mapreduce.properties'
        try:
            copy(gobblin_config_template, gobblin_config)
        except FileNotFoundError:
            pass

        utils.re_edit_in_place(gobblin_config, {
            r'fs.uri=hdfs://localhost:8020': 'fs.uri=hdfs://%s' % hdfs_endpoint,
        })

        if '2.7.2' in self.hadoop_version:
            utils.re_edit_in_place(gobblin_config, {
                r'task.data.root.dir=*': 'task.data.root.dir=${env:GOBBLIN_WORK_DIR}/task'
            }, append_non_matches=True)
