"""Connection classes."""

from netsquid.components.cchannel import ClassicalChannel
from netsquid.components.models import FibreDelayModel
from netsquid.nodes import DirectConnection


class ClassicalConnection(DirectConnection):
    def __init__(self, name="ClassicalConnection", **properties):
        super().__init__(
            name=name,
            channel_AtoB=ClassicalChannel(
                name="AtoB",
                models={"delay_model": FibreDelayModel()},
                **properties,
            ),
            channel_BtoA=ClassicalChannel(
                name="BtoA",
                models={"delay_model": FibreDelayModel()},
                **properties,
            ),
        )
