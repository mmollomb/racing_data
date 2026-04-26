from datetime import datetime

import pytz


class Entity(dict):
    """Common functionality for racing entities"""

    def __init__(self, provider, property_cache, *args, **kwargs):
        super(Entity, self).__init__(*args, **kwargs)

        self.provider = provider
        self.property_cache = dict(property_cache) if property_cache is not None else {}

        if 'created_at' not in self:
            timestamp = datetime.now(pytz.utc)
            self['created_at'] = timestamp
            self['updated_at'] = timestamp

        for key, value in list(self.items()):
            if isinstance(value, datetime):
                try:
                    self[key] = pytz.utc.localize(value)
                except ValueError:
                    pass

    @property
    def has_expired(self):
        """Expire entities sourced from an incompatible scraper version"""

        return not self.provider.scraper.is_compatible_with(self['scraper_version'])

    def get_cached_property(self, key, source_method, *source_args, **source_kwargs):
        """Get a cached property value, or source, cache and return it if necessary"""

        if key not in self.property_cache:
            self.property_cache[key] = source_method(*source_args, **source_kwargs)

        return self.property_cache[key]
