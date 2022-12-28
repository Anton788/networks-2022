#import pandas as pd

from Products.models import *
from Products.serializers import ProductTableSerializer

from Organizations.models import *
from Services.models import Task

import datetime

from Services.constants.download_status import (
    WAITING,
    FINISHED,
    REJECTED,
    IN_PROGRESS
)


from Services.constants.tasks import (
    CREATE_EXCEL_TABLE_FROM_PRODUCTS,
    OTHER,
)


    
# def DownloadFilteredProductsExcel(task):
    
    # data = task.data
    #
    # product_id_list = data["product_id_list"]
    # price_min = data["price_min"]
    # price_max = data["price_max"]
    # condition = data["condition"]
    # company = Company.objects.get(id=data["company_id"])
    # factory_id_list = data["factory_id_list"]
    # factory_producer = data["factory_producer"]
    # company_producer = data["company_producer"]
    #
    # filename = get_random_string(15) + ".xlsx"
    # df = pd.DataFrame()
    #
    # products = Product.objects.filter(company=company,
    #                                   price__range=[price_min, price_max],
    #                                   )
    #
    # if condition:
    #     products = products.filter(condition__in=condition)
    #
    # if factory_id_list:
    #     products = products.filter(factory__in=factory_id_list)
    #
    # if product_id_list:
    #     products = products.filter(id__in=product_id_list)
    #
    # if factory_producer:
    #     products = products.filter(factory_producer__in=factory_producer)
    #
    # if company_producer:
    #     products = products.filter(company_producer__in=company_producer)
    #
    # for product in products:
    #     data = ProductTableSerializer(product).data
    #     df = df.append(data, ignore_index=True)
    #
    #
    #
    # df.to_excel(filename, encoding='UTF-8')
    # excel_file = ProductTable.objects.create(link="-")
    # with open(filename, 'rb',
    #           ) as file:
    #     link = add_file_to_storage(file, excel_file.id, is_image=False)
    #     excel_file.link = link
    #     excel_file.save()
    # os.remove(filename)
    # return link


# def DownloadProductExcelsFromQueue():
    # tasks = Task.objects.filter(task_type=CREATE_EXCEL_TABLE_FROM_PRODUCTS,
    #                             status=WAITING)
    # tasks = tasks[:50]
    #
    # for task in tasks:
    #     task.started_at = datetime.datetime.now()
    #     task.status = IN_PROGRESS
    #     task.save()
    # links = []
    # for count, task in enumerate(tasks):
    #     link = DownloadFilteredProductsExcel(task)
    #     links.append(link)
    #     task.status = FINISHED
    #     task.finished_at = datetime.datetime.now()
    #     task.save()
    #     if not (count + 1) % 10:
    #         for i in range(count+1, len(tasks)):
    #             new_task = tasks[i]
    #             new_task.started_at = datetime.datetime.now()
    #             new_task.save()
    #
    # time_to_remake_task = datetime.datetime.now()-datetime.timedelta(hours=1)
    # tasks_back_to_waiting = Task.objects.filter(task_type=CREATE_EXCEL_TABLE_FROM_PRODUCTS,
    #                                             status=IN_PROGRESS,
    #                                             started_at__lte=time_to_remake_task)
    # for task in tasks_back_to_waiting:
    #     task.status = WAITING
    #     task.started_at = None
    #     task.save()
    #
    # tasks_rejected = Task.objects.filter(task_type=CREATE_EXCEL_TABLE_FROM_PRODUCTS,
    #                                     status=REJECTED)
    #
    # for task in tasks_rejected:
    #     task.status = WAITING
    #     task.started_at = None
    #     task.save()
    #
    # return links
