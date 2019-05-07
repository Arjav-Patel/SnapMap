using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEngine;

public class LevelManager : MonoBehaviour
{ 
    // Level blocks
    List<GameObject> Blocks;

    // Texture cache for faster loading times
    Dictionary<string, Texture> texCache;

    // Options
    public bool save = false;
    public bool reload = false;

    // Tag Manager
    public bool tagBlocks = false;
    SerializedObject tagManager;
    SerializedProperty tagsProp;

    // Paths
    public string level;
    public string spritePath = "Sprites";
    public string dataPath = "Data";
    void Awake() 
    {
        tagManager = new SerializedObject(AssetDatabase.LoadAllAssetsAtPath("ProjectSettings/TagManager.asset")[0]);
        tagsProp = tagManager.FindProperty("tags");

        Blocks = new List<GameObject>();

        texCache = new Dictionary<string, Texture>();

        LoadLevel();
    }


    private void Update()
    {
        if (reload)
        {
            for (int i = 0; i < Blocks.Count; i++)
            {
                Destroy(Blocks[i]);
            }
            Blocks.Clear();

            LoadLevel();
            reload = false;
        }

        if (save)
        {
            SaveLevel();
            save = false;
        }
    }

    void LoadLevel()
    {
        
        float unitBlockWidth = int.MaxValue;
        string[] lines = File.ReadAllLines(Path.Combine(Application.dataPath, dataPath, level + ".txt"));
        for (int i = 0; i < lines.Length; i++)
        {
            string[] blockParams = lines[i].Split(' ');

            string sprite = blockParams[0].Split('.')[0];

            float x = float.Parse(blockParams[1]);
            float y = float.Parse(blockParams[2]);
            float z = float.Parse(blockParams[3]);

            float x_rot = float.Parse(blockParams[4]);
            float y_rot = float.Parse(blockParams[5]);
            float z_rot = float.Parse(blockParams[6]);

            float width = float.Parse(blockParams[7]);
            float height = float.Parse(blockParams[8]);
            float depth = float.Parse(blockParams[9]);
        
            if (width < unitBlockWidth) 
            {
                unitBlockWidth = width;
            }
            CreateBlock(x, y, z, x_rot, y_rot, z_rot, width, height, depth, sprite);
        }

        NormalizeBlocks(unitBlockWidth);

        reload = true;
    }


    void CreateBlock(float x, float y, float z, float x_rot, float y_rot, float z_rot, float width, float height, float depth, string sprite, PrimitiveType type=PrimitiveType.Cube)
    {
        GameObject block = GameObject.CreatePrimitive(type);

        if (texCache.ContainsKey(sprite)) 
        {
            block.GetComponent<MeshRenderer>().material.mainTexture = texCache[sprite];
        }
        else 
        {
            Texture tex =  Resources.Load<Texture>(Path.Combine(spritePath,  sprite));

            block.GetComponent<MeshRenderer>().material.mainTexture = tex;
            texCache.Add(sprite, tex);
        }

        block.transform.position = new Vector3(x, y, z);
        block.transform.eulerAngles = new Vector3(x_rot, y_rot, z_rot);
        block.transform.localScale = new Vector3(width, height, depth);

        block.name = sprite;

        if (tagBlocks)
        {
            CreateTag(sprite);
            block.tag = sprite;
        }
        
        Blocks.Add(block);

    }


    void NormalizeBlocks(float unitBlockWidth) 
    {
        for (int i = 0; i < Blocks.Count; i++) 
        {
            Vector3 scale = Blocks[i].transform.localScale;
            Vector3 position = Blocks[i].transform.position;

            Vector3 normalizedScale = new Vector3 
            (
                scale.x / unitBlockWidth,
                scale.y / unitBlockWidth,
                scale.z / unitBlockWidth
            );
            
            Vector3 normalizedPosition = new Vector3 
            (
                position.x / unitBlockWidth,
                position.y / unitBlockWidth,
                position.z / unitBlockWidth
            );

            Blocks[i].transform.localScale = normalizedScale;
            Blocks[i].transform.position = normalizedPosition;
        }
    }

    void CreateTag(string sprite)
    {
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

    void SaveLevel()
    {
        using (System.IO.StreamWriter file =
            new System.IO.StreamWriter(File.Open(Path.Combine(Application.dataPath, "Data", level + ".txt"), FileMode.OpenOrCreate)))
        {
            for (int i = 0; i < Blocks.Count; i++)
            {
                string sprite = Blocks[i].name;

                float x = Blocks[i].transform.position.x;
                float y = Blocks[i].transform.position.y;
                float z = Blocks[i].transform.position.z;

                float x_rot = Blocks[i].transform.localEulerAngles.x;
                float y_rot = Blocks[i].transform.localEulerAngles.y;
                float z_rot = Blocks[i].transform.localEulerAngles.z;

                float width = Blocks[i].transform.localScale.x;
                float height = Blocks[i].transform.localScale.y;
                float depth = Blocks[i].transform.localScale.z;

                string line = string.Format("{0} {1} {2} {3} {4} {5} {6} {7} {8} {9}", sprite, x, y, z, x_rot, y_rot, z_rot, width, height, depth);
                file.WriteLine(line);
            }
        }
        Debug.Log("Saved");
    }
}
