class NonRelRouter:
    """A router to control if database should use primary database or non-relational one."""

    def db_for_read(self, model, *args, **kwargs):
        db = getattr(
            model._meta, 'in_db', None
        )  # use default database for models that dont have 'in_db'
        return db or 'default'

    def db_for_write(self, model, *args, **kwargs):
        db = getattr(model._meta, 'in_db', None)
        return db or 'default'

    def allow_relation(self, obj1, obj2, *args, **kwargs):
        # only allow relations within a single database
        return getattr(obj1._meta, 'in_db', None) == getattr(obj2._meta, 'in_db', None)

    def allow_syncdb(self, db, model):
        return db == getattr(model._meta, 'in_db', 'default')

    def allow_migrate(self, *args, **kwargs):
        return True
