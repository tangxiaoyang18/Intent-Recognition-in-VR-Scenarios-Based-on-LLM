using UnityEngine;


/// <summary>
/// 该脚本用为Unity编辑器扩展
/// 作用：当给public变量添加[DisplayOnly]时，该变量在Inspector视图中变为只读状态，不嫩在该视图中编辑
/// </summary>
public class DisplayOnly : PropertyAttribute
{

}