from collections import deque
from skimage import color, transform
import gym
import torch


def _state_to_tensor(state):
  gray_img = color.rgb2gray(state)  # TODO: Check image conversion doesn't cause problems
  downsized_img = transform.resize(gray_img, (84, 84), mode='constant')  # TODO: Check resizing doesn't cause problems
  return torch.from_numpy(downsized_img).float()  # Return 2D image tensor


class Env():
  def __init__(self, args):
    super().__init__()
    self.env = gym.make(args.game + 'Deterministic-v4')
    self.window = 4  # Number of frames to concatenate
    self.buffer = deque([], maxlen=self.window)
    self.t = 0  # Internal step counter
    self.T = args.max_episode_length

  def _reset_buffer(self):
    for t in range(self.window):
      self.buffer.append(torch.zeros(84, 84))

  def reset(self):
    # Reset internals
    self.t = 0
    self._reset_buffer()
    # Process and return initial state
    observation = self.env.reset()
    observation = _state_to_tensor(observation)
    self.buffer.append(observation)
    return torch.stack(self.buffer, 0)

  def step(self, action):
    # Process state
    observation, reward, done, _ = self.env.step(action)
    observation = _state_to_tensor(observation)
    self.buffer.append(observation)
    # Time out episode if necessary
    self.t += 1
    if self.t == self.T:
      done = True
    # Return state, reward, done
    return torch.stack(self.buffer, 0), reward, done

  def seed(self, seed):
    self.env.seed(seed)

  def render(self):
    self.env.render()

  def close(self):
    self.env.close()
