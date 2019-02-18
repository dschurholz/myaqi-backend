
class ExtendedFilter(object):

    def filter_queryset(self, queryset):

        if 'extended' in self.request.query_params:
            self.serializer_class = self.extended_serializer_class

        return queryset
