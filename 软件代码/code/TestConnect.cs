using System;
using System.Collections;
using System.Collections.Generic;
using System.Net.WebSockets;
using System.Security.Cryptography;
using System.Text;
using System.Threading;
using UnityEngine;

public class TestConnect : MonoBehaviour
{
    private string appid = "944ae114";
    private string appkey = "192d7cb1f510d910cbfb160ff5fbbaa9";

    private string timeStamp;
    private string baseString;
    private string toMd5;

    private string signa;
    private ClientWebSocket ws;
    private CancellationToken ct;

    // Start is called before the first frame update
    void Start()
    {
        Connect();
    }

    private async void Connect()
    {
        try
        {
            ws = new ClientWebSocket();
            ct = new CancellationToken();
            Uri uri = GetUri();
            await ws.ConnectAsync(uri, ct);

            //await ws.SendAsync(new ArraySegment<byte>(Encoding.UTF8.GetBytes("{\"end\": true}")), WebSocketMessageType.Binary, true, ct); //��������
            while (true)
            {
                var result = new byte[1024];
                await ws.ReceiveAsync(new ArraySegment<byte>(result), new CancellationToken()); 
                var str = Encoding.UTF8.GetString(result, 0, result.Length);
                Debug.Log("Return String: " + str);
            }
        }
        catch (Exception ex)
        {
            Debug.Log("Exception Msg: " + ex.Message);
            ws.Dispose();
        }
    }

    private Uri GetUri()
    {

        timeStamp = GetTimeStamp();

        baseString = appid + timeStamp;

        toMd5 = ToMD5(baseString);

        signa = ToHmacSHA1(toMd5, appkey);

        string requestUrl = string.Format("wss://rtasr.xfyun.cn/v1/ws?appid={0}&ts={1}&signa={2}&pd=tech", appid,
            timeStamp, UrlEncode(signa));
        Debug.Log("requestUrl: " + requestUrl);
        return new Uri(requestUrl);
    }

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

    public static string GetTimeStamp()
    {
        TimeSpan ts = DateTime.UtcNow - new DateTime(1970, 1, 1, 0, 0, 0, 0);
        return Convert.ToInt64(ts.TotalSeconds).ToString();
    }


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


    public static string ToHmacSHA1(string text, string key)

    {
        //HMACSHA1����
        HMACSHA1 hmacsha1 = new HMACSHA1();
        hmacsha1.Key = System.Text.Encoding.UTF8.GetBytes(key);

        byte[] dataBuffer = System.Text.Encoding.UTF8.GetBytes(text);
        byte[] hashBytes = hmacsha1.ComputeHash(dataBuffer);

        return Convert.ToBase64String(hashBytes);
    }
}