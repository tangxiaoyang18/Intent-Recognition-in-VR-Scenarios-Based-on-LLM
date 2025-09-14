using System;
using System.Collections;
using System.Collections.Generic;
using System.Net;
using System.Text;
using Newtonsoft.Json.Linq;
using Unity.XR.PXR;
using UnityEngine;

[RequireComponent(typeof(AudioSource))]
public class MicUnlimitedDuration : MonoBehaviour
{
    public AudioSource audioSource;

    AudioClip micClip;

    bool isMicRecordFinished = true;

    List<float> micDataList = new List<float>();
    float[] micDataTemp;


    private DateTime beginTime;
    [DisplayOnly] public string filePath; 
    //C:/Users/Administrator/AppData/LocalLow/DefaultCompany/VisualCommunication/REC/
    public string dirName = "REC";
    private AudioClip newAudioClip;

    public void StartMicrophone()
    {
        StopCoroutine(Recording());
        StartCoroutine(Recording());
    }


    IEnumerator Recording()
    {
        Debug.Log("Start Mic");
        if (Microphone.devices.Length == 0)
        {
            Debug.LogError("no mic device");
            yield break;
        }

        newAudioClip = null;
        micDataList = new List<float>();
        micClip = Microphone.Start(null, true, 2, 16000);
        isMicRecordFinished = false;
        int length = micClip.channels * micClip.samples;
        bool isSaveFirstHalf = true; 
        int micPosition;
        while (!isMicRecordFinished)
        {
            if (isSaveFirstHalf)
            {
                yield return new WaitUntil(() =>
                {
                    micPosition = Microphone.GetPosition(null);
                    return micPosition > length * 6 / 10 && micPosition < length;
                }); 
                micDataTemp = new float[length / 2];
                micClip.GetData(micDataTemp, 0);
                micDataList.AddRange(micDataTemp);
                isSaveFirstHalf = !isSaveFirstHalf;
            }
            else
            {
                yield return new WaitUntil(() =>
                {
                    micPosition = Microphone.GetPosition(null);
                    return micPosition > length / 10 && micPosition < length / 2;
                }); 
                micDataTemp = new float[length / 2];
                micClip.GetData(micDataTemp, length / 2);
                micDataList.AddRange(micDataTemp);
                isSaveFirstHalf = !isSaveFirstHalf;
            }
        }

        micPosition = Microphone.GetPosition(null);
        if (micPosition <= length) //ǰ���
        {
            micDataTemp = new float[micPosition / 2];
            micClip.GetData(micDataTemp, 0);
        }
        else
        {
            micDataTemp = new float[micPosition - length / 2];
            micClip.GetData(micDataTemp, length / 2);
        }

        micDataList.AddRange(micDataTemp);
        Microphone.End(null);
        newAudioClip = AudioClip.Create("RecordClip", micDataList.Count, 1, 16000, false);
        newAudioClip.SetData(micDataList.ToArray(), 0);
        audioSource.clip = newAudioClip;

   
        Save(newAudioClip);
        Debug.Log("RecordEnd");
    }


    public void StopMicrophone()
    {
        Debug.Log("Stop mic");
        isMicRecordFinished = true;
    }

    public void PlayAudioRecord()
    {
        if (audioSource == null)
        {
            Debug.LogError("no audioclip");
            return;
        }

        audioSource.Play();
    }

    public byte[] Save(AudioClip clip)
    {
        if (clip == null)
        {
            Debug.Log("clip is null,can't be saved");
            return null;
        }

        return WavUtility.FromAudioClip(clip, out filePath, true, dirName);
    }

    public AudioClip Read(string path)
    {
        return WavUtility.ToAudioClip(path);
    }

    public AudioClip Read(byte[] data)
    {
        return WavUtility.ToAudioClip(data);
    }

    private void Reset()
    {
        audioSource = GetComponent<AudioSource>();
        audioSource.playOnAwake = false;
    }
}