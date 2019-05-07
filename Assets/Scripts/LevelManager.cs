using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEngine;

public class LevelManager : MonoBehaviour
{
    public float UnitBlockWidth;
    public float UnitBlockHeight;
    public float UnitBlockDepth;

    public float DefaultDepth = 0;

    List<GameObject> Blocks;

    // Options
    public string level;

    public bool load = false;
    public bool save = false;
    public bool useSaveData = false;

    public bool addTags = false;

    void Start()
    {
        System.IO.Directory.CreateDirectory(Path.Combine(Application.dataPath, "Data"));
        System.IO.Directory.CreateDirectory(Path.Combine(Application.dataPath, "Save"));
        System.IO.Directory.CreateDirectory(Path.Combine(Application.dataPath, "Resources"));
        System.IO.Directory.CreateDirectory(Path.Combine(Application.dataPath, "Resources", "Sprites"));
        System.IO.Directory.CreateDirectory(Path.Combine(Application.dataPath, "Resources", "Levels"));

        Blocks = new List<GameObject>();
        LoadLevel();
    }

    private void Update()
    {
        if (load)
        {
            for (int i = 0; i < Blocks.Count; i++)
            {
                Destroy(Blocks[i]);
            }
            Blocks.Clear();

            LoadLevel();
            load = false;
        }

        if (save)
        {
            SaveLevel();
            save = false;
        }
    }

    void LoadLevel()
    {
        string path = "";
        if (!useSaveData)
        {
            path = "Data";
        }
        else
        {
            path = "Save";
        }
        
        string[] lines = File.ReadAllLines(Path.Combine(Application.dataPath, path, level + ".txt"));
        for (int i = 0; i < lines.Length; i++)
        {
            string[] blockParams = lines[i].Split(' ');

            string sprite = blockParams[0];

            float x = float.Parse(blockParams[1]) / UnitBlockWidth;
            float y = float.Parse(blockParams[2]) / UnitBlockHeight;
            // float z = float.Parse(blockParams[3]) / UnitBlockDepth;
            float z = 0;

            // float x_rot = float.Parse(blockParams[4]);
            // float y_rot = float.Parse(blockParams[5]);
            // float z_rot = float.Parse(blockParams[6]);
            float x_rot = 0f;
            float y_rot = 90f;
            float z_rot = 0f;

            float width = int.Parse(blockParams[3]) / UnitBlockWidth;
            float height = int.Parse(blockParams[4]) / UnitBlockHeight;
            float depth = int.Parse(blockParams[3]) / UnitBlockHeight;


            CreateBlock(x, y, z, x_rot, y_rot, z_rot, width, height, depth, sprite);
        }
    }

    void SaveLevel()
    {
        using (System.IO.StreamWriter file =
            new System.IO.StreamWriter(File.Open(Path.Combine(Application.dataPath, "Save", level + ".txt"), FileMode.OpenOrCreate)))
        {
            for (int i = 0; i < Blocks.Count; i++)
            {
                string sprite = Blocks[i].name;

                float x = Blocks[i].transform.position.x * UnitBlockWidth;
                float y = Blocks[i].transform.position.y * UnitBlockHeight;
                float z = Blocks[i].transform.position.z * UnitBlockDepth;

                float x_rot = Blocks[i].transform.localEulerAngles.x;
                float y_rot = Blocks[i].transform.localEulerAngles.y;
                float z_rot = Blocks[i].transform.localEulerAngles.z;

                float width = Blocks[i].transform.localScale.x * UnitBlockWidth;
                float height = Blocks[i].transform.localScale.y * UnitBlockHeight;
                float depth = Blocks[i].transform.localScale.z * UnitBlockDepth;

                string line = string.Format("{0} {1} {2} {3} {4} {5} {6} {7} {8} {9}", sprite, x, y, z, x_rot, y_rot, z_rot, width, height, depth);
                file.WriteLine(line);
            }
        }
    }


    void CreateBlock(float x, float y, float z, float x_rot, float y_rot, float z_rot, float width, float height, float depth, string sprite, PrimitiveType type=PrimitiveType.Cube)
    {
        GameObject block = GameObject.CreatePrimitive(type);
        block.GetComponent<MeshRenderer>().material.mainTexture = Resources.Load<Texture>("Sprites/" + sprite.Split('.')[0]);

        block.transform.position = new Vector3(x, y, z);
        block.transform.eulerAngles = new Vector3(x_rot, y_rot, z_rot);
        block.transform.localScale = new Vector3(width, height, depth);

        block.name = sprite;

        if (addTags)
        {
            AddTag(sprite);
            block.tag = sprite;
        }

        Blocks.Add(block);
    }


    void AddTag(string sprite)
    {
        // Open tag manager
        SerializedObject tagManager = new SerializedObject(AssetDatabase.LoadAllAssetsAtPath("ProjectSettings/TagManager.asset")[0]);
        SerializedProperty tagsProp = tagManager.FindProperty("tags");

        bool found = false;
        for (int i = 0; i < tagsProp.arraySize; i++)
        {
            SerializedProperty tag = tagsProp.GetArrayElementAtIndex(i);
            if (tag.stringValue.Equals(sprite))
            {
                found = true; break;
            }
        }

        if (!found)
        {
            tagsProp.InsertArrayElementAtIndex(0);
            SerializedProperty n = tagsProp.GetArrayElementAtIndex(0);
            n.stringValue = sprite;
        }
        tagManager.ApplyModifiedProperties();
    }
}
