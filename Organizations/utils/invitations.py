import datetime
from Organizations.models import TokenInviteToCompany


def DeleteInvalidInvitationLinks():
    time_to_delete = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=7)
    tokens_to_delete = TokenInviteToCompany.objects.filter(created_at__lte=time_to_delete)
    for token in tokens_to_delete:
        token.delete()