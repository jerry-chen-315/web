# -*- coding:utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render
from . import es_query
# Create your views here.

def index(request):
    # request HttpResponse()
    if request.method == 'POST':
        #print (request.GET['metric_name'])
        print (request)
        print (request.POST)
        mydict = {}
        if request.POST['query_type'] == 'single':
            # print (type(request.POST['ipaddress']))
            # print (type(request.POST['metric_name']))
            # print (type(request.POST['start_time']))
            # print (type(request.POST['end_time']))
            query_type = 'single'
            start_time = request.POST['start_time'] + 'T00:00:00'
            end_time = request.POST['end_time'] + 'T23:59:59'
            metric_name = request.POST['metric_name']
            ipaddress = request.POST['ipaddress']
            host_name = 'server'
            host_set = {('server', ipaddress)}
            res_dict = es_query.get_data(start_time, end_time, query_type, metric_name, host_set)
            mydict['res'] = res_dict
        else:
            query_type = 'batch'
            start_time = request.POST['start_time'] + 'T00:00:00'
            end_time = request.POST['end_time'] + 'T23:59:59'
            metric_name = request.POST['metric_name']
            myfile = request.FILES['hostname_ip']
            raw = str(myfile.read())[1:].replace('\'','')
            msg = raw.split('\\r\\n')
            lines = []
            for line in msg:
                lines.append(tuple(line.split(';')))
            host_set = set(lines)
            res_dict = es_query.get_data(start_time, end_time, query_type, metric_name, host_set)
            mydict['res'] = res_dict
        return render(request, 'index.html', mydict)
    else:
        print(request)
        return render(request, 'index.html')

    # return render(request, 'index.html', mydict)


