from datetime import datetime
from connect_db.connect import connect_db
from module.tbmt import Tbmt
from zullip_module import zullip_code as zc
from logger import get_app_logger


def table_to_send(tbmts: list[Tbmt]) -> str:
    msg = f'''
    Thông tin Thầu - Ngày {datetime.now().date()}:

    | Số TBMT | BP | Mã NV thực hiện | Mã KH | Tên KH | Tên gói thầu | Loại hình thầu | Ngày đóng thầu |
    |-------|-------|:----------:|:-----------:|---------------------|-------------------|---------|:------:|
    '''
    for t in tbmts:
        tb: Tbmt = Tbmt(*t)
        msg += tb.to_table()
    return msg


def task_to_send(tbmts: list[Tbmt]) -> str:
    msg_task = f'''
    /todo Thông báo thầu đến hạn - Ngày {datetime.strftime(datetime.now().date(), "%d-%m-%Y")}
    '''
    for t in tbmts:
        tb: Tbmt = Tbmt(*t)
        msg_task += tb.to_task()
    return msg_task


def send_tbmt_zullip():
    logger = get_app_logger()
    conn = connect_db()
    cursor = conn.cursor()

    sql_query = '''
        SET NOCOUNT ON
        {CALL GETDL_TBMT_Zulip}
    '''
    cursor.execute(sql_query)
    tbmts: list[Tbmt] = cursor.fetchall()
    if len(tbmts) > 0:
        msg_task = task_to_send(tbmts)
        result = zc.send_msg(msg_task, 1974)
        logger.info(result)
    else:
        logger.info("No more TBMT to send today.")


if __name__ == '__main__':
    send_tbmt_zullip()
