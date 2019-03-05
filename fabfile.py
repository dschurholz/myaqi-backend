import fabutils

from django.conf import settings

from fabric.colors import red
from fabric.context_managers import cd
from fabric.operations import prompt
from fabric.contrib import django

django.settings_module('aqi_backend.settings')


fabutils.autodiscover_environments(settings)


class Deploy(fabutils.VirtualenvMixin,
             fabutils.SupervisorMixin,
             fabutils.Deployment):

    """
    Base deployment class, do not use it directly in the commands
    """

    database_handler = fabutils.PostgresqlDatabaseBackup

    def fab_deploy(self):
        """
        Deploys the system to a specified server (check environments.py)
        """

        if self.env.is_production and not prompt(
                red("Do you REALLY wanna deploy to PRODUCTION SERVER? "
                    "Type 'yes' if you know what are you doing."
                    )).lower() == 'yes':
            return

        with cd(self.env.core_dir):
            # db_handler = fabutils.RemoteDatabaseOperations()
            # db_handler.fab_make_remote_backup()
            self.fab_update_repo()
            if prompt("Do you want to install requirements [yes/no]:"
                      ).lower() == 'yes':
                self.fab_install_requirements()
            self.fab_migrate()
            self.fab_clean_pyc_files()
            self.fab_collectstatic()
            self.fab_restart_instance()


class PostgresqlLocalDatabaseOperations(fabutils.LocalDatabaseOperations):
    db_backup_handler_class = fabutils.PostgresqlDatabaseBackup
    db_restore_handler_class = fabutils.PostgresqlDatabaseRestore


fabutils.register_class(Deploy, settings)
fabutils.register_class(PostgresqlLocalDatabaseOperations, settings)
fabutils.register_class(fabutils.RemoteDatabaseOperations, settings)
