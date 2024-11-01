from datetime import datetime
import json

from kafka import KafkaConsumer, TopicPartition, OffsetAndMetadata
from connect_db.connect import connect_db
from module.tbmt import Tbmt
from zullip_module import zullip_code as zc
from logger import get_app_logger

def getdecode(obj):
    if obj is None:
        return None
    else:
        return json.loads(obj.decode('utf-8'))

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
        result = zc.send_msg_group(msg_task, 1974)
        logger.info(result)
    else:
        logger.info("No more TBMT to send today.")

def kafka_consumer():
    logger = get_app_logger()
    conn = connect_db()
    cursor = conn.cursor()
    bootstrap_server = 'localhost:9092'
    topic = 'notify.SKMT_App.dbo.notify_zullip'
    # To consume latest messages and auto-commit offsets
    consumer = KafkaConsumer(
                            topic,
                            client_id='zullip-local',
                            group_id='zullip-consumer',
                            bootstrap_servers=bootstrap_server,
                            auto_offset_reset='latest',
                            value_deserializer=lambda m: getdecode(m),
                            enable_auto_commit=False
                            )
    try:
        for message in consumer:
            tp = TopicPartition(message.topic, message.partition)
            om = OffsetAndMetadata(message.offset+1, message.timestamp)
            msg_before = message.value['payload']['before'] 
            msg = message.value['payload']['after']
            logger.info(f"Before: {msg_before}")
            logger.info(f"After: {msg}")
            if msg['status'] != '1':
                if msg['gc_td1'] != None & msg['gc_td1'] != '':
                    sql_query = msg['gc_td1']
                    cursor.execute(sql_query)
                    tbmts: list[Tbmt] = cursor.fetchall()
                    if len(tbmts) > 0:
                        msg_task = task_to_send(tbmts)
                else:
                    msg_task = msg['content']
                if msg['group_yn'] != 1:
                    result = zc.send_msg_private(msg_task, int(msg['to_person']))
                else:
                    result = zc.send_msg_group(msg_task, int(msg['to_person']))
                if result['result'] == 'success':
                    sql_query = 'update notify_zullip set datetime2 = getdate(), status = 1 where id = ' + str(msg['id'])
                    cursor.execute(sql_query)
                    conn.commit()
                logger.info(f"Result: {result}")
            consumer.commit({tp:om})
    except Exception as e:
        consumer.commit({tp:om})
        conn.rollback()
        logger.error(f"ERROR: {e}")
    conn.close()

if __name__ == '__main__':
    kafka_consumer()
