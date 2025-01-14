class FlowsService:
    def __init__(self, client):
        self.client = client

    def _update_flows_config(self, app):
        """
        synchronize Flows channel configuration.
        """
        detail_channel = self.client.detail_channel(app.flow_object_uuid)
        flows_config = detail_channel["config"]
        flows_config["treshold"] = app.config["treshold"]

        self.client.update_config(
            data=flows_config, flow_object_uuid=app.flow_object_uuid
        )

        return True

    def update_treshold(self, app, treshold):
        app.config["treshold"] = treshold
        app.save()

        return self._update_flows_config(app)
