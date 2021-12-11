from tethysapp.hydraulic_structures.services.upload.upload_resource_workflow import UploadResourceWorkflow


class UploadCropWatWorkflow(UploadResourceWorkflow):

    def get_jobs(self):
        """
        Get CondorWorkflowJobNodes and the corresponding status key.

        Returns:
            list: A list of 2 tuples in the format [(CondorWorkflowJobNodes, 'status_key'), ...]
        """
        upload_extent_layer = self.generate_extent_layer_job(
            job_name='create_model_extent_layer',
            status_key=self.UPLOAD_EXTENT_LAYER_STATUS_KEY,
        )

        return [(upload_extent_layer, self.UPLOAD_EXTENT_LAYER_STATUS_KEY)]
