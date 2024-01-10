from random import choice
from CybORG.Shared.Observation import Observation
from CybORG.Shared.Actions.Action import Action
from CybORG.Shared.Enums import DecoyType
from CybORG.Simulator.Host import Host
from CybORG.Simulator.Session import Session
from CybORG.Simulator.State import State
from CybORG.Shared.Actions.AbstractActions.Misinform import Decoy, DecoyFactory, _is_host_using_port


class SSHDDecoyFactory(DecoyFactory):
    """
    Assembles process information to appear as an ssh server
    """
    def make_decoy(self, host: Host) -> Decoy:
        del host
        return Decoy(service_name="sshd", name="Sshd.exe",
                open_ports=[{'local_port':22, 'local_address':'0.0.0.0'}],
                process_type="sshd",
                process_path="C:\\Program Files\\OpenSSH\\usr\\sbin")

    def is_host_compatible(self, host: Host) -> bool:
        return not _is_host_using_port(host, 22)
sshd_decoy_factory = SSHDDecoyFactory()

class DecoySSHD(Action):
    """
    Creates a misleading process on the designated host depending on
    available and compatible options.
    """
    def __init__(self, *, session: int, agent: str, hostname: str):
        self.agent = agent
        self.session = session
        self.hostname = hostname
        self.decoy_type = DecoyType.EXPLOIT
        self.candidate_decoys = (sshd_decoy_factory,)

    def emu_execute(self) -> Observation:
        raise NotImplementedError

    def sim_execute(self, state: State) -> Observation:
        obs_fail = Observation(False)
        obs_succeed = Observation(True)

        sessions = [s for s in state.sessions[self.agent].values() if
                s.host == self.hostname]
        if len(sessions) == 0:
            return obs_fail

        session = choice(sessions)
        host = state.hosts[self.hostname]

        try:
            decoy_factory = self.__select_one_factory(host)
            decoy = decoy_factory.make_decoy(host)
            self.__create_process(obs_succeed, session, host, decoy)
            #print ("Misinform Success. Result: {}".format(result))

            return obs_succeed

        except RuntimeError:
            #print ("Misinform FAILURE")
            return obs_fail


    def __select_one_factory(self, host: Host) -> DecoyFactory:
        """
        Examines all decoy factories and returns one randomly compatible one.
        Raises RuntimeError if no compatible ones are found.
        """

        compatible_factories = [factory for factory in self.candidate_decoys
                if factory.is_host_compatible(host) ]

        if len(compatible_factories) == 0:
            raise RuntimeError("No compatible factory")

        return choice(list(compatible_factories))

    def __create_process(self, obs: Observation, sess: Session, host: Host,
            decoy: Decoy) -> None:
        """
        Creates a process & service from Decoy on current host, adds it
        to the observation.
        """

        parent_pid = 1

        process_name = decoy.name
        username = sess.username
        version = decoy.version
        open_ports = decoy.open_ports
        process_type = decoy.process_type
        process_props = decoy.properties

        service_name = decoy.service_name

        new_proc = host.add_process(name=process_name, ppid=parent_pid,
                user=username, version=version, process_type=process_type,
                open_ports=open_ports, decoy_type=self.decoy_type,
                properties=process_props)

        host.add_service(service_name=service_name, process=new_proc.pid,
                session=sess)

        obs.add_process(hostid=self.hostname, pid=new_proc.pid,
                parent_pid=parent_pid, name=process_name,
                username=username, service_name=service_name,
                properties=process_props)

    def __str__(self):
        return f"{self.__class__.__name__} {self.hostname}"
