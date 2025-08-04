# Qwen-VL-Max Setup Guide

## Overview
You've successfully integrated **Qwen-VL-Max** from Alibaba Cloud into your PhotoGen application! This is currently the most advanced vision model available, matching GPT-4V and Gemini Ultra performance.

## What Qwen-VL-Max Can Do For Your Use Case

For your landscape image with blue selection box scenario:

### ✅ **Background Analysis**
- "A pastoral landscape with rolling green fields and scattered trees under natural daylight"
- Identifies scene composition, lighting conditions, and environmental context

### ✅ **Selection Box Location**
- "The blue selection box is positioned over natural grass in the foreground area"
- Understands spatial relationships and relative positioning

### ✅ **Surface Material Detection**
- Converts to placement format: "in the grass area", "on the stone surface", "on the wooden table"
- Perfect for your image editing workflow

## Getting Your Alibaba Cloud API Key

### Step 1: Create Alibaba Cloud Account
1. Go to [Alibaba Cloud Console](https://ecs.console.aliyun.com/)
2. Sign up or log in to your account
3. Complete identity verification if required

### Step 2: Enable DashScope Service
1. Navigate to [DashScope Console](https://dashscope.console.aliyun.com/)
2. Click "Activate Service" if not already enabled
3. Choose your pricing plan (Free tier available)

### Step 3: Generate API Key
1. In DashScope Console, go to "API Keys" section
2. Click "Create API Key"
3. Copy the generated key (starts with `sk-`)
4. **Important**: Store this key securely - you won't see it again!

### Step 4: Configure PhotoGen
1. Launch your PhotoGen application
2. Open "⚙️ AI Vision / Enhancer Settings"
3. Select "Qwen-VL-Max (Alibaba Cloud)" from the dropdown
4. Paste your API key and click "Save Key"

## Testing Your Setup

### Basic Test
1. Go to "Edit" tab in PhotoGen
2. Upload an image (like your landscape photo)
3. Click twice to create a selection box
4. Click "🤖 Auto-Generate Prompt"
5. You should see detailed analysis like:
   > "Background: A pastoral landscape with green fields and trees. Selection: in the grass area"

### Advanced Test
Try different image types:
- **Indoor scenes**: Should detect furniture, lighting, materials
- **Urban environments**: Should identify buildings, streets, architectural elements  
- **Natural landscapes**: Should recognize terrain, vegetation, water features

## Performance Expectations

### Speed
- **Analysis time**: 2-5 seconds per image
- **Accuracy**: State-of-the-art vision understanding
- **Rate limits**: Check your DashScope plan limits

### Quality
- **Spatial awareness**: Excellent at describing object locations
- **Material detection**: Very accurate surface type identification
- **Scene understanding**: Comprehensive environmental context

## API Usage & Costs

### Free Tier
- Usually includes thousands of free API calls per month
- Perfect for testing and small projects

### Paid Tiers
- Pay-per-use pricing
- Check [DashScope Pricing](https://help.aliyun.com/zh/dashscope/product-overview/billing-guide/) for current rates

## Troubleshooting

### Common Issues

**"API Error: 401"**
- Check your API key is correct
- Ensure DashScope service is activated
- Verify your account has sufficient credits

**"API Error: 429"**
- You've hit rate limits
- Wait a few minutes and try again
- Consider upgrading your plan

**"Empty response from Qwen-VL-Max"**
- Image might be too large or corrupted
- Try a different image format (PNG recommended)
- Check your internet connection

### Debug Mode
Enable detailed logging by checking the console output for:
```
INFO: Qwen-VL-Max analysis: Full description: '[detailed analysis]'
INFO: Qwen-VL-Max placement: '[surface description]'
```

## Fallback Options

If Qwen-VL-Max is unavailable, your system will automatically:
1. Return a generic surface description
2. Still allow manual prompt editing
3. Maintain all other PhotoGen functionality

## Support Resources

- [Alibaba Cloud DashScope Documentation](https://help.aliyun.com/zh/dashscope/)
- [Qwen-VL-Max Model Details](https://qianwen.aliyun.com/)
- [API Reference](https://help.aliyun.com/zh/dashscope/developer-reference/vl-plus-quick-start/)

## Next Steps

1. **Test with your landscape images** - Try the blue box selection workflow
2. **Experiment with different scenes** - Indoor, urban, natural environments
3. **Monitor API usage** - Check your DashScope console for usage statistics
4. **Optimize prompts** - The better your base prompts, the better the enhancement

Your PhotoGen application now has access to one of the world's most advanced vision AI systems! 🚀
