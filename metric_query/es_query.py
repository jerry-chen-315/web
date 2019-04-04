import elasticsearch
from collections import OrderedDict
import copy
from . import conn_mysql



def get_data(start_time,
            end_time,
            query_type,
            metric_name,
            host_set
            ):
    es = elasticsearch.Elasticsearch(['162.12.0.234', '162.12.0.233'])
    keyorder = ['host_name', 'ipaddress', 'query_type', 'date_range', 'cpu_avg', 'cpu_max', 'mem_avg', 'mem_max']
    # res_dict = OrderedDict()
    res_dict = {}
    res_dict['0'] = {'host_name': '主机名称', 'ipaddress': 'IP地址', \
                     'query_type': '查询类型', 'date_range': '时间取值范围', \
                     'cpu_avg': 'CPU平均值', 'cpu_max': 'CPU最大值', \
                     'mem_avg': '内存平均值', 'mem_max': '内存最大值' \
                     }
    if metric_name == "cpu":
        field_name = "check_cpu.cpu_usage"
        aggs_str = """
                {"cpu_avg":{"avg":{"field":"check_cpu.cpu_usage"}},
                 "cpu_max":{"max":{"field":"check_cpu.cpu_usage"}}
                }
                """

    elif metric_name == "mem":
        aggs_str = """
                {"mem_avg":{"avg":{"field":"check_memory.MUsedPrc"}},
                 "mem_max":{"max":{"field":"check_memory.MUsedPrc"}}
                }
                """
    elif metric_name == "all":
        aggs_str = """
                {
                 "cpu_avg":{"avg":{"field":"check_cpu.cpu_usage"}},
                 "cpu_max":{"max":{"field":"check_cpu.cpu_usage"}},
                 "mem_avg":{"avg":{"field":"check_memory.MUsedPrc"}},
                 "mem_max":{"max":{"field":"check_memory.MUsedPrc"}}
                }
                """
    i = 1
    for item in host_set:
        host_name = item[0]
        ipaddr = item[1]
        query_body = ("""
                        { 
                         "size":0,
                         "aggs":%s,
                         "docvalue_fields":["@timestamp"],
                         "query":{"bool":{"must":[{"query_string":{"query":"ipaddr.keyword:%s",
                                                                   "analyze_wildcard":true,"default_field":"*"}
                                                   },
                                                  {"range":{"@timestamp":{"gte":"%s","lte":"%s"}}}
                                                 ]
                                         }
                                  }
                         }
                         """ % (aggs_str, ipaddr, start_time, end_time))
        res = es.search(index="nagios-perf-*", body=query_body)
        row_dict = {}
        for k,v in res['aggregations'].items():
            if v['value'] == None:
                row_dict[k] = 'None'
            else:
                row_dict[k] = round(v['value'], 2)
        row_dict['host_name'] = host_name
        row_dict['ipaddress'] = ipaddr
        row_dict['query_type'] = query_type
        row_dict['date_range'] = ('%s to %s' % (start_time[:10], end_time[:10]))
        if metric_name == 'cpu':
            row_dict['mem_avg'] = 'N/A'
            row_dict['mem_max'] = 'N/A'
        elif metric_name == 'mem':
            row_dict['cpu_avg'] = 'N/A'
            row_dict['cpu_max'] = 'N/A'
        print (row_dict)
        res_dict[i] = dict(sorted(row_dict.items(), key=lambda i:keyorder.index(i[0])))
        i += 1
    res_web = copy.deepcopy(res_dict)
    del res_dict['0']
    # print (res_dict)
    conn_mysql.write_to_mysql(res_dict, metric_name)

    return res_web