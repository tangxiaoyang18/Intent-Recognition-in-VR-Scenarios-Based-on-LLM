import time

from openai import OpenAI
client = OpenAI()

print(time.time())
completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "你是VR场景下的智能代理，需要你帮忙完成VR场景中用户的交互意图识别任务，我会提供给你分析出来的用户注视信息、手部信息和手势信息，你需要从中分析用户最有可能的交互意图。"},
    {"role": "user", "content": "注视信息："
                                "用户从注视Milk Bottle变为注视Milk Cup"
                                "手部信息："
                                "左手没有明显移动。"
                                "右手有明显移动，主要方向是Y轴（上下）方向。"
                                "左手没有明显旋转。"
                                "右手有明显旋转。"
                                "左手与头部的距离没有明显变化。"
                                "右手与头部的距离没有明显变化。"
                                "左手与右手的距离没有明显变化。"
                                "手势信息："
                                "左手的整体手势变化为：一直保持半握手势。"
                                "右手的整体手势变化为：从半握手势先变为张开手势再变为半握手势。"
                                "请分析用户最有可能的三种交互意图，按可能性排序"}
  ]
)

print(completion.choices[0].message)

print(time.time())
