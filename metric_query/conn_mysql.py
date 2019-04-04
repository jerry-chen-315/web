#-*-coding:utf-8-*-
import datetime
import mysql.connector

def write_to_mysql(res_dict, metric_name):
    try:
        conn = mysql.connector.connect(user="ch", password="chenh@123", host="127.0.0.1", database="mymetric")
        cursor = conn.cursor()
        check_time = datetime.datetime.now()
        add_metric_result = ("insert into stats_hist(host_name, ipaddress, date_range, query_type, "
                             "cpu_avg, cpu_max, mem_avg, mem_max) values"
                             "(%(host_name)s, %(ipaddress)s, %(date_range)s, %(query_type)s, "
                             "%(cpu_avg)s, %(cpu_max)s, %(mem_avg)s, %(mem_max)s)")
        for row in res_dict.values():
            if row['ipaddress'] == None:
                continue
            cursor.execute(add_metric_result, row)
        conn.commit()
        cursor.close()
        conn.close()

        return
    except Exception as err:
        print (err)
