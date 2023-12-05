from djongo.base import DatabaseWrapper
from djongo.operations import DatabaseOperations


class PatchedDatabaseOperations(DatabaseOperations):
    """Allows you to use djongo with classic bool field filtering like ``.filter(is_active=True)``.

    Ref. https://github.com/doableware/djongo/issues/562"""

    def conditional_expression_supported_in_where_clause(self, expression):
        return False


DatabaseWrapper.ops_class = PatchedDatabaseOperations
