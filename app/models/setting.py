from app.extensions import db

class Setting(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)
    description = db.Column(db.String(255), nullable=True)

    _cache = {}

    @staticmethod
    def get_val(key, default=None):
        if key in Setting._cache:
            return Setting._cache[key]
        setting = Setting.query.filter_by(key=key).first()
        val = setting.value if setting else default
        Setting._cache[key] = val
        return val

    @staticmethod
    def set_val(key, value):
        Setting._cache[key] = value
        setting = Setting.query.filter_by(key=key).first()
        if setting:
            setting.value = value
        else:
            setting = Setting(key=key, value=value)
            db.session.add(setting)
        db.session.commit()

    def __repr__(self):
        return f'<Setting {self.key}: {self.value}>'
