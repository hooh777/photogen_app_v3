# Vision Model Test Images Summary

## Quick Reference:
- **Total Images**: 20
- **Categories**: indoor_tables_surfaces, indoor_floors_complex, outdoor_natural, outdoor_mixed_complex
- **Complexity Levels**: Simple, Medium, Complex
- **Expected Formats**: "on the [material] surface"

## Image Categories:
- **Indoor Tables Surfaces**: 5 images
- **Indoor Floors Complex**: 5 images
- **Outdoor Natural**: 5 images
- **Outdoor Mixed Complex**: 5 images

## Files Created:
- `test_plan.json`: Complete test specification
- `testing_instructions.md`: Detailed testing guidelines  
- `test_summary.md`: This quick reference

## Next Steps:
1. Collect/photograph the 20 images according to the test plan
2. Save them in test_images/ folder with the specified filenames
3. Run your vision model on each image
4. Record results and compare with expected outputs
5. Calculate accuracy score based on success criteria

## Sample Expected Outputs:
- Wooden dining table → "on the wooden surface"
- Marble counter → "on the marble surface"  
- Grass lawn → "on the grass surface"
- Concrete patio → "on the concrete surface"
