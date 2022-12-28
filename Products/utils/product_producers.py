from rest_framework import status
from rest_framework.response import Response

from Organizations.models import Factory, CompanyProducer, FactoryProducer, Company


def create_factory_producer(company_id, name):
    if company_id is None:
        return Response(status=status.HTTP_400_BAD_REQUEST,
                        data="Завод должен принадлежать компании.")
    company_prod = CompanyProducer.objects.get(id=company_id)
    if company_prod.company is not None:
        if name is not None and name != "":
            factory = Factory.objects.filter(name=name, company=company_prod.company)

            if factory.exists():
                factory_prod, _ = FactoryProducer.objects.get_or_create(name=factory.first().name,
                                                                        factory=factory.first(),
                                                                        company_producer=company_prod)
            else:
                factory_prod, _ = FactoryProducer.objects.get_or_create(name=name, company_producer=company_prod)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data="Введите название завода")
    else:
        if name is not None and name != "":
            factory_prod, _ = FactoryProducer.objects.get_or_create(name=name, company_producer=company_prod)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data="Введите название завода")
    return Response(status=status.HTTP_200_OK,
                    data={"id": factory_prod.id})


def create_company_producer(inn, company_text):
    if inn is not None and inn != "":
        company_inn = Company.objects.filter(inn=inn)

        if company_inn.exists():
            if company_text is not None and company_text != "":
                if company_inn.first().name != company_text:
                    return Response(status=status.HTTP_400_BAD_REQUEST,
                                    data="Неверное имя компании.")
            company_prod, _ = CompanyProducer.objects.get_or_create(name=company_inn.first().name,
                                                                    company=company_inn[0], inn=inn)
        else:
            if company_text is not None and company_text != "":
                company_prod, _ = CompanyProducer.objects.get_or_create(name=company_text, inn=inn)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data="Неверное имя компании.")
    else:
        if company_text is not None and company_text != "":
            company_prod, _ = CompanyProducer.objects.get_or_create(name=company_text)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data="Неверное имя компании.")
    return Response(data={"id": company_prod.id})