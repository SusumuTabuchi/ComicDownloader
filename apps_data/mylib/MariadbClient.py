from ast import Raise
from signal import raise_signal
import pymysql.cursors
import toml
from logging import exception, getLogger, StreamHandler, DEBUG, INFO, WARN, Formatter

from . import Message as ms

if __name__ == "__main__":
    print(ms.TEST)

# CONF_FILE_PATH  = ""
STR_CONST = toml.load(open("const.toml"))
SELECT_QUERY_ORIGINAL = "code/query/select.sql"
INSERT_QUERY_ORIGINAL = "code/query/insert.sql"
# logger
logger = getLogger()

class MarriadbClient:
    """This class is for operating maradb.
    """
    def __init__(self, host=None, user=None, password=None, charset="utf8mb4", local_infile=0, db=None):
        # db settings
        self.host = host
        self.user = user
        self.password = password
        self.charset = charset
        self.local_infile = local_infile
        self.db = db

        # application status
        self.connection = None
        self.cursor = None

        # query result
        self.result = None

    def __del__(self):
        """finalize
        """
        try:
            self.cursor.close()
        finally:
            logger.info(STR_CONST["db"]["CursorClose"])
        try:
            self.connection.close()
        finally:
            logger.info(STR_CONST["db"]["ConnectionClose"])

    def connect(self):
        """connect to database
        """
        logger.info(STR_CONST["db"]["ConnectionStart"])
        logger.info("host: {0}. database: {1}".format(self.host, self.db))
        try:
            self.connection = pymysql.connect(
                host = self.host,
                db = self.db,
                user = self.user,
                password = self.password,
                charset = self.charset,
                cursorclass = pymysql.cursors.DictCursor,
                local_infile = self.local_infile
            )
            logger.info(STR_CONST["db"]["ConnectionSuccess"])
        except Exception as e:
            logger.error(e)
            logger.info(STR_CONST["db"]["ConnectionError"])
            self.connection = None

    def get_connection_status(self):
        return self.connection.open

    def set_cousor(self):
        """cursor setter
        """
        self.cursor = self.connection.cursor()

    def exec_query(self, query):
        """execute SQL

        Args:
            query (str): SQL sentense
        """
        # # 引数の妥当性確認
        # if mode not in ["select", "updete", "insert", "delete", "truncate"]:
        #     raise ArgumentException(mode)
        # self.logger.debug("Mode : {0}".format(mode))
        # self.start_transaction()

        logger.debug("Query : {0}".format(query))

        # execute SQL
        if not self.get_connection_status():
            self.connect()
        try:
            self.cursor.execute(query)
            self.result = self.cursor.fetchall()
        except Exception as e:
            logger.error(e)
            self.result = None
            raise e

        # self.commit()

        # return self.result is not None

    def start_transaction(self):
        self.connection.begin()

    def commit(self):
        self.connection.commit()

def create_query_select(select_columns, from_table, where_phrase=None, groupby_phrase=None, having_phrase=None, orderby_columns=None, limit_count=None, model_file_path=SELECT_QUERY_ORIGINAL):
    """SELECT SQL create.

    Args:
    select_columns (str): SELECT phrase.
    from_table (str): table name.
    where_phrase (str, optional): where phrase. Defaults to None.
    groupby_phrase (str, optional): group by phrase. Defaults to None.
    having_phrase (str, optional): having phrase. Defaults to None.
    model_file_path (str, optional): base file path. Defaults to SELECT_QUERY_ORIGINAL.

    Returns:
    str: SQL query of SELECT.
    """
    # SQLのベースファイルを読み込み
    with open(model_file_path) as mf:
        query = mf.read()

    # create query
    query = query.replace("{COLUMNS}", select_columns)
    query = query.replace("{TABLE}", from_table)
    # WHERE句
    if where_phrase is None:
        query = query.replace("{IS_WHERE}", "/*", 1) # 最初の{IS_WHERE}のみ置換
        query = query.replace("{IS_WHERE}", "*/")
    else:
        query = query.replace("{IS_WHERE}", "")
        query = query.replace("{WHERE}", where_phrase)
    # GROUPBY句
    if groupby_phrase is None:
        query = query.replace("{IS_GROUP_BY}", "/*", 1) # 最初の{IS_GROUP_BY}のみ置換
        query = query.replace("{IS_GROUP_BY}", "*/")
        # GROUPBY句がない場合はHAVING句もない
        query = query.replace("{IS_HAVING}", "/*", 1) # 最初の{IS_GROUP_BY}のみ置換
        query = query.replace("{IS_HAVING}", "*/")
    else:
        query = query.replace("{IS_GROUP_BY}", "")
        query = query.replace("{GROUP_BY}", groupby_phrase)
    # HAVING句
    if having_phrase is None:
        query = query.replace("{IS_HAVING}", "/*", 1) # 最初の{IS_GROUP_BY}のみ置換
        query = query.replace("{IS_HAVING}", "*/")
    else:
        query = query.replace("{IS_HAVING}", "")
        query = query.replace("{HAVING}", having_phrase)
    # ORDERBY句
    if orderby_columns is None:
        query = query.replace("{IS_ORDER_BY}", "/*", 1) # 最初の{IS_GROUP_BY}のみ置換
        query = query.replace("{IS_ORDER_BY}", "*/")
    else:
        query = query.replace("{IS_ORDER_BY}", "")
        query = query.replace("{ORDER_BY}", orderby_columns)
    # LIMIT句
    if limit_count is None:
        query = query.replace("{IS_LIMIT}", "/*", 1) # 最初の{IS_GROUP_BY}のみ置換
        query = query.replace("{IS_LIMIT}", "*/")
    else:
        query = query.replace("{IS_LIMIT}", "")
        query = query.replace("{LIMIT}", limit_count)

    # スペースを作成
    query = query.replace("{SPACE}", " ")
    # 不要な改行を削除
    query = query.replace("\n", "")

    return query

def create_query_insert(table, to_columns, insert_values, ignore_error=False, model_file_path=INSERT_QUERY_ORIGINAL):
    """INSERT SQL create

    Args:
        table (str): INSERT destination table
        to_columns (str): INSERT destination columns
        insert_values (str): INSERT values
        ignore_error (bool, optional): whether to ignore errors. Defaults to False.
        model_file_path (str, optional): base file path. Defaults to INSERT_QUERY_ORIGINAL.

    Returns:
        _type_: _description_
    """
    # SQLのベースファイルを読み込み
    with open(model_file_path) as mf:
        query = mf.read()
    # create query
    query = query.replace("{TABLE}", table)
    query = query.replace("{COLUMNS}", to_columns)
    query = query.replace("{VALUES}", insert_values)
    # ignore
    if ignore_error:
        query = query.replace("{IS_IGNORE}", "")
    else:
        query = query.replace("{IS_IGNORE}", "/*", 1) # 最初の{IS_GROUP_BY}のみ置換
        query = query.replace("{IS_IGNORE}", "*/")

    # スペースを作成
    query = query.replace("{SPACE}", " ")
    # 不要な改行を削除
    query = query.replace("\n", "")

    return query

def list_to_column_name(columns_list, is_single_quart=True):
    """columns create

    Args:
        columns_list (list): columns list
        is_single_quart (bool, optional): Specifies whether to enclose column names with single quotation marks. Defaults to True.

    Returns:
        str: columns phrase.
    """
    single_quart = "`" if is_single_quart else ""
    columns_str = "{0},{0}".format(single_quart).join(columns_list)
    return single_quart + columns_str + single_quart



class ArgumentException(Exception):
    """Argment Error.User error.

    Args:
        Exception (str): error message
    """
    def __init__(self, str):
        self.str = "Argument error. problematic argument:{0}".format(str)
    def __str__(self):
        return self.str
