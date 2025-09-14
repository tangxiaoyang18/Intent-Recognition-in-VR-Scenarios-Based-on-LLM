using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;
using System.Net.WebSockets;
using System.Security.Cryptography;
using System.Text;
using System.Threading;
using Newtonsoft.Json;
using UnityEngine.UI;
using UnityEngine.XR.Interaction.Toolkit;
using UnityEngine.XR;
using TMPro;
using LitJson;

/// <summary>
/// ����ֵ�����ʽΪjson
/// </summary>
[Serializable]
public struct JsonData
{

    public string action;

    public string code;

    public string data;

    public string desc;
    public string sid;
}

[Serializable]
public struct Data
{
    /// <summary>
    /// תд������	��0��ʼ
    /// </summary>
    public string seg_id;

    [Serializable]
    public struct CN
    {
        [Serializable]
        public struct ST
        {
            [Serializable]
            public struct RT
            {
                [Serializable]
                public class WS
                {
                    [Serializable]
                    public class CW
                    {
                        /// <summary>
                        /// ��ʶ����
                        /// </summary>
                        public string w;

                        /// <summary>
                        /// �ʱ�ʶ  n-��ͨ�ʣ�s-˳���ʣ������ʣ���p-���
                        /// </summary>
                        public string wp;
                    }

                    [SerializeField] public CW[] cw;

                    /// <summary>
                    /// ���ڱ����еĿ�ʼʱ�䣬��λ��֡��1֡=10ms  ���������������еĿ�ʼʱ��Ϊ(bg+wb*10)ms
                    /// �м����� wb Ϊ 0
                    /// </summary>
                    public string wb;

                    /// <summary>
                    /// ���ڱ����еĽ���ʱ�䣬��λ��֡��1֡=10ms  ���������������еĽ���ʱ��Ϊ(bg+we*10)ms
                    /// �м����� we Ϊ 0
                    /// </summary>
                    public string we;
                }

                [SerializeField] public WS[] ws;
            }

            [SerializeField] public RT[] rt;

            /// <summary>
            /// ���������������еĿ�ʼʱ�䣬��λ����(ms)
            /// �м�����bgΪ׼ȷֵ
            /// </summary>
            public string bg;

            /// <summary>
            /// ������ͱ�ʶ	0-���ս����1-�м���
            /// </summary>
            public string type;

            /// <summary>
            /// ���������������еĽ���ʱ�䣬��λ����(ms)
            /// �м�����edΪ0
            /// </summary>
            public string ed;
        }

        [SerializeField] public ST st;
    }

    [SerializeField] public CN cn;

    /// <summary>
    /// 
    /// </summary>
    public string ls;

    public override string ToString()
    {
        return string.Format("seg_id:{0}, cn:{1}, ls:{2}", seg_id.ToString(), cn.ToString(), ls.ToString());
    }
}

public class VisualCommunication : MonoBehaviour
{
    private string appid = "944ae114";
    private string appkey = "192d7cb1f510d910cbfb160ff5fbbaa9";

    private string timeStamp;
    private string baseString;
    private string toMd5;

    private string signa;

    public AudioClip RecordedClip;
    private ClientWebSocket ws;
    private CancellationToken ct;

    //���¼��ʱ��
    private int MAX_RECORD_LENGTH = 3599;

    /// <summary>
    /// ����ʶ��ص��¼�
    /// </summary>
    public event Action<string> asrCallback;


    public AudioClip clipTest;
    public Text _text;

    public TMP_Text debug_text;
    private bool flag = false;

    private Coroutine autoStopCoroutine;
    private bool isCountdownActive = false; 

    // ����������ѡ�񴥷�¼�����ֱ�����/�ң�
    public enum HandType { Left, Right }
    public HandType hand = HandType.Left;

    // �������������ô���¼���İ�����Ĭ��ΪTrigger��
    public InputHelpers.Button triggerButton = InputHelpers.Button.Trigger;

    void Update()
    {
        if (CheckControllerButtonPressed(hand, triggerButton))
        {
            if (!flag)
            {
                flag = true;
                StartASR();
                debug_text.text += "��ʼ¼��\n";
            }

            if (isCountdownActive)
            {
                StopCoroutine(autoStopCoroutine);
                isCountdownActive = false;
                debug_text.text += "ȡ���Զ�ֹͣ\n";
            }
        }
        else if (flag && !isCountdownActive)
        {
            autoStopCoroutine = StartCoroutine(AutoStopAfterDelay(3f));
            isCountdownActive = true;
            debug_text.text += "����3��ֹͣ����ʱ\n";
        }
    }

    IEnumerator AutoStopAfterDelay(float seconds)
    {
        yield return new WaitForSeconds(seconds);
        StopASR();
        flag = false;
        isCountdownActive = false;
        debug_text.text += "�Զ�ֹͣ���\n";
    }

    private bool CheckControllerButtonPressed(HandType handType, InputHelpers.Button button)
    {
        InputDeviceCharacteristics characteristics =
            (handType == HandType.Left) ?
            InputDeviceCharacteristics.Left :
            InputDeviceCharacteristics.Right;

        List<InputDevice> devices = new List<InputDevice>();
        InputDevices.GetDevicesWithCharacteristics(characteristics, devices);

        if (devices.Count > 0)
        {
            InputDevice device = devices[0];

            // ���� button ������̬��ⲻͬ����
            switch (button)
            {
                case InputHelpers.Button.Trigger:
                    if (device.TryGetFeatureValue(CommonUsages.triggerButton, out bool triggerPressed))
                    {
                        return triggerPressed;
                    }
                    break;
                case InputHelpers.Button.Grip:
                    if (device.TryGetFeatureValue(CommonUsages.gripButton, out bool gripPressed))
                    {
                        return gripPressed;
                    }
                    break;
                case InputHelpers.Button.PrimaryButton:
                    if (device.TryGetFeatureValue(CommonUsages.primaryButton, out bool primaryPressed))
                    {
                        return primaryPressed;
                    }
                    break;
                    // ����������������...
            }
        }
        return false;
    }

    public void StartASR()
    {
        if (ws != null && ws.State == WebSocketState.Open)
        {
            debug_text.text = debug_text.text + "��ʼ����ʶ��ʧ�ܣ����ȴ��ϴ�ʶ�����ӽ���\n";
            Debug.LogWarning("��ʼ����ʶ��ʧ�ܣ����ȴ��ϴ�ʶ�����ӽ���");
            return;
        }

        if (Microphone.devices.Length == 0)
        {
            debug_text.text = debug_text.text + "δ��⵽���õ���˷�\n";
            Debug.LogError("δ��⵽���õ���˷�");
            return;
        }

        ConnectASR_Aysnc();

        RecordedClip = Microphone.Start(null, false, MAX_RECORD_LENGTH, 16000);
    }

    public async void StopASR()
    {
        if (ws != null)
        {
            //�ص�������Ƶ��Э��
            StopCoroutine(SendAudioClip());

            //Debug.Log("���ͽ�����ʶ" + ws.State);
            //��Ƶ�����ϴ���ɺ�,�ͻ����跢��һ�� {"end": true} ���������Ϊ������ʶ
            await ws.SendAsync(new ArraySegment<byte>(Encoding.UTF8.GetBytes("{\"end\": true}")),
                WebSocketMessageType.Binary,
                true, new CancellationToken());
            ws.Dispose();
            //await ws.CloseAsync(WebSocketCloseStatus.NormalClosure, "�ر�WebSocket����", new CancellationToken());
            Microphone.End(null);
            StartCoroutine(StopRecord());
        }
    }

    private IEnumerator StopRecord()
    {
        yield return new WaitUntil(() => ws.State != WebSocketState.Open);
        debug_text.text = debug_text.text + "ʶ�������ֹͣ¼��\n";
        Debug.Log("ʶ�������ֹͣ¼��");
    }

    async void ConnectASR_Aysnc()
    {
        ws = new ClientWebSocket();
        ct = new CancellationToken();
        Uri url = GetUri();
        await ws.ConnectAsync(url, ct);
        StartCoroutine(SendAudioClip());
        StringBuilder stringBuilder = new StringBuilder();
        while (ws.State == WebSocketState.Open)
        {
            //try
            //{

            var result = new byte[4096];
            await ws.ReceiveAsync(new ArraySegment<byte>(result), ct); //��������
            List<byte> list = new List<byte>(result);
            while (list[list.Count - 1] == 0x00) list.RemoveAt(list.Count - 1); //ȥ�����ֽ�
            string str = Encoding.UTF8.GetString(list.ToArray());
            if (string.IsNullOrEmpty(str))
            {
                return;
            }

            try
            {
                JsonData jsonData = JsonUtility.FromJson<JsonData>(str);
                if (jsonData.action.Equals("started"))
                {
                    debug_text.text = debug_text.text + "���ֳɹ���\n";
                    Debug.Log("���ֳɹ���");
                }
                else if (jsonData.action.Equals("result"))
                {
                    debug_text.text = debug_text.text + "���ؽ����" + str + "\n";
                    Debug.Log("���ؽ����" + str);
                    AnalysisResult(jsonData.data);
                }
                else if (jsonData.action.Equals("error"))
                {
                    debug_text.text = debug_text.text + "Error: " + jsonData.desc + "\n";
                    Debug.Log("Error: " + jsonData.desc);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError(ex.Message + str);
            }

            //}
            //catch (Exception ex)
            //{


            //    Debug.LogError(ex.InnerException);
            //    Debug.LogError(ex.Message);

            //}
        }

        debug_text.text = debug_text.text + "�Ͽ�����\n";
        Debug.LogWarning("�Ͽ�����");
    }


    /// <summary>
    /// ������ƵƬ��
    /// </summary>
    /// <param name="socket"></param>
    /// <returns></returns>
    IEnumerator SendAudioClip()
    {
        yield return new WaitWhile(() => Microphone.GetPosition(null) <= 0);
        float t = 0;
        int position = Microphone.GetPosition(null);
        const float waitTime = 0.04f; 
        const int Maxlength = 1280; 
        int status = 0;
        int lastPosition = 0;
        while (position < RecordedClip.samples && ws.State == WebSocketState.Open)
        {
            t += waitTime;
            if (t >= MAX_RECORD_LENGTH)
            {
                Debug.Log("¼��ʱ�����þ�����������ʶ��");
                break;
            }

            yield return new WaitForSecondsRealtime(waitTime);
            if (Microphone.IsRecording(null))
            {
                position = Microphone.GetPosition(null);
            }

            if (position <= lastPosition)
            {
                continue;
            }

            int length = position - lastPosition > Maxlength ? Maxlength : position - lastPosition;
            byte[] data = GetAudioClip(lastPosition, length, RecordedClip);
            ws.SendAsync(new ArraySegment<byte>(data), WebSocketMessageType.Binary, true,
                new CancellationToken());
            lastPosition = lastPosition + length;
            status = 1;
        }
    }

    string endText = "";

    private void OnApplicationQuit()
    {
        StopASR();
    }

    /// <summary>
    /// ��ȡʶ�𲢷����ַ���
    /// </summary>
    /// <param name="data">����ȡ��ʶ���Json�ַ���</param>
    /// <returns>��ʶ��������һ�仰</returns>
    void AnalysisResult(string data)
    {
        Data result = JsonUtility.FromJson<Data>(data);
        StringBuilder stringBuilder = new StringBuilder();

        //Debug.Log(result.cn.st.rt[0].ws.Length);
        for (int i = 0; i < result.cn.st.rt[0].ws.Length; i++)
        {

            stringBuilder.Append(result.cn.st.rt[0].ws[i].cw[0].w);
        }

        string _thisType = result.cn.st.type;
        string testing = stringBuilder.ToString();

        if (_thisType.Equals("0"))
        {
            endText = endText + testing;
            _text.text = endText;
        }
        else
        {
            _text.text = endText + testing;
        }
    }

    /// <summary>
    /// ��ȡ��Ƶ��Ƭ��
    /// </summary>
    /// <param name="start">��ʼ������</param>
    /// <param name="length">��������</param>
    /// <param name="recordedClip">��Ƶ</param>
    /// <returns></returns>
    public static byte[] GetAudioClip(int start, int length, AudioClip recordedClip)
    {
        float[] soundata = new float[length];
        recordedClip.GetData(soundata, start);
        int rescaleFactor = 32767;
        byte[] outData = new byte[soundata.Length * 2];
        for (int i = 0; i < soundata.Length; i++)
        {
            short temshort = (short)(soundata[i] * rescaleFactor);
            byte[] temdata = BitConverter.GetBytes(temshort);
            outData[i * 2] = temdata[0];
            outData[i * 2 + 1] = temdata[1];
        }

        return outData;
    }

    /// <summary>
    /// �������URI
    /// </summary>
    /// <returns>�����URI</returns>
    private Uri GetUri()
    {
        //��ȷ����
        timeStamp = GetTimeStamp();

        //baseString��appid�͵�ǰʱ���tsƴ�Ӷ���
        baseString = appid + timeStamp;

        //��baseString����MD5
        toMd5 = ToMD5(baseString);

        //��apiKeyΪkey��MD5֮���baseString����HmacSHA1����
        //Ȼ���ٶԼ��ܺ���ַ�������base64����
        signa = ToHmacSHA1(toMd5, appkey);

        string requestUrl = string.Format("wss://rtasr.xfyun.cn/v1/ws?appid={0}&ts={1}&signa={2}&pd=tech", appid,
            timeStamp, UrlEncode(signa));
        Debug.Log("requestUrl: " + requestUrl);
        return new Uri(requestUrl);
    }

    #region һЩ�����㷨

    /// <summary>
    /// ���ַ�������UrlEncodeת��
    /// </summary>
    /// <param name="str">��Ҫת����ַ���</param>
    /// <returns>����UrlEncodeת����ַ���</returns>
    public static string UrlEncode(string str)
    {
        StringBuilder sb = new StringBuilder();
        byte[] byStr = System.Text.Encoding.UTF8.GetBytes(str); //Ĭ����System.Text.Encoding.Default.GetBytes(str)
        for (int i = 0; i < byStr.Length; i++)
        {
            sb.Append(@"%" + Convert.ToString(byStr[i], 16));
        }

        return (sb.ToString());
    }

    /// <summary>
    /// ��ȡʱ���
    /// </summary>
    /// <returns>ʱ�������ȷ����</returns>
    public static string GetTimeStamp()
    {
        TimeSpan ts = DateTime.UtcNow - new DateTime(1970, 1, 1, 0, 0, 0, 0);
        return Convert.ToInt64(ts.TotalSeconds).ToString();
    }

    /// <summary>
    /// MD5�ַ�������
    /// </summary>
    /// <param name="txt">��Ҫ���ܵ��ַ���</param>
    /// <returns>���ܺ��ַ���</returns>
    public static string ToMD5(string txt)
    {
        using (MD5 mi = MD5.Create())
        {
            byte[] buffer = Encoding.Default.GetBytes(txt);
            //��ʼ����
            byte[] newBuffer = mi.ComputeHash(buffer);
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < newBuffer.Length; i++)
            {
                sb.Append(newBuffer[i].ToString("x2"));
            }

            return sb.ToString();
        }
    }

    /// <summary>
    /// HMACSHA1�㷨���ܲ�����ToBase64String
    /// </summary>
    /// <param name="text">Ҫ���ܵ�ԭ��</param>
    ///<param name="key">˽Կ</param>
    /// <returns>����һ��ǩ��ֵ(����ϣֵ)</returns>
    public static string ToHmacSHA1(string text, string key)
    {
        //HMACSHA1����
        HMACSHA1 hmacsha1 = new HMACSHA1();
        hmacsha1.Key = System.Text.Encoding.UTF8.GetBytes(key);

        byte[] dataBuffer = System.Text.Encoding.UTF8.GetBytes(text);
        byte[] hashBytes = hmacsha1.ComputeHash(dataBuffer);

        return Convert.ToBase64String(hashBytes);
    }

    #endregion
}