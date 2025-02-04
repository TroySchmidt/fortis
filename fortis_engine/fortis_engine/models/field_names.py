class FieldNames:
    def __init__(self, defaults=None):
        if defaults is None:
            self._names = {}  # Start with an empty dictionary
        else:
            self._names = defaults.copy() # Copy the defaults to avoid modifying the original

    def __getattr__(self, name):
        if name in self._names:
            return self._names[name]
        else:
            # Return the name itself as the default if not overridden
            return name  # Or raise an AttributeError if you prefer strict checking

    def set(self, name, value):
        self._names[name] = value