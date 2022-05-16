from django.shortcuts import reverse

from tethysext.atcore.controllers.resources.tabs import ResourceListTab


class ProjectAreaHealthInfrastructuresTab(ResourceListTab):
    template_name = 'hydraulic_structures/resources/tabs/hydraulic_structures_resource_list_tab.html'

    def get_resources(self, request, resource, session, *args, **kwargs):
        """
        Get a list of resources

        Returns:
            A list of Resources.
        """
        return resource.health_infrastructures

    def get_href_for_resource(self, app_namespace, resource):
        return reverse(f'{app_namespace}:health_infrastructure_details_tab', args=[resource.id, 'summary'])
