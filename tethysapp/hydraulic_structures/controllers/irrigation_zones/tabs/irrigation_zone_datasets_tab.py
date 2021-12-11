from django.shortcuts import reverse

from tethysext.atcore.controllers.resources.tabs import ResourceListTab


class IrrigationZoneDatasetsTab(ResourceListTab):

    def get_resources(self, request, resource, session, *args, **kwargs):
        """
        Get a list of resources

        Returns:
            A list of Resources.
        """
        return resource.datasets

    def get_href_for_resource(self, app_namespace, resource):
        return reverse(f'{app_namespace}:dataset_details_tab', args=[resource.id, 'summary'])
