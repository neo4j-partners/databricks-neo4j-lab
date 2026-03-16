# Collection of Databricks-specific functions used by scripts

from databricks.sdk import AccountClient, WorkspaceClient
from databricks.sdk.errors.platform import AlreadyExists, BadRequest, InvalidParameterValue, NotFound, \
    ResourceAlreadyExists, ResourceConflict, ResourceDoesNotExist
from databricks.sdk.service import sql
from databricks.sdk.service.catalog import CreateMetastore, UpdateMetastore, UpdateMetastoreDeltaSharingScope
from databricks.sdk.service.catalog import AwsIamRoleRequest, CreateStorageCredential, PermissionsChange, Privilege, \
    SecurableType, VolumeType
from databricks.sdk.service.compute import ClusterSpec, State
from databricks.sdk.service.iam import AccessControlRequest, Patch, PatchOp, PatchSchema, PermissionLevel, \
    WorkspacePermission
from databricks.sdk.service.jobs import NotebookTask, Task
from databricks.sdk.service.marketplace import ConsumerTerms
from databricks.sdk.service.serving import EndpointCoreConfigInput, ServingEndpointAccessControlRequest, \
    ServingEndpointPermissionLevel, ServedEntityInput
from databricks.sdk.service.settings import DefaultNamespaceSetting, StringMessage, TokenAccessControlRequest, \
    TokenPermissionLevel
from databricks.sdk.service.sql import CreateWarehouseRequestWarehouseType, StatementState
from databricks.sdk.service.vectorsearch import EndpointType
from databricks.sdk.service.workspace import AclPermission, ImportFormat, Language, ObjectType

import base64
import copy
from enum import Enum, auto
import json
import logging
import os
import sys
import time
from typing import Dict, List
from urllib.parse import urlparse, urlunsplit

from io import BytesIO
from zipfile import ZipFile


class DBAcademyNamingScheme(Enum):
    USER = 'USERNAME'
    RANDOM = 'RANDOM'


class DBAcademyClusterType(Enum):
    PERSONAL = auto()
    SHARED = auto()
    JOB = auto()


class DBAcademyClusterPolicy(Enum):
    ALL_PURPOSE = 'ALL_PURPOSE'
    JOBS = 'JOBS'
    DLT = 'DLT'
    DLT_UC = 'DLT_UC'


# nested dict implementation of c1.update(c2)
def config_merge(c1: dict, c2: dict):
    for k, v in c2.items():
        if k in c1 and isinstance(c1[k], dict) and isinstance(v, dict):
            c1[k] = config_merge(c1[k], v)
        else:
            c1[k] = v

    return c1


# path can be a file (in which case course_path will be the containing directory) or it
# can be a folder (in which case it will load any .json or .cfg it finds)
def config_load_from_fs(path: str) -> dict:
    config = {}

    if os.path.isdir(path):
        for file in os.scandir(path):
            ext = file.name.split('.')[-1].lower()
            if ext == 'json' or ext == 'cfg':
                with open(file.path) as fd:
                    config.update(json.load(fd))

        config['course_path'] = path

    elif os.path.isfile(path):
        with open(path) as fd:
            config.update(json.load(fd))

        config['course_path'] = os.path.dirname(path)

    return config


def config_load_from_tags(tags: dict) -> dict:
    if tags:
        config_tags = [t for t in tags if t.startswith('dbacademy.config')]

        if config_tags:
            config_tags.sort()

            config_string = ''

            for t in config_tags:
                config_string += tags[t]

            return json.loads(
                base64.b64decode(config_string).decode()
            )


def config_save_to_tags(config: dict, existing_tags: dict = None, tag_max_len=255):
    tags_out = {}

    # remove any existing config tags if present
    if existing_tags:
        for key in filter(
                lambda k: not k.startswith('dbacademy.config'),
                existing_tags.keys()
        ):
            tags_out[key] = existing_tags[key]

    # serialize config and base64 encode it to a string
    config_string = base64.b64encode(
        json.dumps(config).encode()
    ).decode()

    if len(config_string) > tag_max_len:
        custom_tag_count = int((len(config_string) + tag_max_len - 1) / tag_max_len)
        for x in range(custom_tag_count):
            tags_out[f'dbacademy.config.{x:02}'] = config_string[x * tag_max_len:(x + 1) * tag_max_len]
    else:
        tags_out['dbacademy.config'] = config_string

    return tags_out


# initialize a DBAcademy object using Vocareum interface
def voc_init():
    custom_data_file = os.getenv('VOC_CUSTOM_DATA_FILE', 'voccustomdata.txt')

    host = os.getenv('VOC_DB_WORKSPACE_URL')
    token = os.getenv('VOC_DB_API_TOKEN')
    account_id = os.getenv('VOC_DB_ACCOUNT_ID')
    client_id = os.getenv('VOC_DB_SP_APPLICATION_ID')
    client_secret = os.getenv('VOC_DB_SP_SECRET')
    if client_secret:
        client_secret = base64.b64decode(client_secret).decode()

    partid = os.getenv('VOC_PARTID')

    for course_path in [f'/voc/course/part{partid}', '/voc/private/courseware']:
        if os.path.isdir(course_path):
            course_config = config_load_from_fs(course_path)
            if 'metastore_config' not in course_config:
                course_config['metastore_config'] = {}

            course_config['metastore_config']['name'] = partid
            break
    else:
        course_config = {}

    db = DBAcademy(
        host=host,
        token=token,
        account_id=account_id,
        client_id=client_id,
        client_secret=client_secret,
        course_config=course_config
    )

    with open(custom_data_file, 'w') as data_file:
        data_file.write(json.dumps(course_config))

    return db


class DBAcademy:

    def __init__(self,
                 host: str = None,
                 token: str = None,
                 workspace_client: WorkspaceClient = None,
                 account_id: str = None,
                 client_id: str = None,
                 client_secret: str = None,
                 account_host: str = 'https://accounts.cloud.databricks.com',
                 course_config: dict = None,
                 account_client: AccountClient = None,
                 ):

        # set up module logging
        self.logger = logging.getLogger('dbacademy')
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(
            logging.Formatter('%(asctime)s (%(name)s) %(levelname)s: %(message)s')
        )
        self.logger.addHandler(handler)

        # create workspace api client
        if workspace_client:
            self.w = workspace_client
        elif host and token:
            self.w = WorkspaceClient(
                host=host,
                token=token,
                debug_truncate_bytes=1024,
                debug_headers=False)
        else:
            self.w = None

        # create account api client
        if account_client:
            self.a = account_client
        elif account_id and client_id and client_secret:
            self.a = AccountClient(
                host=account_host,
                account_id=account_id,
                client_id=client_id,
                client_secret=client_secret,
                debug_truncate_bytes=1024,
                debug_headers=False)
        else:
            self.a = None

        self.update_config_tags = False

        if course_config:
            self.course_config = copy.deepcopy(course_config) if course_config else {}
            self.update_config_tags = True
            self.logger.info(
                f'using the following provided course configuration:\n{json.dumps(self.course_config, indent=4)}')
        elif self.w and self.a:
            workspace = self.a.workspaces.get(self.w.get_workspace_id())
            self.course_config = config_load_from_tags(workspace.custom_tags) or {}

            if self.course_config:
                self.logger.info(
                    f'loaded the following configuration from workspace custom tags:\n{json.dumps(self.course_config, indent=4)}')
        else:
            self.course_config = {}
            self.logger.warning('no course configuration loaded')

        self._warehouse = None

        self.username = self.w.current_user.me().user_name if self.w else None
        self._default_catalog = None
        self.metastore_defer_setup = False

    @staticmethod
    def safe_name(name: str):
        return ''.join(
            map(
                lambda x: '_' if x in ['.', ' ', '/'] else '' if ord(x) < 0x20 or ord(x) == 0x7f else x,
                name
            )
        ).lower()[0:255]

    @staticmethod
    def _get_name(
            username: str = None,
            naming_scheme=DBAcademyNamingScheme.RANDOM,
            _random_name=None):

        if type(naming_scheme) == DBAcademyNamingScheme:
            naming_scheme = naming_scheme.value

        match naming_scheme:
            case DBAcademyNamingScheme.RANDOM.value:
                return username.split('@')[0]

            case DBAcademyNamingScheme.USER.value:
                return username.split('@')[0] if username else None

            case _:
                return naming_scheme

    def file_to_dbfs(self,
                     local_filename: str,
                     dbfs_filename: str,
                     blocksize: int = 1048576):

        with open(local_filename, 'rb') as ifd:
            ofd = self.w.dbfs.create(dbfs_filename, overwrite=True).handle

            while True:
                data = ifd.read(blocksize)
                if data:
                    self.w.dbfs.add_block(ofd, base64.b64encode(data).decode('ascii'))
                else:
                    break

            self.w.dbfs.close(ofd)

    def zip_to_dbfs(self,
                    zip_file: str,
                    dbfs_dir: str = '/',
                    force: bool = False):

        with open(zip_file, 'rb') as fd:
            zip_info = ZipFile(BytesIO(fd.read()))

        for f in filter(lambda x: not x.endswith('/'), zip_info.namelist()):

            dbfs_file = os.path.join(dbfs_dir, f)

            if force or not self.w.dbfs.exists(path=dbfs_file):
                with zip_info.open(f) as ifd:
                    ofd = self.w.dbfs.create(path=dbfs_file, overwrite=True).handle

                    while True:
                        data = ifd.read(1048576)
                        if data:
                            self.w.dbfs.add_block(ofd, base64.b64encode(data).decode())
                        else:
                            break

                    self.w.dbfs.close(ofd)

    def dir_to_dbfs(self,
                    local_dir: str,
                    dbfs_dir: str = '/'):

        for root, dirs, files in os.walk(local_dir):
            for file in files:
                self.file_to_dbfs(
                    os.path.join(root, file),
                    os.path.join(dbfs_dir, root.lstrip(local_dir), file)
                )

    def _db_files_create_catalog(self, catalog: str):

        if catalog == 'DEFAULT':
            catalog_name = self.default_catalog
        else:
            catalog_name = self.safe_name(catalog)

            if catalog_name != catalog:
                self.logger.warning(
                    f"file_copy: adjusted catalog name from {catalog} to {catalog_name}")

        try:
            self.w.catalogs.create(catalog_name)
            self.logger.info(f"file_copy: created catalog {catalog_name}")

        except BadRequest:
            self.logger.info(f"file_copy: catalog {catalog_name} already exists")

        self.w.grants.update(
            full_name=catalog_name,
            securable_type=SecurableType.CATALOG,
            changes=[
                PermissionsChange(
                    add=[Privilege.USE_CATALOG],
                    principal='account users'
                )
            ]
        )

        return catalog_name

    def _db_files_create_schema(self, schema: str, catalog_name: str):

        schema_name = self.safe_name(schema)

        if schema_name != schema:
            self.logger.warning(f"file_copy: adjusted schema name from {schema} to {schema_name}")

        try:
            self.w.schemas.create(name=schema_name, catalog_name=catalog_name)
            self.logger.info(f"file_copy: created schema {catalog_name}.{schema_name}")

        except BadRequest:
            self.logger.info(f"file_copy: schema {catalog_name}.{schema_name} already exists")

        self.w.grants.update(
            full_name=f'{catalog_name}.{schema_name}',
            securable_type=SecurableType.SCHEMA,
            changes=[
                PermissionsChange(
                    add=[Privilege.USE_SCHEMA],
                    principal='account users'
                )
            ]
        )

        return schema_name

    def _db_files_create_volume(self, volume: str, schema_name: str, catalog_name: str):

        volume_name = self.safe_name(volume)

        if volume_name != volume:
            self.logger.warning(
                f"file_copy: adjusted volume name from {volume} to {volume_name}")

        volume_full_name = '.'.join([catalog_name, schema_name, volume_name])

        try:
            self.w.volumes.create(
                catalog_name=catalog_name,
                schema_name=schema_name,
                name=volume_name,
                volume_type=VolumeType.MANAGED
            )

            self.logger.info(f'created volume {volume_full_name}')

        except ResourceAlreadyExists:
            self.logger.info(f'volume {volume_full_name} already exists')

        self.w.grants.update(
            full_name=volume_full_name,
            securable_type=SecurableType.VOLUME,
            changes=[
                PermissionsChange(
                    add=[Privilege.READ_VOLUME],
                    principal='account users'
                )
            ]
        )

        return volume_name

    def dir_to_db(self, src_dir: str):

        for subdir in os.scandir(src_dir):
            if subdir.name == 'Volumes':
                for catalog_dir in os.scandir(subdir.path):
                    if not catalog_dir.is_dir():
                        self.logger.error(f'file_copy: {catalog_dir.path} is not a directory')
                        continue

                    catalog_name = self._db_files_create_catalog(catalog_dir.name)

                    for schema_dir in os.scandir(catalog_dir.path):
                        if not schema_dir.is_dir():
                            self.logger.error(f'file_copy: {schema_dir.path} is not a directory')
                            continue

                        schema_name = self._db_files_create_schema(schema_dir.name, catalog_name)

                        for volume_dir in os.scandir(schema_dir.path):
                            if not volume_dir.is_dir():
                                self.logger.error(f'file_copy: {volume_dir.path} is not a directory')
                                continue

                            volume_name = self._db_files_create_volume(volume_dir.name, schema_name, catalog_name)

                            for root, dirs, files in os.walk(volume_dir.path):
                                relative_root = root.removeprefix(src_dir)
                                for file in files:
                                    full_dst_path = os.path.join(
                                        '/Volumes', catalog_name, schema_name, volume_name, relative_root, file
                                    )
                                    with open(os.path.join(root, file), "rb") as infd:
                                        self.w.files.upload(full_dst_path, infd)
                                    self.logger.info(f"file_copy: uploaded file {full_dst_path}")
            else:
                self.logger.error(f'file_copy: {subdir.name} namespace not supported')

    def zip_to_db(self, zip_file: str):
        created = {}
        with open(zip_file, 'rb') as fd:
            zip_info = ZipFile(BytesIO(fd.read()))

        for f in filter(lambda x: not x.endswith('/'), zip_info.namelist()):
            path_components = f.lstrip('/').split('/')
            if path_components[0] == 'Volumes':
                if len(path_components) < 5:
                    self.logger.error(f'file_copy: archive member {f} missing required 4-level namespace')
                    continue
                [c,s,v] = path_components[1:4]
                csv = '.'.join([c,s,v])
                if csv not in created:
                    catalog_name = self._db_files_create_catalog(c)
                    schema_name = self._db_files_create_schema(s, catalog_name)
                    volume_name = self._db_files_create_volume(v, schema_name, catalog_name)
                    path = f'/Volumes/{catalog_name}/{schema_name}/{volume_name}'
                    created[csv] = path
                else:
                    path = created[csv]
                path = path + '/' + '/'.join(path_components[4:])
                with zip_info.open(f) as infd:
                    self.w.files.upload(path, infd)
                self.logger.info(f"file_copy: uploaded file {path}")
            else:
                self.logger.error(f'file_copy: {path_components[0]} namespace not supported')

    @property
    def warehouse(self):
        if not self._warehouse:
            warehouse_name = self._get_name(username=self.username, naming_scheme=DBAcademyNamingScheme.USER)
            for warehouse in self.w.warehouses.list():
                if warehouse.name == warehouse_name:
                    if warehouse.state not in [sql.State.RUNNING, sql.State.STARTING, sql.State.DELETED, sql.State.DELETING]:
                        self.w.warehouses.start(warehouse.id)
                    break
            else:
                warehouse = self.w.warehouses.create_and_wait(
                    cluster_size='2X-Small',
                    enable_serverless_compute=True,
                    warehouse_type=CreateWarehouseRequestWarehouseType.PRO,
                    name=warehouse_name,
                    max_num_clusters=1)
                self.logger.info(f'created internal serverless warehouse {warehouse.name}')
            self._warehouse = warehouse.id
        return self._warehouse

    def sql(self, statement: str):
        self.logger.debug(f'executing the following statement:\n{statement}')
        response = self.w.statement_execution.execute_statement(
            statement=statement,
            warehouse_id=self.warehouse,
            wait_timeout='50s',
            on_wait_timeout=sql.ExecuteStatementRequestOnWaitTimeout.CONTINUE
        )
        while response.status.state == StatementState.PENDING:
            self.logger.info(f'still waiting for statement to complete: {response.status.state}')
            time.sleep(5)
            response = self.w.statement_execution.get_statement(statement_id=response.statement_id)
        if response.status.state != StatementState.SUCCEEDED:
            self.logger.info(f'The following statement failed:\n{statement}')
            raise Exception(response.status.error.message)
        return response.result.data_array

    def enable_dbfs(self):
        self.w.workspace_conf.set_status(contents={'enableDbfsFileBrowser': 'true'})

    def enable_tokens(self):
        try:
            self.w.token_management.update_permissions(
                access_control_list=[
                    TokenAccessControlRequest(group_name='users', permission_level=TokenPermissionLevel.CAN_USE)
                ]
            )
            self.logger.info('enabled PAT access for all users')
        except ResourceDoesNotExist:
            token_id = self.w.tokens.create(comment='enable_tokens', lifetime_seconds=30).token_info.token_id
            self.logger.info('created temporary token to enable PAT access for all users')
            self.w.token_management.update_permissions(
                access_control_list=[
                    TokenAccessControlRequest(group_name='users', permission_level=TokenPermissionLevel.CAN_USE)
                ]
            )
            self.logger.info('enabled PAT access for all users')
            try:
                self.w.tokens.delete(token_id)
            except:
                pass

    def workspace_delete_folder(self, folder: str):
        try:
            self.w.workspace.delete(folder, recursive=True)
        except ResourceDoesNotExist:
            pass

    def workspace_clear_folder(self, folder: str):
        for f in self.w.workspace.list(folder):
            self.w.workspace.delete(f.path, recursive=True)

    def workspace_import(self, src_parms: dict, src_base: str, dst_base: str,
                         overwrite: bool = False, dbfs: bool = False):
        url_object = urlparse(src_parms['src'])
        if url_object.scheme:
            dbc = None
            repo = src_parms['src']
            repo_provider = src_parms.get('provider', 'gitHub')
        else:
            repo = None
            repo_provider = None
            if os.path.isabs(src_parms['src']):
                dbc = src_parms['src']
            else:
                dbc = os.path.join(src_base, src_parms['src'])

        folder = src_parms.get('folder', os.path.split(src_parms['src'])[1][0:-4])
        dst = os.path.join(dst_base, folder)

        if overwrite:
            self.workspace_delete_folder(dst)

        try:
            self.w.workspace.get_status(dst)
        except ResourceDoesNotExist:
            if dbc:
                self.logger.info(f"Importing material in {dbc} to {dst}")
                if dbc[-4:].lower() == '.dbc':
                    fmt = ImportFormat.DBC
                    import_dst = dst
                else:
                    fmt = ImportFormat.AUTO
                    import_dst = dst + '.zip'
                with open(dbc, 'rb') as fd:
                    self.w.workspace.import_(
                        path=import_dst, format=fmt,
                        content=base64.b64encode(fd.read()).decode())
                if dbfs:
                    dbc_dbfs = dbc[0:-4] + '-dbfs.zip'
                    if os.path.isfile(dbc_dbfs):
                        self.logger.info(f"Uploading material in {dbc_dbfs} to DBFS")
                        self.zip_to_dbfs(dbc_dbfs, force=overwrite)
            else:
                self.logger.info(f"Pulling material from {repo} to {dst}")
                self.w.repos.create(url=repo, path=dst, provider=repo_provider)

            if 'patch' in src_parms:
                for p in src_parms['patch']:
                    self.logger.info(f"- patching {p['target']}")
                    if os.path.isabs(p['src']):
                        src = p['src']
                    else:
                        src = os.path.join(src_base, p['src'])
                    target = os.path.join(dst, p['target'])
                    try:
                        self.w.workspace.delete(target, recursive=True)
                    except ResourceDoesNotExist:
                        pass
                    with open(src, 'rb') as fd:
                        if src[-4:].lower() == '.dbc':
                            self.w.workspace.import_(
                                path=target,
                                content=base64.b64encode(fd.read()).decode('ascii'),
                                format=ImportFormat.DBC)
                        else:
                            match src.split('.')[-1].lower():
                                case 'py': language = Language.PYTHON
                                case 'r': language = Language.R
                                case 'scala': language = Language.SCALA
                                case 'sql': language = Language.SQL
                                case _: language = None
                            self.w.workspace.import_(
                                path=target,
                                content=base64.b64encode(fd.read()).decode(),
                                format=ImportFormat.SOURCE,
                                language=language)

        if 'entry' in src_parms:
            main_notebook = src_parms['entry']
        else:
            notebooks = sorted(
                [os.path.split(i.path)[1] for i in self.w.workspace.list(dst) if i.object_type == ObjectType.NOTEBOOK]
            )
            main_notebook = notebooks[0] if len(notebooks) else ''

        if main_notebook:
            return os.path.join(dst, main_notebook)

    def workspace_get_url(self, notebook_path: str = None, path: str = None):
        url = urlparse(self.w.config.host)
        if path is None:
            return urlunsplit((url.scheme, url.netloc, url.path, url.query,
                               f'notebook/{self.w.workspace.get_status(notebook_path).object_id}'))
        return urlunsplit((url.scheme, url.netloc, path, url.query, None))

    def secrets_put(self, scope: str = None, secrets: dict = None, principal: str = 'users'):
        if not scope:
            scope = principal
            self.user_putmetadata(principal, records_for={'secrets': scope})
        try:
            self.w.secrets.create_scope(scope=scope)
        except ResourceAlreadyExists:
            pass
        self.w.secrets.put_acl(scope=scope, principal=principal, permission=AclPermission.READ)
        for key in secrets:
            self.w.secrets.put_secret(scope=scope, key=key, string_value=secrets[key])

    def _cluster_config(self, catalog: str = None, settings: dict = None,
                        username: str = None, ctype: DBAcademyClusterType = DBAcademyClusterType.PERSONAL):
        settings = copy.deepcopy(settings) if settings else {}
        if ctype == DBAcademyClusterType.JOB:
            for i in ['autotermination_minutes']:
                if i in settings:
                    del settings[i]
        if 'aws_attributes' not in settings:
            settings['aws_attributes'] = {}
        if 'zone_id' not in settings['aws_attributes']:
            settings['aws_attributes']['zone_id'] = 'auto'
        if 'spark_version' not in settings:
            settings['spark_version'] = self.w.clusters.select_spark_version(
                long_term_support=True, latest=True, photon=False, ml=False, gpu=False)
        if 'node_type_id' not in settings:
            settings['node_type_id'] = (
                self.w.clusters.select_node_type(photon_driver_capable=False, photon_worker_capable=False)
                if ctype != DBAcademyClusterType.JOB else "m6gd.large"
            )
        settings['enable_elastic_disk'] = True
        if 'autotermination_minutes' not in settings and ctype != DBAcademyClusterType.JOB:
            settings['autotermination_minutes'] = 120
        if ctype == DBAcademyClusterType.SHARED:
            settings['data_security_mode'] = 'USER_ISOLATION'
        elif ctype in [DBAcademyClusterType.PERSONAL, DBAcademyClusterType.JOB]:
            settings['data_security_mode'] = 'SINGLE_USER'
            settings['single_user_name'] = username
        if 'spark_conf' not in settings:
            settings['spark_conf'] = {}
        if catalog:
            settings['spark_conf']['spark.databricks.sql.initial.catalog.name'] = catalog
        if 'custom_tags' not in settings:
            settings['custom_tags'] = {}
        if 'num_workers' not in settings and 'autoscale' not in settings:
            settings['spark_conf'].update({
                'spark.databricks.cluster.profile': 'singleNode',
                'spark.master': 'local[*, 4]'
            })
            settings['custom_tags']['ResourceClass'] = 'SingleNode'
            settings['num_workers'] = 0
        if 'spark_env_vars' not in settings:
            settings['spark_env_vars'] = {}
        settings['spark_env_vars']['PYSPARK_PYTHON'] = '/databricks/python3/bin/python3'
        if ctype == DBAcademyClusterType.JOB:
            settings['aws_attributes']['first_on_demand'] = 1
        return settings

    def cluster_policies_create(self):
        policy_definitions = {
            DBAcademyClusterPolicy.ALL_PURPOSE.value: {
                "name": "DBAcademy",
                "cluster_type": {"type": "fixed", "value": "all-purpose"},
                "autotermination_minutes": {"type": "range", "minValue": 1, "maxValue": 180, "defaultValue": 120, "hidden": False},
                "spark_conf.spark.databricks.cluster.profile": {"type": "fixed", "value": "singleNode", "hidden": False},
                "num_workers": {"type": "fixed", "value": 0, "hidden": False},
                "data_security_mode": {"type": "unlimited", "defaultValue": "SINGLE_USER"},
                "runtime_engine": {"type": "unlimited", "defaultValue": "STANDARD"},
                "driver_node_type_id": {"type": "fixed", "value": "i3.xlarge", "hidden": False}
            },
            DBAcademyClusterPolicy.JOBS.value: {
                "name": "DBAcademy Jobs",
                "cluster_type": {"type": "fixed", "value": "job"},
                "spark_conf.spark.databricks.cluster.profile": {"type": "fixed", "value": "singleNode", "hidden": False},
                "num_workers": {"type": "fixed", "value": 0, "hidden": False},
                "data_security_mode": {"type": "unlimited", "defaultValue": "SINGLE_USER"},
                "runtime_engine": {"type": "unlimited", "defaultValue": "STANDARD"},
                "driver_node_type_id": {"type": "fixed", "value": "i3.xlarge", "hidden": False}
            },
            DBAcademyClusterPolicy.DLT.value: {
                "name": "DBAcademy DLT",
                "cluster_type": {"type": "fixed", "value": "dlt"},
                "num_workers": {"type": "range", "maxValue": 1},
                "driver_node_type_id": {"type": "fixed", "value": "i3.xlarge", "hidden": False},
                "node_type_id": {"type": "fixed", "value": "i3.xlarge", "hidden": False},
            },
            DBAcademyClusterPolicy.DLT_UC.value: {
                "name": "DBAcademy DLT UC",
                "cluster_type": {"type": "fixed", "value": "dlt"},
                "num_workers": {"type": "range", "maxValue": 1},
                "driver_node_type_id": {"type": "fixed", "value": "i3.xlarge", "hidden": False},
                "node_type_id": {"type": "fixed", "value": "i3.xlarge", "hidden": False},
            }
        }
        if 'cluster_policies' not in self.course_config:
            return
        for policy in self.course_config['cluster_policies']:
            settings = {}
            if 'template' in policy:
                if policy['template'] in policy_definitions:
                    settings.update(policy_definitions[policy['template']])
            settings.update(policy)
            if 'template' in settings:
                del (settings['template'])
            if 'name' in settings:
                name = settings['name']
                del (settings['name'])
            else:
                continue
            for p in self.w.cluster_policies.list():
                if p.name == name:
                    self.w.cluster_policies.delete(p.policy_id)
                    break
            response = self.w.cluster_policies.create(
                name=name, definition=json.dumps(settings), max_clusters_per_user=1)
            self.logger.info(f'created cluster policy {name}')
            self.w.permissions.set(
                request_object_type='cluster-policies',
                request_object_id=response.policy_id,
                access_control_list=[
                    AccessControlRequest(group_name='users', permission_level=PermissionLevel.CAN_USE)
                ]
            )

    def cluster_start_or_create(self, principal: str = None, catalog: str = None,
                                cluster_name: str = None, _random_name: str = None):
        if 'user_config' in self.course_config and 'cluster_config' in self.course_config['user_config']:
            settings = self.course_config['user_config']['cluster_config']
        elif 'cluster_config' in self.course_config:
            settings = self.course_config['cluster_config']
        else:
            return

        if 'aws_attributes' not in settings:
            settings['aws_attributes'] = {}
            settings['aws_attributes']['first_on_demand'] = 1

        shared = False
        if not cluster_name:
            cluster_name = self._get_name(
                username=principal,
                naming_scheme=settings.get('cluster_name', DBAcademyNamingScheme.RANDOM),
                _random_name=_random_name)
        if cluster_name == settings.get('cluster_name'):
            shared = True

        for c in self.w.clusters.list():
            if c.cluster_name == cluster_name:
                if c.state not in [State.RUNNING, State.PENDING, State.RESIZING, State.RESTARTING]:
                    self.w.clusters.start(c.cluster_id)
                return not shared, cluster_name, c.cluster_id

        settings = self._cluster_config(
            catalog=catalog, username=principal, settings=settings,
            ctype=DBAcademyClusterType.SHARED if shared else DBAcademyClusterType.PERSONAL)
        settings['cluster_name'] = cluster_name

        cluster = self.w.api_client.do('POST', '/api/2.0/clusters/create', body=settings)
        self.logger.info(f'submitted request to create cluster {cluster_name}')

        if 'libraries' in settings:
            self.w.api_client.do('POST', '/api/2.0/libraries/install',
                                 body={'cluster_id': cluster['cluster_id'], 'libraries': settings['libraries']})

        if shared:
            acl = [AccessControlRequest(group_name='users', permission_level=PermissionLevel.CAN_RESTART)]
        else:
            acl = [AccessControlRequest(user_name=principal, permission_level=PermissionLevel.CAN_RESTART)]

        self.w.permissions.set(request_object_type='clusters',
                               request_object_id=cluster['cluster_id'],
                               access_control_list=acl)
        return not shared, cluster_name, cluster['cluster_id']

    def warehouse_start_or_create(self, principal: str = False, warehouse_name: str = None,
                                  _random_name: str = None):
        if 'user_config' in self.course_config and 'warehouse' in self.course_config['user_config']:
            settings = self.course_config['user_config']['warehouse']
        elif 'warehouse' in self.course_config:
            settings = self.course_config['warehouse']
        else:
            return

        shared = False
        if not warehouse_name:
            warehouse_name = self._get_name(
                username=principal,
                naming_scheme=settings.get('name', DBAcademyNamingScheme.RANDOM),
                _random_name=_random_name)
        if warehouse_name == settings.get('name'):
            shared = True

        for wh in self.w.warehouses.list():
            if wh.name == warehouse_name:
                if wh.state not in [sql.State.RUNNING, sql.State.STARTING, sql.State.DELETED, sql.State.DELETING]:
                    self.w.warehouses.start(wh.id)
                return not shared, warehouse_name, wh.id

        settings = copy.deepcopy(settings)
        settings['name'] = warehouse_name
        if 'warehouse_type' not in settings:
            settings['warehouse_type'] = 'PRO'
            settings['enable_serverless_compute'] = True
        if 'spot_instance_policy' not in settings:
            settings['spot_instance_policy'] = 'COST_OPTIMIZED'
        if 'min_num_clusters' not in settings:
            settings['min_num_clusters'] = 1
        if 'max_num_clusters' not in settings:
            settings['max_num_clusters'] = settings['min_num_clusters']
        if 'cluster_size' not in settings:
            settings['cluster_size'] = '2X-Small'
        if 'auto_stop_mins' not in settings:
            settings['auto_stop_mins'] = 30

        warehouse = self.w.api_client.do('POST', '/api/2.0/sql/warehouses', body=settings)
        self.logger.info(f'submitted request to create warehouse {warehouse_name}')

        if shared:
            acl = [AccessControlRequest(group_name='users', permission_level=PermissionLevel.CAN_USE)]
        else:
            acl = [AccessControlRequest(user_name=principal, permission_level=PermissionLevel.CAN_MONITOR)]

        self.w.permissions.set(request_object_type='warehouses',
                               request_object_id=warehouse['id'],
                               access_control_list=acl)
        return not shared, warehouse_name, warehouse['id']

    def vector_search_endpoints_create(self, specs: List[Dict]):
        for i in specs:
            try:
                endpoint_id = self.w.vector_search_endpoints.create_endpoint(
                    name=i['name'], endpoint_type=EndpointType.STANDARD).response.id
            except NotFound:
                endpoint_id = self.w.vector_search_endpoints.get_endpoint(endpoint_name=i['name']).id
            except AlreadyExists:
                endpoint_id = self.w.vector_search_endpoints.get_endpoint(endpoint_name=i['name']).id
            try:
                self.w.permissions.update(
                    request_object_type='vector-search-endpoints',
                    request_object_id=endpoint_id,
                    access_control_list=[
                        AccessControlRequest(group_name='users', permission_level=PermissionLevel.CAN_USE)
                    ]
                )
            except Exception as e:
                self.logger.error(f'error opening permissions on vector search endpoint {i["name"]}: {str(e)}')

    def run_setup(self, parameters: dict, src_base: str, user: str = None):
        setup_notebook = self.workspace_import(
            parameters, src_base,
            dst_base=os.path.join('/Users', user or self.username),
            overwrite=not user)
        if not setup_notebook:
            self.logger.error('could not find a setup notebook')
            return
        job_parameters = {'host': self.w.config.host, 'token': self.w.config.token}
        if user:
            job_parameters['username'] = user
            task_key = f'setup-{user}'
        else:
            task_key = 'setup-workspace'
        settings = self.course_config.get('cluster_config', {})
        cluster_parameters = self._cluster_config(settings=settings, ctype=DBAcademyClusterType.JOB)
        job = self.w.jobs.create(
            name=task_key,
            tasks=[Task(
                new_cluster=ClusterSpec.from_dict(cluster_parameters),
                notebook_task=NotebookTask(notebook_path=setup_notebook, base_parameters=job_parameters),
                task_key=task_key, max_retries=1, min_retry_interval_millis=600000
            )],
            timeout_seconds=0)
        self.w.jobs.run_now(job_id=job.job_id)
        self.logger.info(f"submitted job {job.job_id} to run {setup_notebook}")

    @property
    def default_catalog(self):
        if self._default_catalog:
            return self._default_catalog
        try:
            return self.w.settings.default_namespace.get().namespace.value
        except ResourceDoesNotExist:
            pass
        return self.course_config.get('metastore_config', {}).get('default_catalog', 'dbacademy')

    def metastore_create(self):
        metastore_config = self.course_config.get('metastore_config', {})
        workspace_id = self.w.get_workspace_id()
        region = self.a.workspaces.get(workspace_id=workspace_id).aws_region

        def _find_metastore(metastore_region: str, metastore_name: str = None):
            if metastore_name:
                full_name = f'{metastore_name}-{metastore_region}'
                for m in self.a.metastores.list():
                    if m.name in [full_name, metastore_name] and m.region == metastore_region:
                        return m
            else:
                for m in self.a.metastores.list():
                    if m.region == metastore_region:
                        return m
            raise NotFound

        if metastore_config.get("unique", False):
            name = f'ws{workspace_id}'
        else:
            name = metastore_config.get('name', f'ws{workspace_id}')

        try:
            metastore = _find_metastore(region, name)
            self.logger.info(f'metastore {metastore.name} ({metastore.metastore_id}) exists; will use that one')
        except NotFound:
            metastore = None
            self.logger.info(f"metastore {name} doesn't exist; will create")

        iam_role = metastore_config.get('iam_role')

        default_metastore = _find_metastore(
            metastore_region=region,
            metastore_name=metastore_config.get('default_metastore_name'))

        if not metastore:
            storage_root = metastore_config.get('storage_root')
            if not (storage_root and iam_role):
                url_object = urlparse(default_metastore.storage_root)
                storage_root = f'{url_object.scheme}://{url_object.netloc}/metastore/{name}-root'
                iam_role = self.a.storage_credentials.get(
                    metastore_id=default_metastore.metastore_id,
                    storage_credential_name=default_metastore.storage_root_credential_name
                ).credential_info.aws_iam_role.role_arn

            metastore = self.a.metastores.create(
                metastore_info=CreateMetastore(name=f'{name}-{region}', region=region, storage_root=storage_root)
            ).metastore_info
            self.logger.info(f"created new metastore {metastore.name} (id={metastore.metastore_id})")

        owner = metastore_config.get('owner')
        if not owner:
            owner = default_metastore.owner

        update_metastore = UpdateMetastore()
        if owner:
            update_metastore.owner = owner
        if iam_role:
            update_metastore.storage_root_credential_id = self.a.storage_credentials.create(
                metastore_id=metastore.metastore_id,
                credential_info=CreateStorageCredential(
                    name=metastore.name,
                    aws_iam_role=AwsIamRoleRequest(role_arn=iam_role))
            ).credential_info.id

        update_metastore.delta_sharing_scope = UpdateMetastoreDeltaSharingScope.INTERNAL_AND_EXTERNAL
        update_metastore.delta_sharing_recipient_token_lifetime_in_seconds = 86400

        self.a.metastores.update(metastore_id=metastore.metastore_id, metastore_info=update_metastore)

        try:
            current_metastore = self.w.metastores.current().metastore_id
        except:
            current_metastore = None

        if current_metastore != metastore.metastore_id:
            self.a.metastore_assignments.create(workspace_id=workspace_id, metastore_id=metastore.metastore_id)
            if current_metastore:
                try:
                    current_metastore_summary = self.w.metastores.summary()
                    self.metastore_defer_setup = True
                    if self._warehouse:
                        self.w.warehouses.stop(self._warehouse)
                except NotFound:
                    pass

        self.logger.info(f"assigned metastore {metastore.metastore_id} to workspace {workspace_id}")

        default_catalog = metastore_config.get('default_catalog', 'dbacademy')
        setting = DefaultNamespaceSetting(namespace=StringMessage(value=default_catalog))
        try:
            self.w.settings.default_namespace.update(
                allow_missing=True, setting=setting, field_mask='namespace')
        except ResourceConflict as e:
            setting.etag = json.loads(e.args[0])["serializedCT"]
            self.w.settings.default_namespace.update(
                allow_missing=True, setting=setting, field_mask='namespace')

        self._default_catalog = default_catalog

    def metastore_setup(self):
        if self.metastore_defer_setup:
            self.logger.info('waiting 12 min TTL for metastore setup following metastore change')
            time.sleep(720)

        metastore_config = self.course_config.get('metastore_config', {})

        def _schema_set_ownerships(_w, _catalog, _schema, _owner):
            for _function in _w.functions.list(catalog_name=_catalog, schema_name=_schema):
                _w.functions.update(name=_function.full_name, owner=_owner)
            for _table in _w.tables.list(catalog_name=_catalog, schema_name=_schema):
                _w.tables.update(full_name=_table.full_name, owner=_owner)
            for _volume in _w.volumes.list(catalog_name=_catalog, schema_name=_schema):
                _w.volumes.update(name=_volume.full_name, owner=_owner)
            for _model in _w.registered_models.list(catalog_name=_catalog, schema_name=_schema):
                _w.registered_models.update(full_name=_model.full_name, owner=_owner)
            _w.schemas.update(full_name=f'{_catalog}.{_schema}', owner=_owner)

        def _catalog_set_ownerships(_w, _catalog, _owner, _recurse=False):
            if _recurse:
                for _schema in _w.schemas.list(catalog_name=_catalog):
                    if _schema.owner != 'System user':
                        _schema_set_ownerships(_w, _catalog, _schema.name, _owner)
            _w.catalogs.update(_catalog, owner=_owner)

        summary = self.w.metastores.summary()
        owner = summary.owner
        default_catalog = self.default_catalog

        try:
            self.w.catalogs.create(default_catalog)
            self.logger.info(f"created catalog {default_catalog}")
        except BadRequest:
            self.logger.info(f"catalog {default_catalog} already exists")

        try:
            self.w.schemas.create(name='ops', catalog_name=default_catalog)
        except BadRequest:
            pass

        self.sql(statement=f"""
        CREATE FUNCTION IF NOT EXISTS {default_catalog}.ops.meta_filter(owner STRING)
        RETURN IF(
          current_user() = owner OR current_user() = '{owner}',
          TRUE,
          is_account_group_member(owner) OR is_member(owner) OR is_account_group_member('{owner}')
        )
        """)

        self.sql(statement=f"""
        CREATE TABLE IF NOT EXISTS {default_catalog}.ops.meta (owner STRING, object STRING, key STRING, value STRING)
        WITH ROW FILTER {default_catalog}.ops.meta_filter ON (owner)
        """)

        self.w.grants.update(full_name=default_catalog, securable_type=SecurableType.CATALOG,
            changes=[PermissionsChange(add=[Privilege.USE_CATALOG], principal='account users')])
        self.w.grants.update(full_name=f'{default_catalog}.ops', securable_type=SecurableType.SCHEMA,
            changes=[PermissionsChange(add=[Privilege.USE_SCHEMA], principal='account users')])
        self.w.grants.update(full_name=f'{default_catalog}.ops.meta', securable_type=SecurableType.TABLE,
            changes=[PermissionsChange(add=[Privilege.SELECT], principal='account users')])

        _catalog_set_ownerships(self.w, default_catalog, owner)
        _schema_set_ownerships(self.w, default_catalog, 'ops', owner)

        if metastore_config.get('enable_create_catalog', False):
            self.w.grants.update(full_name=summary.metastore_id, securable_type=SecurableType.METASTORE,
                changes=[PermissionsChange(add=[Privilege.CREATE_CATALOG], principal='account users')])

        for s in metastore_config.get('system_schemas', []):
            try:
                self.w.api_client.do(method='PUT',
                    path=f'/api/2.1/unity-catalog/metastores/{summary.metastore_id}/systemschemas/{s}')
                self.w.grants.update(full_name=f'system.{s}', securable_type=SecurableType.SCHEMA,
                    changes=[PermissionsChange(add=[Privilege.SELECT, Privilege.USE_SCHEMA], principal='account users')])
            except Exception as e:
                self.logger.error(f'error enabling system schema {s}: {str(e)}')

        marketplace = self.course_config.get('marketplace', []).copy()
        datasets = self.course_config.get('datasets', [])

        # Marketplace/dataset installation omitted for brevity — not needed for this workshop

    def workspace_init(self):
        self.logger.info('initializing workspace')

        if self.update_config_tags:
            workspace = self.a.workspaces.get(self.w.get_workspace_id())
            self.a.workspaces.update(
                workspace_id=workspace.workspace_id,
                custom_tags=config_save_to_tags(
                    self.course_config, existing_tags=workspace.custom_tags,
                    tag_max_len=255 if workspace.cloud != 'gcp' else 63))

        self.metastore_create()

        for wh in self.w.warehouses.list():
            if wh.id != self._warehouse:
                self.logger.info(f'deleting warehouse {wh.name} ({wh.id})')
                self.w.warehouses.delete(wh.id)

        if 'course_path' in self.course_config:
            file_src = f'{self.course_config["course_path"]}/files'
            if os.path.isdir(file_src):
                self.dir_to_db(file_src)
            for f in filter(
                lambda x: x.is_file() and x.name.lower().startswith('files') and x.name.lower().endswith('.zip'),
                os.scandir(self.course_config["course_path"])
            ):
                self.zip_to_db(f.path)

        if self.course_config.get('enable_file_access', False):
            self.sql('GRANT SELECT ON ANY FILE TO users')

        if self.course_config.get('enable_dbfs', False):
            self.enable_dbfs()
            if 'course_path' in self.course_config:
                dbfs_src = f'{self.course_config["course_path"]}/dbfs'
                if os.path.isdir(dbfs_src):
                    self.dir_to_dbfs(dbfs_src)

        if self.course_config.get('enable_tokens', True):
            self.enable_tokens()

        if 'secrets' in self.course_config:
            for scope in self.course_config['secrets']:
                self.secrets_put(scope=scope, secrets=self.course_config['secrets'][scope])

        if 'cluster_policies' in self.course_config:
            self.cluster_policies_create()

        self.metastore_setup()

        setup_parms = self.course_config.get('workspace_setup', {})
        setup_base = self.course_config.get('course_path')
        if setup_parms and setup_base:
            self.run_setup(parameters=setup_parms, src_base=setup_base)

    def workspace_destroy(self):
        self.logger.info('tearing down workspace')
        try:
            metastore = self.w.metastores.summary()
        except NotFound:
            return

        if len([x for x in self.a.metastore_assignments.list(metastore.metastore_id)]) < 2:
            drop_metastore = True
        else:
            drop_metastore = False

        try:
            user_records = self.sql(f"SELECT value FROM {self.default_catalog}.ops.meta WHERE key = 'username'")
            active_users = [r[0] for r in user_records] if user_records is not None else []
        except:
            active_users = []

        if active_users:
            for user in active_users:
                user_metadata = self.user_getmetadata(user)
                self.reap_account_resources(user, user_metadata)
                if not drop_metastore:
                    self.reap_metastore_resources(user, user_metadata)

        if drop_metastore:
            self.a.metastores.delete(metastore_id=metastore.metastore_id, force=True)

    def user_getmetadata(self, principal: str, key: str = None):
        if key:
            records = self.sql(f"""
            SELECT value FROM {self.default_catalog}.ops.meta
            WHERE '{principal}' IN (owner,object) AND key='{key}'
            """)
            return records[0][0] if records else None
        records = self.sql(f"""
        SELECT key,value FROM {self.default_catalog}.ops.meta
        WHERE '{principal}' IN (owner,object)
        """)
        values = {}
        if records:
            for record in records:
                values[record[0]] = record[1]
        return values

    def user_putmetadata(self, principal: str, records_for: dict = None, records_about: dict = None):
        if records_for:
            self.sql(
                "INSERT INTO {}.ops.meta REPLACE WHERE owner='{}' AND key in ({}) VALUES {}".format(
                    self.default_catalog, principal,
                    ','.join([f"'{k}'" for k in records_for.keys()]),
                    ','.join([f"('{principal}',null,'{k}','{v}')" for k, v in records_for.items()])
                ))
        if records_about:
            self.sql(
                "INSERT INTO {}.ops.meta REPLACE WHERE owner='{}' AND object='{}' AND key in ({}) VALUES {}".format(
                    self.default_catalog, self.username, principal,
                    ','.join([f"'{k}'" for k in records_about.keys()]),
                    ','.join([f"('{self.username}','{principal}','{k}','{v}')" for k, v in records_about.items()])
                ))

    def user_clearmetadata(self, principal: str):
        self.sql(f"DELETE FROM {self.default_catalog}.ops.meta WHERE '{principal}' IN (owner,object)")

    def lab_setup(self, user: str):
        self.logger.info(f'lab_setup for user {user}')
        if 'models' in self.course_config:
            self.ml_deploy_models(self.course_config['models'])

    def user_setup(self, user: str):
        self.logger.info(f'user_setup for user {user}')

        metadata_about_user = {}
        metadata_for_user = {}
        metadata = self.user_getmetadata(user) or {}

        user_config = self.course_config.get('user_config', {})

        pseudonym = metadata.get('pseudonym')
        if not pseudonym:
            pseudonym = self._get_name(user, DBAcademyNamingScheme.RANDOM)
            self.sql(
                "INSERT INTO {}.ops.meta (owner,key,value) VALUES ('{}','pseudonym','{}')".format(
                    self.default_catalog, user, pseudonym))
            while int(self.sql(f"""
            SELECT COUNT(*) FROM {self.default_catalog}.ops.meta
            WHERE key='pseudonym' AND value='{pseudonym}'
            """)[0][0]) > 1:
                new_pseudonym = self._get_name(user, DBAcademyNamingScheme.RANDOM)
                self.sql(f"""
                UPDATE {self.default_catalog}.ops.meta
                SET value='{new_pseudonym}'
                WHERE owner='{user}' AND key='pseudonym'
                """)
                pseudonym = new_pseudonym

        metadata_for_user['username'] = user
        catalog = self.default_catalog
        schema = self.safe_name(
            self._get_name(username=user,
                           naming_scheme=user_config.get('schema', DBAcademyNamingScheme.RANDOM),
                           _random_name=pseudonym))
        user_schema = schema if schema != self.safe_name(user_config.get('schema', '')) else None

        metadata_for_user['catalog_name'] = catalog

        if schema:
            try:
                self.w.schemas.create(name=schema, catalog_name=catalog)
            except BadRequest:
                pass
            if user_schema:
                metadata_about_user['user_schema'] = f'{catalog}.{user_schema}'
                grantee = user
                privileges = [Privilege.ALL_PRIVILEGES]
            else:
                grantee = user
                privileges = [Privilege.USE_SCHEMA, Privilege.CREATE_TABLE, Privilege.CREATE_VOLUME,
                              Privilege.CREATE_FUNCTION, Privilege.CREATE_MODEL, Privilege.CREATE_MATERIALIZED_VIEW]
            self.w.grants.update(
                full_name=f'{catalog}.{schema}', securable_type=SecurableType.SCHEMA,
                changes=[PermissionsChange(add=privileges, principal=grantee)])
            metadata_for_user['schema_name'] = schema

        volume_name = self.safe_name(user)
        full_volume_name = f'{self.default_catalog}.ops.{volume_name}'
        try:
            self.w.volumes.create(catalog_name=self.default_catalog, schema_name='ops',
                                  name=volume_name, volume_type=VolumeType.MANAGED)
        except ResourceAlreadyExists:
            pass
        self.w.grants.update(full_name=full_volume_name, securable_type=SecurableType.VOLUME,
            changes=[PermissionsChange(add=[Privilege.ALL_PRIVILEGES], principal=user)])

        metadata_about_user['volume'] = full_volume_name
        metadata_for_user['paths.working_dir'] = f'/Volumes/{self.default_catalog}/ops/{volume_name}'

        if 'cluster_name' in metadata:
            self.cluster_start_or_create(principal=user, cluster_name=metadata['cluster_name'])
        else:
            info = self.cluster_start_or_create(principal=user, _random_name=pseudonym)
            if info:
                metadata_for_user['cluster_name'] = info[1]
                if info[0]:
                    metadata_about_user['user_cluster'] = info[2]

        if 'warehouse_name' in metadata:
            self.warehouse_start_or_create(principal=user, warehouse_name=metadata['warehouse_name'])
        else:
            info = self.warehouse_start_or_create(principal=user, _random_name=pseudonym)
            if info:
                metadata_for_user['warehouse_name'] = info[1]
                if info[0]:
                    metadata_about_user['user_warehouse'] = info[2]

        self.user_putmetadata(user, records_for=metadata_for_user, records_about=metadata_about_user)

        redirect_url = self.w.config.host
        if 'content' in self.course_config:
            main_notebook = self.workspace_import(
                src_parms=self.course_config['content'],
                src_base=self.course_config['course_path'],
                dst_base=f'/Users/{user}', overwrite=True, dbfs=True)
            if main_notebook:
                redirect_url = self.workspace_get_url(notebook_path=main_notebook)

        if 'entry' in self.course_config:
            redirect_url = self.workspace_get_url(path=self.course_config['entry'])

        return redirect_url

    def user_setup_resume(self, user: str):
        self.logger.info(f'user_setup_resume for user {user}')
        user_metadata = self.user_getmetadata(user)
        if not user_metadata:
            return
        if 'cluster_name' in user_metadata:
            self.cluster_start_or_create(principal=user, cluster_name=user_metadata.get('cluster_name'))
        if 'warehouse_name' in user_metadata:
            self.warehouse_start_or_create(principal=user, warehouse_name=user_metadata.get('warehouse_name'))

        redirect_url = self.w.config.host
        if 'content' in self.course_config:
            main_notebook = self.workspace_import(
                src_parms=self.course_config['content'],
                src_base=self.course_config['course_path'],
                dst_base=f'/Users/{user}', overwrite=False, dbfs=False)
            if main_notebook:
                redirect_url = self.workspace_get_url(notebook_path=main_notebook)
        if 'entry' in self.course_config:
            redirect_url = self.workspace_get_url(path=self.course_config['entry'])
        return redirect_url

    def lab_end_stop(self, user: str):
        self.logger.info(f'lab_end_stop for user {user}')
        user_metadata = self.user_getmetadata(user)
        if not user_metadata:
            return
        if 'user_cluster' in user_metadata:
            try:
                self.w.clusters.delete(user_metadata['user_cluster'])
            except InvalidParameterValue:
                pass
        if 'user_warehouse' in user_metadata:
            try:
                self.w.warehouses.stop(user_metadata['user_warehouse'])
            except InvalidParameterValue:
                pass
        for c in self.w.clusters.list():
            if c.creator_user_name == user:
                self.w.clusters.delete(c.cluster_id)
        for wh in self.w.warehouses.list():
            if wh.creator_name == user:
                self.w.warehouses.stop(wh.id)
        try:
            for a in filter(lambda x: x.creator == user, self.w.apps.list()):
                self.w.apps.stop(a.name)
        except Exception:
            pass

    def lab_end_terminate(self, user: str):
        self.logger.info(f'lab_end_terminate for user {user}')
        user_metadata = self.user_getmetadata(user)
        if not user_metadata:
            return
        self.reap_workspace_resources(user, user_metadata=user_metadata)
        self.reap_account_resources(user, user_metadata=user_metadata)
        self.reap_metastore_resources(user, user_metadata=user_metadata)

    def reap_workspace_resources(self, user: str, user_metadata: dict):
        self.logger.info(f'reaping workspace resources for user {user}')
        if 'user_cluster' in user_metadata:
            try:
                self.w.clusters.permanent_delete(user_metadata['user_cluster'])
            except InvalidParameterValue:
                pass
        for c in filter(lambda x: x.creator_user_name == user, self.w.clusters.list()):
            self.w.clusters.permanent_delete(c.cluster_id)
        if 'user_warehouse' in user_metadata:
            try:
                self.w.warehouses.delete(user_metadata['user_warehouse'])
            except InvalidParameterValue:
                pass
        for w in filter(lambda x: x.creator_name == user, self.w.warehouses.list()):
            self.w.warehouses.delete(w.id)
        if 'secrets' in user_metadata:
            try:
                self.w.secrets.delete_scope(user_metadata['secrets'])
            except ResourceDoesNotExist:
                pass
        for s in filter(lambda x: x.creator == user, self.w.serving_endpoints.list()):
            self.w.serving_endpoints.delete(s.name)
        for j in filter(lambda x: x.creator_user_name == user, self.w.jobs.list()):
            for r in self.w.jobs.list_runs(job_id=j.job_id):
                try:
                    self.w.jobs.cancel_run_and_wait(r.run_id)
                    self.w.jobs.delete_run(r.run_id)
                except:
                    pass
            self.w.jobs.delete(j.job_id)
        for p in filter(lambda x: x.creator_user_name == user, self.w.pipelines.list_pipelines()):
            self.w.pipelines.delete(p.pipeline_id)
        try:
            for a in filter(lambda x: x.creator == user, self.w.apps.list()):
                self.w.apps.delete(a.name)
        except Exception:
            pass

    def reap_metastore_resources(self, user: str, user_metadata: dict):
        self.logger.info(f'reaping metastore resources for user {user}')
        if 'user_catalog' in user_metadata:
            try:
                self.w.catalogs.delete(user_metadata['user_catalog'], force=True)
            except NotFound:
                pass
        if 'user_schema' in user_metadata:
            try:
                self.w.schemas.delete(full_name=user_metadata['user_schema'], force=True)
            except NotFound:
                pass
        if 'volume' in user_metadata:
            try:
                self.w.volumes.delete(user_metadata['volume'])
            except ResourceDoesNotExist:
                pass
        for catalog in filter(lambda c: c.owner == user, self.w.catalogs.list()):
            self.w.catalogs.update(name=catalog.name, owner=self.username)
            self.w.catalogs.delete(name=catalog.name, force=True)
        self.user_clearmetadata(user)

    def reap_account_resources(self, user: str, user_metadata: dict):
        self.logger.info(f'reaping account resources for user {user}')
        if 'iam.secondary' in user_metadata:
            self.iam_delete_secondary(name=user_metadata['iam.secondary'])

    def iam_create_secondary(self, primary: str, secondary: str):
        self.logger.info(f'creating a secondary principal named {secondary} for user {primary}')
        service_principal = None
        group = None
        try:
            try:
                group = self.a.groups.create(display_name=secondary)
            except ResourceConflict:
                group = next(filter(lambda x: x.display_name == secondary, self.a.groups.list()))
            for s in self.a.service_principals.list():
                if s.display_name == secondary:
                    service_principal = s
                    break
            else:
                service_principal = self.a.service_principals.create(display_name=secondary)
            self.a.groups.patch(
                id=group.id,
                operations=[Patch(op=PatchOp.ADD, value={"members": [{"value": service_principal.id}]})],
                schemas=[PatchSchema.URN_IETF_PARAMS_SCIM_API_MESSAGES_2_0_PATCH_OP])
            self.a.workspace_assignment.update(
                self.w.get_workspace_id(), principal_id=group.id, permissions=[WorkspacePermission.USER])
            self.secrets_put(
                principal=primary,
                secrets={'secondary_token': self.w.token_management.create_obo_token(
                    service_principal.application_id).token_value})
            return group.display_name
        except Exception as e:
            try:
                if service_principal:
                    self.a.service_principals.delete(service_principal.id)
                if group:
                    self.a.groups.delete(group.id)
            except NotFound:
                pass
            raise e

    def iam_delete_secondary(self, name: str):
        self.logger.info(f'deleting secondary principal {name}')
        for g in self.a.groups.list():
            if g.display_name == name:
                self.a.groups.delete(g.id)
                break
        for s in self.a.service_principals.list():
            if s.display_name == name:
                self.a.service_principals.delete(s.id)
                break
