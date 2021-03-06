class AuthRouter:
    """
    A router to control all database operations on models in the
    auth application.
    """
    auth_apps = ['auth', 'accounts']

    def db_for_read(self, model, **hints):
        """
        Attempts to read auth models go to auth_db.
        """
        if model._meta.app_label in self.auth_apps:
            return 'default'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth models go to auth_db.
        """
        if model._meta.app_label in self.auth_apps:
            return 'default'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth app is involved.
        """
        if obj1._meta.app_label in self.auth_apps or \
                obj2._meta.app_label in self.auth_apps:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the auth app only appears in the 'auth_db'
        database.
        """
        if app_label == 'auth':
            return db == 'default'
        return None


class EPADataRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'au_epa_data':
            return 'au_epa_aqi'
        if model._meta.app_label == 'epa_data':
            return 'default'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'au_epa_data':
            return 'au_epa_aqi'
        if model._meta.app_label == 'epa_data':
            return 'default'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the common app is involved.
        """
        if (obj1._meta.app_label == 'au_epa_data' and
                obj2._meta.app_label == 'common') or (
                obj2._meta.app_label == 'au_epa_data' and
                obj1._meta.app_label == 'common'):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'au_epa_data':
            return db == 'au_epa_aqi'
        if app_label == 'epa_data':
            return db == 'default'
        return None


class CommonDataRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'common':
            return 'default'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'common':
            return 'default'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the common app is involved.
        """
        if obj1._meta.app_label == 'common' or \
                obj2._meta.app_label == 'common':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'common':
            return db == 'default'
        return None


class GeoDataRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'geo_data':
            return 'geo_data'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'geo_data':
            return 'geo_data'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the geo_data app is involved.
        """
        if obj1._meta.app_label == 'geo_data' or \
                obj2._meta.app_label == 'geo_data':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'geo_data':
            return db == 'geo_data'
        return None
