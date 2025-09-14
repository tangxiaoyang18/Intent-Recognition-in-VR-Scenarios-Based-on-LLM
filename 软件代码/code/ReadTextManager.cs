using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Newtonsoft.Json;
using System.IO;
using UnityEngine.UI;
using System.Text;
using System.Text.RegularExpressions;
using System.Linq;

public class ReadTextManager : MonoBehaviour
{
    // Start is called before the first frame update
    public string path;
    public Text readText;
    public TextAsset info;
    public List<string> keyWord;//�ȴʵļ���

    void Start()
    {
        path = Application.streamingAssetsPath + "/hologarment.txt";
        ReadText();
    }
    // Update is called once per frame
    void Update()
    {

    }


    public string SetKeyWordColor(string contont)
    {

        string resutl = SclectKeyWord(contont, keyWord, "<color=#FF0000>", "</color>");

        return resutl;
    }


    public void ReadText()
    {
        string line;
        using (StreamReader stream = new StreamReader(path))
        {
            while ((line = stream.ReadLine()) != null)
            {
                //Debug.Log(line);

                keyWord.Add(line.Trim());//keyWord�����ȴʵļ���
                readText.text = readText.text + "\n" + line;
            }
        }
    }


    public string SclectKeyWord(string content, List<string> keyWord, string befordLabel, string afterLabel)
    {
        char[] charArr = content.ToCharArray();
        List<string> keyArr = keyWord;
        List<char> listArr = new List<char>();
        int matchCount = 0;
        string buffWord = "";
        for (int i = 0; i < charArr.Length; i++)
        {
            matchCount = keyArr.Where(r => r.StartsWith(buffWord + charArr[i].ToString())).Count();
            if (matchCount == 0)
            {
                if (buffWord.Length > 0)
                {
                    if (keyArr.Contains(buffWord))
                        listArr.AddRange((befordLabel + buffWord + afterLabel).ToCharArray());
                    else
                        listArr.AddRange(buffWord.ToCharArray());
                    buffWord = "";
                    matchCount = keyArr.Where(r => r.StartsWith(buffWord + charArr[i].ToString())).Count();
                    if (matchCount > 0)
                        buffWord += charArr[i];
                    else
                        listArr.Add(charArr[i]);
                }
                else
                    listArr.Add(charArr[i]);
            }
            else
            {
                if (matchCount == 1)
                {
                    if (keyArr.Contains(buffWord + charArr[i]))
                    {
                        listArr.AddRange((befordLabel + buffWord + charArr[i] + afterLabel).ToCharArray());
                        buffWord = "";
                    }
                    else
                        buffWord += charArr[i];
                }
                else
                    buffWord += charArr[i];
            }
            if (i == charArr.Length - 1)
            {
                if (keyArr.Contains(buffWord))
                    listArr.AddRange((befordLabel + buffWord + afterLabel).ToCharArray());
                else
                    listArr.AddRange(buffWord.ToCharArray());
            }

        }
        return string.Join("", listArr);
    }
}
