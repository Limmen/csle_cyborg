from CybORG.main import Main
import inspect
from CybORG.Agents.SimpleAgents.B_line import B_lineAgent
from CybORG.Agents.SimpleAgents.KeyboardAgent import KeyboardAgent
from CybORG.Agents.Wrappers.TrueTableWrapper import TrueTableWrapper

if __name__ == "__main__":
    print("Setup")
    path = str(inspect.getfile(Main))
    path = path[:-10] + '/Shared/Scenarios/Scenario1b.yaml'

    cyborg = TrueTableWrapper(env=Main(path, 'sim', agents={'Red': B_lineAgent}), observer_mode=False)
    agent_name = 'Blue'

    results = cyborg.reset(agent=agent_name)
    observation = results.observation
    action_space = results.action_space

    agent = KeyboardAgent()

    reward = 0
    done = False
    while True:
        action = agent.get_action(observation, action_space)
        results = cyborg.step(agent=agent_name, action=action)
        red_action = cyborg.get_last_action(agent='Red')
        print(red_action)

        reward += results.reward
        observation = results.observation
        action_space = results.action_space
        if done:
            print(f"Game Over. Total reward: {reward}")
            break
