from Documents.constants.storage import MAX_FILE_SIZE
from Organizations.models import OrganizationsRelationshipFile, OrganizationsRelationship
from Documents.utils.storage import add_file_to_storage


def add_file_to_relation(file, relation: OrganizationsRelationship, name: str = None, description: str = ""):


    if file.size > MAX_FILE_SIZE:
        raise ValueError(f"Размер файла не может быть более {MAX_FILE_SIZE // (1024 * 1024)}МБ")

    relation_file = OrganizationsRelationshipFile.objects.create(
        link="-",
        relation=relation,
        name=file.name[:50] if name is None else name[:50],
        description=description
    )

    link = add_file_to_storage(file, relation_file.id, is_image=False)
    relation_file.link = link
    relation_file.save()

    return relation_file




'''def add_file_to_company(file, company: Company, name: str = None, description: str = ""):

    if file.size > MAX_FILE_SIZE:
        raise ValueError(f"Размер файла не может быть более {MAX_FILE_SIZE // (1024 * 1024)}МБ")

    company_file = CompanyFile.objects.create(
        link="-",
        company=company,
        name=file.name[:50] if name is None else name[:50],
        description=description
    )

    link = add_file_to_storage(file, company_file.id, is_image=False)
    company_file.link = link
    company_file.save()

    return company_file'''



