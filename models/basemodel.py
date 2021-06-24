import dbaccess.sqlengine

class ORMBase():
    def save(self, commit=True):
        self.before_save()
        session = dbaccess.sqlengine.get_session()
        session.add(self)
        if commit:
            try:
                session.commit()
            except Exception as e:
                session.rollback()
                raise e
            finally:                              #
                session.close()         
        self.after_save()


    def before_save(self, *args, **kwargs):
        pass

    def after_save(self, *args, **kwargs):
        pass

    def before_update(self, *args, **kwargs):
        pass

    def after_update(self, *args, **kwargs):
        pass

    def update(self, *args, **kwargs):
        self.before_update(*args, **kwargs)
        session = dbaccess.sqlengine.get_session()
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:                              #
            session.close()   
        self.after_update(*args, **kwargs)


    def delete(self, commit=True):
        session = dbaccess.sqlengine.get_session()
        session.delete(self)
        if commit:
            try:
                session.commit()
            except Exception as e:
                session.rollback()
                raise e
            finally:                              #
                session.close()