import jujuresources

from path import Path
from jujubigdata import utils
from charmhelpers.core import unitdata

# Main Gobblin class for callbacks
class Gobblin(object):

    def __init__(self, dist_config):
        self.dist_config = dist_config
        self.cpu_arch = utils.cpu_arch()
        self.resources = {
            'gobblin': 'gobblin-%s' % self.cpu_arch,
        }
        self.verify_resources = utils.verify_resources(*self.resources.values())

    def is_installed(self):
        return unitdata.kv().get('gobblin.installed')

    def install(self, force=False):
        if not force and self.is_installed():
            return
        jujuresources.install(self.resources['gobblin'],
                              destination=self.dist_config.path('gobblin'),
                              skip_top_level=True)
        self.dist_config.add_users()
        self.dist_config.add_dirs()

        unitdata.kv().set('gobblin.installed', True)
        unitdata.kv().flush(True)

    def setup_gobblin(self):
        gobblin_bin = self.dist_config.path('gobblin') / 'bin'
        with utils.environment_edit_in_place('/etc/environment') as env:
            if gobblin_bin not in env['PATH']:
                env['PATH'] = ':'.join([env['PATH'], gobblin_bin])
            env['HADOOP_BIN_DIR'] = env['HADOOP_HOME'] + '/bin'
            # TODO (ktsakalozos): make gobblin work direcotry configurable
            env['GOBBLIN_WORK_DIR'] = '/gobblin/work'
            hadoop_conf = env['HADOOP_CONF_DIR'] + '/core-site.xml'
        
        with utils.xmlpropmap_edit_in_place(hadoop_conf) as props:
            hdfs_endpoint = props['fs.defaultFS']

        gobblin_config = ''.join((self.dist_config.path('gobblin'), '/conf', '/gobblin-mapreduce.properties'))
        
        # TODO(ktsakalozos): use a regex or something similar.
        utils.re_edit_in_place(gobblin_config, {
                r'fs.uri=hdfs://localhost:8020': 'fs.uri=%s' % hdfs_endpoint,                
                })

        self.__repair_gobblin_exec()

    def __repair_gobblin_exec(self):
        # 1. Ubuntu uses dash and not bash for sh https://wiki.ubuntu.com/DashAsBinSh
        # 2. Gobblin 0.5.0 comes with guava 15.0 not 18.0
        gobblin_exec = ''.join((self.dist_config.path('gobblin'), '/bin/gobblin-mapreduce.sh'))
        utils.re_edit_in_place(gobblin_exec, {
                r'#!/bin/sh': '#!/bin/bash',
                r'guava-18.0.jar': 'guava-15.0.jar',
                })
        

