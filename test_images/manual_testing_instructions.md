# Manual Vision Model Testing Instructions

## Overview
Since we're having dependency issues with the automated testing, here's how to manually test your vision model on the 20 images.

## Testing Process

### Step 1: Prepare Your Vision Model
- Open your vision model interface (Qwen-VL-Max)
- Make sure you have access to the `test_images` folder
- Have the testing template open: `manual_testing_template.json`

### Step 2: Test Each Image
For each image (`1.png` through `20.png`):

1. **Load the image** into your vision model
2. **Use this exact prompt**: 
   ```
   Describe SURFACE TYPE only, Format: 'on the [surface type]'
   ```
3. **Record the response** in the JSON template
4. **Add timestamp** when you tested it
5. **Add notes** if needed (e.g., "unclear response", "perfect match", etc.)

### Step 3: Expected Format
The model should respond with something like:
- "on the wooden surface"
- "on the marble surface"  
- "on the grass surface"
- "on the concrete surface"

### Step 4: Complete the Template
Replace all `ENTER_MODEL_RESPONSE_HERE` entries with actual responses from your model.

### Step 5: Generate Report
When done, run:
```bash
python debug/process_manual_results.py
```

## Quality Guidelines
- ✅ **Perfect**: Exact format "on the [material] surface"
- ⚠️ **Good**: Correct material but different wording
- ❌ **Poor**: Wrong material or includes room/furniture names

## Example Entry
```json
{
  "image_number": 1,
  "filename": "1.png",
  "prompt_used": "Describe SURFACE TYPE only, Format: 'on the [surface type]'",
  "actual_result": "on the wooden surface",
  "notes": "Perfect response, clear wood grain visible",
  "test_timestamp": "2025-08-05 16:15:00"
}
```

## Files Created
- `manual_testing_template.json` - Fill this out with your results
- `manual_testing_instructions.md` - This instruction file

Happy testing! 🧪
