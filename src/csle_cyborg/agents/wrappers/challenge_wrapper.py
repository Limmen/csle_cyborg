from gymnasium import Env
from csle_cyborg.agents.wrappers.base_wrapper import BaseWrapper
from csle_cyborg.agents.wrappers.open_ai_gym_wrapper import OpenAIGymWrapper
from csle_cyborg.agents.wrappers.blue_table_wrapper import BlueTableWrapper
from csle_cyborg.agents.wrappers.red_table_wrapper import RedTableWrapper
from csle_cyborg.agents.wrappers.enum_action_wrapper import EnumActionWrapper


class ChallengeWrapper(Env,BaseWrapper):
    def __init__(self, agent_name: str, env, agent=None,
            reward_threshold=None, max_steps = None):
        super().__init__(env, agent)
        self.agent_name = agent_name
        if agent_name.lower() == 'red':
            table_wrapper = RedTableWrapper
        elif agent_name.lower() == 'blue':
            table_wrapper = BlueTableWrapper
        else:
            raise ValueError('Invalid Agent Name')

        env = table_wrapper(env, output_mode='vector')
        env = EnumActionWrapper(env)
        env = OpenAIGymWrapper(agent_name=agent_name, env=env)

        self.env = env
        self.action_space = self.env.action_space
        self.observation_space = self.env.observation_space
        self.reward_threshold = reward_threshold
        self.max_steps = max_steps
        self.step_counter = None
        self.possible_actions = env.possible_actions

    def step(self,action=None):
        obs, reward, done, info = self.env.step(action=action)
        
        self.step_counter += 1
        if self.max_steps is not None and self.step_counter >= self.max_steps:
            done = True

        return obs, reward, done, info, info

    def reset(self):
        self.step_counter = 0
        return self.env.reset(), {}

    def get_attr(self,attribute:str):
        return self.env.get_attr(attribute)

    def get_observation(self, agent: str):
        return self.env.get_observation(agent)

    def get_agent_state(self,agent:str):
        return self.env.get_agent_state(agent)

    def get_action_space(self, agent=None) -> dict:
        return self.env.get_action_space(self.agent_name)

    def get_last_action(self,agent):
        return self.get_attr('get_last_action')(agent)

    def get_ip_map(self):
        return self.get_attr('get_ip_map')()

    def get_rewards(self):
        return self.get_attr('get_rewards')()

    def get_reward_breakdown(self, agent: str):
        return self.get_attr('get_reward_breakdown')(agent)

