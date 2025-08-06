# Vision Model Testing Quick Reference

## 🎯 **Testing Setup**

### **Model**: Qwen-VL-Max (Alibaba Cloud)

### **Detailed Prompt** (Use this exact text):
```
Please provide a detailed description of this image. Describe the overall scene, environment, surfaces, materials, lighting, and any other relevant visual details. Be comprehensive and include all observations about the setting, spatial relationships, and material characteristics.
```

## 📋 **Testing Process**

### **Step 1: Open Your Vision Model Interface**
- Access your Qwen-VL-Max interface
- Have the `test_images` folder ready (images 1.png through 20.png)

### **Step 2: Test Each Image**
For each image (1.png, 2.png, ..., 20.png):

1. **Load the image** into Qwen-VL-Max
2. **Use the detailed prompt above** (copy-paste exactly)
3. **Copy the full response** from the model
4. **Paste it** into `manual_testing_template.json` 
   - Replace `"ENTER_MODEL_RESPONSE_HERE"` with the actual response
   - Add timestamp if desired

### **Step 3: Generate Report**
When you have some responses (or all 20):
```bash
python debug/collect_vision_responses.py
```

## 📝 **Example Entry**

Replace this:
```json
{
  "image_number": 1,
  "filename": "1.png",
  "actual_result": "ENTER_MODEL_RESPONSE_HERE",
  "test_timestamp": "ENTER_TIMESTAMP_WHEN_TESTED"
}
```

With this (example):
```json
{
  "image_number": 1,
  "filename": "1.png", 
  "actual_result": "This is an indoor dining room scene featuring a rustic wooden dining table as the central element. The table appears to be made of natural oak with visible grain patterns and a warm finish. The surface shows natural character marks and has a slightly worn appearance. The table is positioned in a well-lit room with natural light coming from windows, creating soft shadows across the wooden surface...",
  "test_timestamp": "2025-08-05 17:10:00"
}
```

## 🎯 **What You're Collecting**

- **Detailed scene descriptions** from Qwen-VL-Max
- **Complete context** about surfaces, materials, lighting
- **Rich information** for analysis and app development
- **No comparison needed** - just pure vision model responses

## 📊 **Output Files**

After running the collector, you'll get:
- **Markdown Report**: Clean, readable format with all responses
- **JSON Data**: Structured data for programmatic use
- **Progress Tracking**: Shows completed vs pending tests

## 🚀 **Ready to Start Testing!**

1. Copy the detailed prompt above
2. Open your first image (1.png) in Qwen-VL-Max
3. Get the detailed response
4. Paste it into the JSON template
5. Repeat for all 20 images
6. Run the collector to see your results!
