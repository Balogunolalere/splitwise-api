from deta import Deta
from config import settings

deta = Deta(settings.SPLITWISE_PROJECT_KEY)

users_db = deta.Base("splitwise_users")
groups_db = deta.Base("splitwise_groups")
expenses_db = deta.Base("splitwise_expenses")