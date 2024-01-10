# Copyright DST Group. Licensed under the MIT license.
import time
from cyborg.shared.Observation import Observation
from cyborg.shared.Enums import QueryType
from .VelociraptorAction import VelociraptorAction


class VelociraptorSleep(VelociraptorAction):

    def __init__(self, session: int, agent: str, t: int = 1):
        super().__init__(session=session,
                         agent=agent,
                         query_type=QueryType.SYNC,
                         poll_alerts=False)
        self.t = t

    def emu_execute(self,
                    session_handler,
                    *args,
                    **kwargs):
        time.sleep(self.t)
        obs = Observation()
        obs.set_success(True)
        obs.add_raw_obs(f"I slept {self.t} secs")
        return obs