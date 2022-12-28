from Organizations.models import OrganizationsRelationship
import Organizations.constants.organizations_relationship_type as ORGANIZATIONS_RELATIONSHIP_TYPE


def get_potential_relationships_for_company(company):
    return OrganizationsRelationship.objects.filter(
        company_2=company,
        company_1_confirmed=True,
        company_2_confirmed__isnull=True,
        relationship_type=ORGANIZATIONS_RELATIONSHIP_TYPE.PARTNERSHIP
    )
