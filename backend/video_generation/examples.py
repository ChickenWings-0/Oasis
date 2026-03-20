"""
Example usage of the video generation models
"""

from generate_video import generate_video
from models import get_model

# ============================================================================
# EXAMPLE 1: Simple Text-Based Generation (No API Key Required)
# ============================================================================
def example_simple_generation():
    """Basic text-based video generation - fast and free"""
    success = generate_video(
        prompt="A colorful gradient background with inspiring text",
        duration=10,
        output_path="outputs/simple_video.mp4",
        fps=24,
        resolution=(1280, 720)
    )
    print(f"Simple generation: {'✓ Success' if success else '✗ Failed'}")


# ============================================================================
# EXAMPLE 2: HuggingFace API Generation (AI-Powered)
# ============================================================================
def example_huggingface_generation():
    """
    Generate video using HuggingFace API
    Requires: export HF_TOKEN="your_token_here"
    """
    success = generate_video(
        prompt="A beautiful landscape with mountains and river under sunset",
        model_type="huggingface",
        model_id="cerspense/zeroscope_v2_XL",
        output_path="outputs/ai_video_xl.mp4",
        num_inference_steps=25
    )
    print(f"HuggingFace generation: {'✓ Success' if success else '✗ Failed'}")


# ============================================================================
# EXAMPLE 3: Using Model Class Directly
# ============================================================================
def example_model_class():
    """Direct usage of model classes"""
    
    # Create model instance
    model = get_model(
        model_type="huggingface",
        model_id="cerspense/zeroscope_v2_576w"  # Faster variant
    )
    
    # Generate video
    result = model.generate(
        prompt="A robot dancing in a futuristic city",
        num_inference_steps=20,
        output_path="outputs/robot_dance.mp4"
    )
    
    # Check results
    if result['success']:
        print(f"✓ Video generated: {result['output_path']}")
        print(f"  Metadata: {result['metadata']}")
    else:
        print(f"✗ Error: {result['error']}")


# ============================================================================
# EXAMPLE 4: Batch Processing Multiple Prompts
# ============================================================================
def example_batch_processing():
    """Generate multiple videos in sequence"""
    
    prompts = [
        "A cat sitting by a sunny window",
        "A sailboat on calm blue ocean",
        "A garden full of blooming flowers"
    ]
    
    results = []
    for i, prompt in enumerate(prompts, 1):
        print(f"\nGenerating video {i}/{len(prompts)}: {prompt[:50]}...")
        
        success = generate_video(
            prompt=prompt,
            model_type="huggingface",
            model_id="cerspense/zeroscope_v2_576w",
            output_path=f"outputs/batch_video_{i}.mp4",
            num_inference_steps=20
        )
        
        results.append({
            'prompt': prompt,
            'success': success,
            'output': f"outputs/batch_video_{i}.mp4"
        })
    
    print("\n=== Batch Processing Results ===")
    for r in results:
        status = "✓ Success" if r['success'] else "✗ Failed"
        print(f"{status}: {r['prompt'][:40]}...")


# ============================================================================
# EXAMPLE 5: Model Comparison
# ============================================================================
def example_model_comparison():
    """Compare different models with the same prompt"""
    
    prompt = "A spaceship flying through a nebula"
    
    models_to_test = [
        ("cerspense/zeroscope_v2_576w", 20, "Fast/Low Quality"),
        ("cerspense/zeroscope_v2_XL", 25, "High Quality"),
        ("damo-vilab/text-to-video-ms-1.7b", 30, "Alternative"),
    ]
    
    print(f"Testing models with prompt: '{prompt}'\n")
    
    for model_id, steps, description in models_to_test:
        print(f"Testing {description}: {model_id}")
        print(f"  Steps: {steps}")
        
        result = get_model(
            model_type="huggingface",
            model_id=model_id
        ).generate(
            prompt=prompt,
            num_inference_steps=steps,
            output_path=f"outputs/compare_{model_id.split('/')[-1]}.mp4"
        )
        
        if result['success']:
            metadata = result['metadata']
            print(f"  ✓ Generated - Size: {metadata.get('file_size', 'N/A')} bytes")
        else:
            print(f"  ✗ Failed - {result['error']}")
        print()


# ============================================================================
# EXAMPLE 6: Error Handling
# ============================================================================
def example_error_handling():
    """Demonstrates proper error handling"""
    
    try:
        result = get_model(
            model_type="huggingface",
            model_id="cerspense/zeroscope_v2_XL"
        ).generate(
            prompt="A test video",
            output_path="outputs/test.mp4"
        )
        
        if result['success']:
            print(f"✓ Success!")
            print(f"  Output: {result['output_path']}")
            print(f"  Metadata: {result['metadata']}")
        else:
            print(f"✗ Generation failed")
            print(f"  Error: {result['error']}")
            
            # Implement retry logic
            print("  Retrying with fallback model...")
            result = generate_video(
                prompt="A test video",
                output_path="outputs/fallback.mp4"  # Fallback to simple generation
            )
            
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    # Create outputs directory
    Path("outputs").mkdir(exist_ok=True)
    
    print("Video Generation Examples")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        example_name = sys.argv[1]
        
        if example_name == "simple":
            example_simple_generation()
        elif example_name == "huggingface":
            example_huggingface_generation()
        elif example_name == "model_class":
            example_model_class()
        elif example_name == "batch":
            example_batch_processing()
        elif example_name == "compare":
            example_model_comparison()
        elif example_name == "error":
            example_error_handling()
        else:
            print(f"Unknown example: {example_name}")
            print("\nAvailable examples:")
            print("  python examples.py simple")
            print("  python examples.py huggingface")
            print("  python examples.py model_class")
            print("  python examples.py batch")
            print("  python examples.py compare")
            print("  python examples.py error")
    else:
        print("\nUsage: python examples.py <example_name>\n")
        print("Available examples:")
        print("  simple         - Simple text-based generation")
        print("  huggingface    - HuggingFace API generation")
        print("  model_class    - Direct model class usage")
        print("  batch          - Batch processing multiple prompts")
        print("  compare        - Compare different models")
        print("  error          - Error handling patterns")
        print("\nExample: python examples.py simple")
