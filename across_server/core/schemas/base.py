class PrefixMixin:

    def model_dump_with_prefix(self, prefix: str | None = None) -> dict:
        data = self.model_dump()
        data_with_prefixes = {}
        if prefix is not None:
            for key, value in data.items():
                data_with_prefixes[prefix + "_" + key] = value

        return data_with_prefixes