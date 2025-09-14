from zhipuai import ZhipuAI
import ast
import json

from zhipuai import ZhipuAI
from PromptTemplate import gaze_prompt, hand_prompt, finger_prompt
from PromptTemplate import gaze_data, hand_data, finger_data
from PromptTemplate import intention_prompt_begin, intention_prompt_end
from PromptTemplate import operation_prompt_begin, operation_prompt_end


def extract_substring(s):
    # 找到第一个 '{' 的位置
    start = s.find('{')

    # 找到最后一个 '}' 的位置
    end = s.rfind('}')

    # 如果都找到，截取子字符串
    if start != -1 and end != -1 and start < end:
        return s[start:end + 1]
    else:
        return "{\"type\": 0}"


client = ZhipuAI(api_key="24e679f739a277277ed1832e688d1542.w6tIOQJClCCBzpIM")

# data = "{'intention': '打开Lamp', 'objects_info': [{'name': 'Lamp', 'position': {'x': 0.69, 'y': 1.08, 'z': 1.35}, 'rotation': {'x': 0.0, 'y': 35.51, 'z': 0.0}, 'size': {'x': 0.18, 'y': 0.33, 'z': 0.18}}], 'api_list': ['turn_on()']}"
# prompt = operation_prompt_begin + '\n' + data + '\n' + operation_prompt_end

# intention_prompt = (intention_prompt_begin +
#                     "\n注视信息:\n" + gaze_data +
#                     "\n手部信息:\n" + hand_data +
#                     "\n手势信息:\n" + finger_data +
#                     "\n" + intention_prompt_end)
#
# response = client.chat.completions.create(
#         model="glm-4-0520",
#         messages=[
#             {"role": "system", "content": hand_prompt},
#             {"role": "user", "content": hand_data}
#         ]
#     )
intention_prompt = """
假如你是VR场景下的智能代理，需要你帮忙完成VR场景中用户的交互意图识别任务，我会提供给你分析出来的用户注视信息、手部信息、手势信息，以及可能存在的注视对象的状态信息，你需要从中分析用户最有可能的交互意图。

注视信息:
用户从注视盒子变为注视衣柜
手部信息:
左手无明显移动
右手无明显移动
左手无明显旋转
右手有明显旋转
左手与头部的距离无明显变化
右手与头部的距离无明显变化
左手与右手的距离无明显变化
手势信息:
左手手势变化情况：从张开手势变为紧握手势；
右手手势变化情况：从张开手势变为紧握手势；
左手特殊手势情况：无特殊手势；
右手特殊手势情况：无特殊手势。
物体状态信息:
衣柜: 当前状态:关闭状态

以下是一些你在分析过程中需要知道的规则：

1、若注视信息中有两种交互对象，首先考虑同时包含这两种对象的交互意图，并需要考虑两个对象的顺序；在这之后再考虑单个对象的交互意图；
2、开始分析时，你需要先忽略提供的物体状态信息，当你的分析得到的某条交互意图中若存在模糊状态时，如你分析的交互意图为关门或开门这类不确定情况时，则再考虑加入物体状态信息进行补充分析，从而确定交互意图。若你分析出的某条交互意图中不存在这样的情况，则五务必忽略物体状态信息，以免对你的分析产生干扰。

请分析用户最有可能的6种交互意图，每种交互意图请根据可能性进行0-100的打分（分数越高，可能性越大），其中交互意图中出现的交互对象名称需保持和注视信息中的名称一致。

最后输出一个包含六个元素的列表，每个元素为一个字典，包含两个字段，"intention"为可能的交互意图，"possibility"为对应的可能性分数，如下所示：
[{"intention": 交互意图1, "possibility": 交互意图1的可能性分数}, 
{"intention": 交互意图2, "possibility": 交互意图2的可能性分数}, 
{"intention": 交互意图3, "possibility": 交互意图3的可能性分数}, 
{"intention": 交互意图4, "possibility": 交互意图4的可能性分数}, 
{"intention": 交互意图5, "possibility": 交互意图5的可能性分数}, 
{"intention": 交互意图6, "possibility": 交互意图6的可能性分数}]

请严格按上述格式提供结果，不需要提供分析过程。
"""

"""
[{"intention": "从盒子移动到衣柜", "possibility": 100}, 
{"intention": "打开衣柜", "possibility": 90}, 
{"intention": "关闭衣柜", "possibility": 80}, 
{"intention": "检查衣柜", "possibility": 70}, 
{"intention": "抓取衣柜", "possibility": 60}, 
{"intention": "忽略盒子，专注于衣柜", "possibility": 50}]
"""

response = client.chat.completions.create(
    model="glm-4-0520",
    messages=[
        {"role": "user", "content": intention_prompt}
    ]
)
print(response.choices[0].message.content)

