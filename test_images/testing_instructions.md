# Vision Model Testing Instructions

## Testing Objectives:
1. **Scene Description Accuracy**: Test if model captures overall scene context
2. **Surface Material Detection**: Test if model identifies primary surface materials correctly
3. **Format Consistency**: Test if model follows expected format: "on the [surface type]"
4. **Priority Handling**: For complex scenes, test which surface the model prioritizes

## Test Execution:
1. Load each test image into your vision model
2. Use your current prompt: "Describe SURFACE TYPE only, Format: 'on the [surface type]'"
3. Record the actual output for each image
4. Compare with expected outputs in this file

## Success Criteria:
- ✅ **Perfect Match**: Output exactly matches expected format
- ⚠️  **Partial Match**: Correct surface type but different wording
- ❌ **Miss**: Wrong surface type or includes room/furniture names
- 🔄 **Complex**: For complex scenes, any reasonable surface detection is acceptable

## Scoring:
- Perfect Matches: 3 points each
- Partial Matches: 2 points each  
- Complex Reasonable: 2 points each
- Misses: 0 points each
- Total Possible: 60 points (assuming all simple/medium get perfect matches)

## Key Testing Areas:

### Surface Material Variety:
- Wood (tables, floors, decks)
- Stone/Rock (natural, paved)
- Fabric (sofa, carpet)
- Glass (tables, surfaces)  
- Concrete (floors, patios)
- Ceramic/Tile (counters, floors)
- Metal (if included)
- Natural (grass, sand)

### Scene Complexity:
- **Simple**: Single clear surface (Images 1-5, 11-15)
- **Medium**: Some complexity but clear primary surface (Images 6-8, 13, 16, 18-20)
- **Complex**: Multiple competing surfaces (Images 9-10, 16-17)

### Environment Types:
- **Indoor Professional**: Kitchen, office, bathroom
- **Indoor Residential**: Living room, bedroom, dining
- **Outdoor Natural**: Grass, sand, stone, wood
- **Outdoor Built**: Concrete, brick, asphalt, paving

## Expected Model Behavior:
1. Should focus on SURFACE ONLY, not describe rooms/furniture
2. Should use format "on the [surface material] surface"
3. For complex scenes, should pick the most prominent/relevant surface
4. Should handle lighting variations (natural, artificial, mixed)
5. Should distinguish between similar materials (wood table vs wood floor)
