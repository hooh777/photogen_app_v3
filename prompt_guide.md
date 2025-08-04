# 📝 PhotoGen Prompt Guide

## Quick Start

PhotoGen supports both **Text-to-Image** and **Image-to-Image** generation using FLUX models. This guide will help you craft effective prompts for the best results.

## 🎨 Text-to-Image Prompts

### Basic Structure
```
[Subject] [Action/Pose] [Setting/Environment] [Style] [Technical Details]
```

### Examples

**Portrait Photography:**
```
A professional headshot of a woman in her 30s, confident smile, office background, natural lighting, shot with 85mm lens, shallow depth of field
```

**Landscape:**
```
A serene mountain lake at golden hour, misty forest in background, calm water reflections, cinematic composition, ultra-wide angle
```

**Product Photography:**
```
A sleek smartphone on marble surface, dramatic side lighting, minimalist composition, commercial photography style, high contrast
```

## 🖼️ Image-to-Image Prompts

### Purpose
I2I prompts describe the **changes** you want to make, not the entire scene.

### Examples

**Adding Objects:**
```
A vintage leather bag sitting on the wooden table
```

**Changing Style:**
```
Transform to watercolor painting style, soft brushstrokes, artistic interpretation
```

**Lighting Changes:**
```
Dramatic sunset lighting, warm golden hour glow, long shadows
```

## 🎭 Style Keywords

### Photography Styles
- `professional photography`
- `commercial product shot`
- `street photography`
- `portrait photography`
- `macro photography`
- `architectural photography`

### Artistic Styles
- `oil painting`
- `watercolor`
- `digital art`
- `concept art`
- `anime style`
- `photorealistic`

### Mood & Atmosphere
- `cinematic`
- `dramatic`
- `moody`
- `ethereal`
- `vibrant`
- `minimalist`

## 🔧 Technical Parameters

### Lighting
- `natural lighting`
- `studio lighting`
- `golden hour`
- `blue hour`
- `dramatic lighting`
- `soft diffused light`

### Camera Settings
- `shallow depth of field`
- `sharp focus`
- `bokeh background`
- `wide angle`
- `telephoto lens`
- `macro lens`

### Quality Modifiers
- `high resolution`
- `ultra detailed`
- `8K quality`
- `professional grade`
- `award winning`

## ⚡ Pro Tips

### DO:
✅ Be specific about what you want  
✅ Use descriptive adjectives  
✅ Mention lighting and composition  
✅ Include style references  
✅ Keep prompts focused  

### DON'T:
❌ Use overly long prompts (>77 tokens)  
❌ Include contradictory descriptions  
❌ Repeat the same words multiple times  
❌ Use unclear or ambiguous terms  

## 🚀 Advanced Techniques

### Negative Prompting
While FLUX doesn't use traditional negative prompts, you can guide away from unwanted elements:
```
A clean, modern kitchen (avoid: cluttered, messy, outdated)
```

### Composition Control
```
Rule of thirds composition, leading lines, symmetrical balance, dynamic angle
```

### Color Schemes
```
Monochromatic blue palette, warm earth tones, high contrast black and white, pastel colors
```

## 🎯 Mode-Specific Tips

### Create Mode (T2I)
- Start with the main subject
- Add environment and context
- Specify style and mood
- Include technical details

### Demo Mode
- Use the template system
- Fill in object descriptions
- Customize position and lighting
- Adjust style and tone

### Edit Mode (I2I)
- Focus on the changes you want
- Use the auto-prompt feature for inspiration
- Consider the existing image context
- Be specific about object placement

## 🔄 Iteration Strategy

1. **Start Simple**: Begin with basic description
2. **Add Details**: Gradually add style, lighting, composition
3. **Refine**: Use AI enhancement for better prompts
4. **Experiment**: Try different approaches and styles

## 📚 Resources

- **FLUX Model Documentation**: Check Hugging Face for model-specific tips
- **Photography Terms**: Learn composition and lighting terminology
- **Art Styles**: Research different artistic movements and styles

---

*Happy prompting! 🎨*