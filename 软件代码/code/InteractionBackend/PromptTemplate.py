gaze_prompt = """
假如你是VR场景下的智能代理，你需要根据采集到的用户注视数据，分析用户的注视行为。

我给你提供的数据中包含3个字段：
timestamp：时间戳，说明这些数据是按时序采集的，你需要以时序为基础进行处理分析；
on_target：用户是否正在注视某个可交互对象，若为TRUE则说明用户正在注视某一物体，若为FALSE则说明用户注视点不在任何可交互物体上；
target_name：注视对象的名称，只有当on_target=TRUE时才有意义

用户的注视对象行为可以分为三类：
1、一直注视某一对象；
2、从一个注视对象转移到另一个注视对象；
3、一开始注视某一对象，之后不再注视任何可交互对象（on_target变为FALSE）。

因此，在这一步中，你需要根据提供的时序数据分析出对应的注视行为，并提供分析结果，按照前面的分类，分析结果的形式为：
用户一直注视XXX  或  用户从注视XXX变为注视YYY  或  用户从注视XXX变为不注视任何对象  （其中XXX、YYY需要根据实际的target_name字段进行替换）

需要强调的两点：1、请基于timestamp进行分析，不要忽略数据之间的时序关系；2、由于采集过程中的不确定性，可能会出现一些噪声点，比如一系列on_target=TRUE的数据中间突然出现一条on_target=FALSE的数据，或者一系列target_name=XXX的数据中间突然出现几条target_name=YYY的数据，你需要识别出这些噪声点并丢弃，只提取出现次数较多的那些注视对象。

每次我会给你提供一份数据，是转为文本的csv格式数据，一份数据对应一个注视行为。

请只输出一行分析结果，格式按照前述要求，分析过程由你内部完成，不需要输出给我。
"""

gaze_data = """
timestamp,on_target,target_name
0,True,Milk Bottle
1,True,Milk Bottle
2,True,Milk Bottle
3,True,Milk Bottle
4,True,Milk Bottle
5,True,Milk Bottle
6,False,None
7,True,Milk Cup
8,True,Milk Cup
9,True,Milk Cup
10,True,Milk Cup
11,True,Milk Cup
12,True,Milk Cup
13,True,Milk Cup
14,True,Milk Cup
15,True,Milk Cup
16,True,Milk Cup
"""

hand_prompt = """
假如你是VR场景下的智能代理，你需要根据采集到的用户手部数据，计算用户的手部行为。

我给你提供的数据中包含：
timestamp：时间戳，说明这些数据是按时序采集的，你需要以时序为基础进行处理分析；
left_hand_pos_x、left_hand_pos_y、left_hand_pos_z：左手位置坐标；
right_hand_pos_x、right_hand_pos_y、right_hand_pos_z：右手位置坐标；
left_hand_rot_angle：左手旋转角度（当前时刻相对于前一时刻的旋转角度）；
right_hand_rot_angle：右手旋转角度（当前时刻相对于前一时刻的旋转角度）；
leftHand_head_dist：左手和用户头部之间的距离；
rightHand_head_dist：右手和用户头部之间的距离；
leftHand_rightHand_dist：左手和右手之间的距离。

坐标对应的方向定义为：x轴正方向为右，x轴负方向为左，y轴正方向为上，y轴负方向为下，z轴正方向为前，z轴负方向为后

计算并分析以下3项内容：
一、
分析对象：
left_hand_pos_x、left_hand_pos_y、left_hand_pos_z、right_hand_pos_x、right_hand_pos_y、right_hand_pos_z六个字段
分析方法：
对每个字段分别进行分析，若开始几帧的平均值和结束几帧的平均值之差超过0.1，则判定对应手在对应方向上有明显移动。
例如，最后5帧的left_hand_pos_x的平均值 减去 前5帧的left_hand_pos_x的平均值，若差值>0.1则左手有明显向右移动，若差值<-0.1则左手有明显向左移动，否则说明左手没有明显的左右方向上的移动。其他5个字段的分析与此同理。
结果中的方向为向前、向后、向左、向右、向上、向下，不要出现x轴、y轴、z轴。
分析结果：
1、左手有明显移动，移动方向为……（可能有多个移动方向） 或者 左手无明显移动；
2、右手有明显移动，移动方向为……（可能有多个移动方向） 或者 右手无明显移动。

二、
分析对象：
left_hand_rot_angle、right_hand_rot_angle两个字段
分析方法：
若连续几帧的数值均超过或接近10，则判定对应手有明显旋转。
例如，若中间连续有3帧数据left_hand_rot_angle均>10，则认为左手有明显旋转，否则左手无明显旋转。右手同理。
分析结果：
1、左手是否有明显旋转；
2、右手是否有明显旋转。

三、
分析对象：
leftHand_head_dist、rightHand_head_dist、leftHand_rightHand_dist三个字段
分析方法：
取开头几帧的平均值作为起始距离，中间几帧的平均值作为中期距离，最后几帧的平均值作为结束距离，以0.08为阈值分析这三个时间的距离是否有明显变化。
例如，计算前5帧的leftHand_head_dist的平均值记为A、中间5帧的leftHand_head_dist的平均值记为B、最后5帧的leftHand_head_dist的平均值记为C，若B-A>0.08且C-B>0.08，则说明左手与头部的距离一直增大；若B-A>0.08且C-B<-0.08，则说明左手与头部的距离先增大后减小。其他情况类似，另外两个字段同理。
分析结果：
1、左手与头部的距离有明显变化，距离增大/减小/先增大后减小/先减小后增大 或者 左手与头部的距离无明显变化；
2、右手与头部的距离有明显变化，距离增大/减小/先增大后减小/先减小后增大 或者 右手与头部的距离无明显变化；
3、左手与右手的距离有明显变化，距离增大/减小/先增大后减小/先减小后增大 或者 左手与右手的距离无明显变化。

3项内容共计7项分析结果，因此最终结果共7行。

其中，需要说明的是：
1、请基于timestamp进行分析，不要忽略数据之间的时序关系
2、务必使用完整的数据，而不仅对文件中前几帧进行分析
3、分析过程请严格基于数据进行计算，但最终提供的是概括性的结果（即最终结果不需要提供具体的数值，而是概括性使用类似于距离远离/靠近、有/无明显旋转等结论）

每次我会给你提供一份数据，是转为文本的csv格式数据，一份数据对应一份手部行为，请只输出上述规定格式提供分析结果，结果有且仅有7行，分析过程由你内部完成，不需要输出给我。
"""

hand_data = """
timestamp,left_hand_pos_x,left_hand_pos_y,left_hand_pos_z,right_hand_pos_x,right_hand_pos_y,right_hand_pos_z,left_hand_rot_angle,right_hand_rot_angle,leftHand_head_dist,rightHand_head_dist,leftHand_rightHand_dist
0,-0.22,-0.28,0.18,0.13,-0.06,0.49,0.0,0.0,0.4,0.51,0.52
1,-0.22,-0.28,0.18,0.13,-0.06,0.49,0.27,1.27,0.4,0.51,0.51
2,-0.22,-0.28,0.19,0.12,-0.06,0.49,0.14,1.22,0.4,0.51,0.51
3,-0.22,-0.28,0.19,0.12,-0.06,0.5,0.16,1.21,0.41,0.51,0.51
4,-0.23,-0.28,0.19,0.11,-0.06,0.5,0.02,3.49,0.41,0.51,0.51
5,-0.23,-0.28,0.19,0.1,-0.06,0.5,0.1,8.86,0.41,0.51,0.5
6,-0.23,-0.28,0.19,0.09,-0.07,0.49,0.18,15.58,0.41,0.51,0.49
7,-0.23,-0.28,0.19,0.07,-0.09,0.47,0.34,25.18,0.41,0.48,0.45
8,-0.23,-0.28,0.19,0.06,-0.1,0.43,0.39,23.03,0.41,0.45,0.41
9,-0.23,-0.28,0.2,0.06,-0.11,0.4,0.59,10.21,0.41,0.42,0.39
10,-0.23,-0.28,0.19,0.06,-0.12,0.36,0.26,6.1,0.41,0.39,0.37
11,-0.23,-0.28,0.19,0.07,-0.12,0.32,0.33,4.25,0.41,0.35,0.36
12,-0.23,-0.28,0.19,0.08,-0.13,0.29,0.57,4.54,0.41,0.33,0.35
13,-0.23,-0.27,0.19,0.09,-0.15,0.26,0.44,1.45,0.41,0.32,0.35
14,-0.23,-0.27,0.19,0.09,-0.15,0.22,0.39,2.54,0.41,0.28,0.34
15,-0.23,-0.27,0.19,0.09,-0.15,0.2,0.1,3.31,0.41,0.27,0.34
16,-0.23,-0.27,0.19,0.09,-0.16,0.19,0.23,1.21,0.4,0.26,0.34
17,-0.23,-0.27,0.19,0.09,-0.16,0.19,0.15,1.08,0.41,0.26,0.34
18,-0.23,-0.27,0.19,0.09,-0.16,0.19,0.13,0.37,0.41,0.26,0.34
19,-0.23,-0.27,0.19,0.09,-0.15,0.19,0.1,0.56,0.4,0.26,0.34
20,-0.23,-0.27,0.19,0.09,-0.15,0.19,0.19,0.91,0.41,0.26,0.34
21,-0.23,-0.27,0.19,0.09,-0.15,0.19,0.16,0.35,0.41,0.26,0.34
22,-0.23,-0.27,0.19,0.09,-0.15,0.19,0.14,0.85,0.41,0.26,0.34
23,-0.23,-0.27,0.19,0.09,-0.15,0.19,0.21,0.25,0.4,0.26,0.34
24,-0.23,-0.27,0.19,0.09,-0.15,0.19,0.24,0.82,0.4,0.26,0.34
25,-0.23,-0.27,0.19,0.09,-0.15,0.19,0.27,0.32,0.4,0.26,0.35
26,-0.23,-0.27,0.19,0.09,-0.15,0.19,0.19,0.33,0.4,0.26,0.35
27,-0.23,-0.27,0.19,0.09,-0.15,0.19,0.28,0.26,0.4,0.26,0.35
"""

finger_prompt = """
假如你是VR场景下的智能代理，你需要根据采集到的用户手指数据，计算用户的手势行为。

我给你提供的数据中包含：
timestamp：时间戳，说明这些数据是按时序采集的，你需要以时序为基础进行处理分析；
以flex结尾的字段：表示对应手指是否屈曲（例如：left_thumb_flex表示左手大拇指是否屈曲）；
以curl结尾的字段：表示对应手指是否弯曲（例如：left_thumb_curl表示左手大拇指是否弯曲）；
left_pinching、right_pinching：分别表示左手、右手是否有“捏合”的手势；
left_pointing、right_pointing：分别表示左手、右手是否有“指向”的手势。

其中，屈曲的定义为：手指与手掌相连的关节是否屈曲；弯曲的定义为：手指远端指节是否弯曲。

请按两个方面进行分析：

一、分析整体手势
这一步忽略双手的大拇指的数据，只看每只手其他四指的数据，对于每一帧的数据，定义以下三种手势：
张开：除大拇指外的其他四指的flex和curl均为FALSE；
半握：除大拇指外的其他四指的flex为TRUE，curl为FALSE；
紧握：除大拇指外的其他四指的curl为TRUE；
由于采集手部数据时可能存在的误差，不可能完美匹配，请根据匹配度分析最有可能的整体手势，从上述三种整体手势中选择最有可能的手势
接下来你需要分析整个多帧数据中手势的时序变化，需要考虑可能存在的噪声数据，分析结果格式为：
一直保持XXX手势 或 从XXX手势变为YYY手势 或 从XXX手势先变为YYY手势再变为ZZZ手势
注：一般来说，一个数据文件中的手势变化不会超过两次，若出现大量手势变化，可能是由于噪声点的影响，你需要分析并去除。

二、分析特殊手势
这一步请分析left_pinching、right_pinching、left_pointing、right_pointing四个字段。
如果某个字段连续5帧以上均为True，则说明对应手有对应的特殊手势
由于存在用户不小心触发该动作或检测有误等情况，因此，你需要正确处理噪声情况，只有连续5帧以上均保持该特殊手势，才说明用户真的在做该特殊手势。
分析结果格式为：
存在特殊手势：XXX 或 无特殊手势

最后，请输出两只手各自的整体手势变化情况，以及中间可能存在的特殊手势。

最终的输出格式为：
左手手势变化情况：【左手整体手势分析结果】；
右手手势变化情况：【右手整体手势分析结果】；
左手特殊手势情况：【左手特殊手势分析结果】；
右手特殊手势情况：【右手特殊手势分析结果】。

每次我会给你提供一份数据，是转为文本的csv格式数据，一份数据对应一份手势行为，请只按照上述格式输出分析结果，分析过程由你内部完成，不需要输出给我。
"""

finger_data = """
timestamp,left_thumb_flex,left_index_flex,left_middle_flex,left_ring_flex,left_pinky_flex,left_thumb_curl,left_index_curl,left_middle_curl,left_ring_curl,left_pinky_curl,right_thumb_flex,right_index_flex,right_middle_flex,right_ring_flex,right_pinky_flex,right_thumb_curl,right_index_curl,right_middle_curl,right_ring_curl,right_pinky_curl
0,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,TRUE,TRUE,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE
1,FALSE,FALSE,FALSE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,TRUE,TRUE,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE
2,FALSE,FALSE,FALSE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,TRUE,TRUE,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE
3,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE
4,FALSE,TRUE,TRUE,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE
5,FALSE,TRUE,TRUE,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,TRUE,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE
6,FALSE,TRUE,TRUE,TRUE,TRUE,FALSE,TRUE,FALSE,TRUE,FALSE,FALSE,TRUE,TRUE,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE
7,FALSE,TRUE,TRUE,TRUE,TRUE,FALSE,TRUE,TRUE,TRUE,TRUE,FALSE,FALSE,TRUE,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE
8,FALSE,TRUE,TRUE,TRUE,TRUE,FALSE,TRUE,FALSE,TRUE,TRUE,FALSE,FALSE,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE
9,FALSE,TRUE,TRUE,TRUE,TRUE,FALSE,TRUE,FALSE,TRUE,TRUE,FALSE,FALSE,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE
10,FALSE,TRUE,TRUE,TRUE,TRUE,FALSE,TRUE,FALSE,TRUE,TRUE,FALSE,TRUE,TRUE,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE
11,FALSE,TRUE,TRUE,TRUE,TRUE,FALSE,FALSE,FALSE,TRUE,TRUE,FALSE,TRUE,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE
12,FALSE,TRUE,TRUE,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,TRUE,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE
13,FALSE,TRUE,TRUE,TRUE,TRUE,FALSE,TRUE,FALSE,FALSE,FALSE,FALSE,TRUE,TRUE,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE
14,FALSE,TRUE,TRUE,TRUE,TRUE,FALSE,TRUE,FALSE,FALSE,FALSE,FALSE,TRUE,TRUE,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE
15,FALSE,TRUE,TRUE,TRUE,TRUE,FALSE,TRUE,FALSE,FALSE,FALSE,FALSE,TRUE,TRUE,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE
"""

intention_prompt_begin_1 = """
假如你是VR场景下的智能代理，需要你帮忙完成VR场景中用户的交互意图识别任务，我会提供给你分析出来的用户注视信息、手部信息、手势信息，以及可能存在的注视对象的状态信息，你需要从中分析用户最有可能的交互意图。
"""

intention_prompt_begin_2 = """
假如你是VR场景下的智能代理，需要你帮忙完成VR场景中用户的交互意图识别任务，我会提供给你分析出来的用户注视信息、语音信息，以及可能存在的注视对象的状态信息，你需要从中分析用户最有可能的交互意图。
"""

intention_prompt_end = """
以下是一些你在分析过程中需要知道的规则：

1、若注视信息中有两种交互对象，首先考虑同时包含这两种对象的交互意图，并需要考虑两个对象的顺序；在这之后再考虑单个对象的交互意图；
2、开始分析时，你需要先忽略提供的物体状态信息，当你的分析得到的某条交互意图中若存在模糊状态时，如你分析的交互意图为关门或开门这类不确定情况时，则再考虑加入物体状态信息进行补充分析，从而确定交互意图。若你分析出的某条交互意图中不存在这样的情况，则务必忽略物体状态信息，以免对你的分析产生干扰。

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

operation_prompt_begin = """
假如你是VR场景下的智能代理，你需要根据用户的交互意图帮助用户操控场景中的物体。
以下是需要分析的数据：
"""

operation_prompt_end = """
字段解释：
intention：表示用户的交互意图，即你需要完成的操作任务；
objects_info：所有相关的物体的列表，每一个元素为一个相关物体，其中：name为物体名称，movable为物体能否位移，position为物体位置坐标，api_list为物体可调用的api列表。

坐标系补充说明：xz平面为水平面（x轴为左右方向，z轴为前后方向），y轴为高度轴。

你需要按照以下步骤进行分析：
一、确定唯一的待操作物体
一般来说，如果意图中只有一个物体，那就仅操控该物体；如果意图中有两个物体，请根据常识，选择操控其中一个物体。即无论怎样，都仅操控一个物体实现交互意图，将该物体确定为待操作物体（controlled_object）。

二、确定操作类型
操作类型分为两种：1、对待操作物体进行位移；2、调用待操作物体的api
如果交互意图中涉及到需要移动、旋转待操作物体的操作，且待操作物体的movable为True，且待操作物体的api_list中的api信息和交互意图不相关，则操作类型type=1（一般来说，如果交互意图中出现两个物体，大概率是此类操作类型）；
如果提供的待操作物体的api_list不为空，且其中某个api的名称和交互意图强相关，即若调用api即可完成交互意图，则操作类型type=2（你不能将交互意图强制和api_list中的某个api联系起来，如果确实找不到合适的api，则将操作类型type设为0）；
否则，如果你认为交互意图无法通过上述两种类型的操作完成，则设type=0

三、计算具体操作信息
若type=0：
则无需操作。
若type=1：
请计算待操作物体最终需要被移动到哪个位置（destination_position）、到达目标位置后是否需要让被操作物体做一些小范围运动（motion）、到达目标位置后是否需要倾斜被操作物体（incline）。
做小范围运动的含义为：若只是简单的移动、放置等操作，则到达目标位置就结束，motion=0；若类似于拿笔写字，刀切食物、擦拭物品等操作，根据常识当被操作物体到达目标位置后还需要做一些小范围移动（铅笔的左右移动、刀的上下移动等），这种情况下motion=1。
倾斜物体的含义为：若交互意图类似倒水、倒牛奶、倒咖啡、浇水等需要倾斜被操作物体，则incline=1；否则，incline=0。
此外，如果objects_info有两个物体，一般来说，则将待操作物体移到另一个物体处。
若type=2：请分析具体要使用api_list中的哪个api，api必须来源于提供的api_list，需要和提供的某个api名称一致，你不能凭空捏造。

四、按json格式输出
若type=0，输出的json格式为：
{"type": 0}
若type=1，输出的json格式为：
{"type": 1, "controlled_object": , "destination_position": , "motion": , "incline": }
若type=2，输出的json格式为：
{"type": 2, "controlled_object": , "api": }

controlled_object和api请使用中文，确保与提供的objects_info中对应的内容一致

无论如何，请严格按上述json格式进行输出，只需要输出json结果，结果前后也不要包含json相关说明，确保第一个字符为{，最后一个字符为}，保证整个输出内容能够被json模块解析。分析过程由你内部完成，不需要提供给我。
"""