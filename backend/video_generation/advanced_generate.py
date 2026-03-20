#!/usr/bin/env python3
"""
Advanced local video generation with templates and procedural animations
No API required - all processing is local
"""

import argparse
import sys
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import logging
import random
import math
from enum import Enum
import numpy as np

# Load environment variables from .env.local
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent.parent / '.env.local'
    load_dotenv(env_path)
except ImportError:
    pass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ================ UTILITY EFFECTS ================

class PerlinNoise2D:
    """Simple 2D Perlin noise implementation for natural textures"""
    def __init__(self, scale: int = 100):
        self.scale = scale
        self.permutation = list(range(256))
        random.shuffle(self.permutation)
        self.permutation += self.permutation  # Double for wraparound
    
    def dot_product_distance(self, gradient: Tuple, distance: Tuple) -> float:
        return gradient[0] * distance[0] + gradient[1] * distance[1]
    
    def interpolate(self, t: float) -> float:
        """Smooth interpolation"""
        return t * t * (3 - 2 * t)
    
    def perlin(self, x: float, y: float) -> float:
        """Get Perlin noise value at (x, y)"""
        x = x / self.scale % 256
        y = y / self.scale % 256
        
        xi = int(x) & 255
        yi = int(y) & 255
        
        xf = x - int(x)
        yf = y - int(y)
        
        # Grid points
        n00 = self.permutation[(self.permutation[xi] + yi) & 255]
        n01 = self.permutation[(self.permutation[xi] + yi + 1) & 255]
        n10 = self.permutation[(self.permutation[xi + 1] + yi) & 255]
        n11 = self.permutation[(self.permutation[xi + 1] + yi + 1) & 255]
        
        # Gradients
        grad = [(random.random() * 2 - 1, random.random() * 2 - 1) for _ in range(256)]
        
        u = self.interpolate(xf)
        v = self.interpolate(yf)
        
        n0 = n00 * (1 - u) + n10 * u
        n1 = n01 * (1 - u) + n11 * u
        return n0 * (1 - v) + n1 * v


def add_glow_effect(frame, radius: int = 15, intensity: float = 0.3):
    """Add glow/bloom effect to a frame (optimized with NumPy)"""
    from PIL import ImageFilter, Image
    import numpy as np
    
    if frame.mode != 'RGB':
        frame = frame.convert('RGB')
    
    # Create glow layer by blurring
    glow = frame.filter(ImageFilter.GaussianBlur(radius=radius))
    
    # Vectorized blending with NumPy (100x faster than pixel loops)
    orig_array = np.array(frame).astype(float)
    glow_array = np.array(glow).astype(float)
    
    blended = (orig_array * (1 - intensity) + glow_array * intensity).astype(np.uint8)
    return Image.fromarray(blended, 'RGB')


def add_atmospheric_particles(frame, count: int = 100, opacity: float = 0.15):
    """Add dust/haze particles floating in the scene"""
    from PIL import ImageDraw
    import numpy as np
    
    frame = frame.convert('RGBA')
    draw = ImageDraw.Draw(frame)
    
    width, height = frame.size
    
    # Create pseudo-random particles based on frame hash (consistent per frame)
    random.seed(hash(frame.tobytes()) % (2**32))
    
    for _ in range(count):
        x = random.randint(0, width)
        y = random.randint(0, height)
        size = random.randint(1, 5)
        
        # Particles are slightly lighter than background
        brightness = random.randint(200, 255)
        color = (brightness, brightness, brightness, int(255 * opacity))
        
        draw.ellipse([x - size, y - size, x + size, y + size], fill=color)
    
    return frame.convert('RGB')


def add_god_rays(frame, light_source_x: float = 0.8, light_source_y: float = 0.2, intensity: float = 0.15):
    """Add volumetric god rays effect from a light source"""
    from PIL import Image, ImageDraw
    import numpy as np
    
    frame = frame.convert('RGBA')
    width, height = frame.size
    
    # Create rays layer
    rays = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(rays)
    
    light_x = int(width * light_source_x)
    light_y = int(height * light_source_y)
    
    # Draw multiple rays from light source
    for i in range(40):
        angle = (i / 40) * 2 * math.pi
        end_x = int(light_x + width * math.cos(angle))
        end_y = int(light_y + height * math.sin(angle))
        
        alpha = int(100 * intensity * (1 - (i / 40) ** 0.5))  # Stronger rays fade quicker
        draw.line([(light_x, light_y), (end_x, end_y)], 
                 fill=(255, 255, 200, alpha), width=3)
    
    # Blend rays with original frame
    frame_array = np.array(frame).astype(float)
    rays_array = np.array(rays).astype(float)
    
    # Blend
    blended = (frame_array + rays_array * 0.3).astype(np.uint8)
    return Image.fromarray(blended, 'RGBA').convert('RGB')


def add_color_grading(frame, saturation: float = 1.2, contrast: float = 1.1, brightness: float = 1.0):
    """Apply color grading for better visuals"""
    from PIL import ImageEnhance
    
    # Adjust contrast
    enhancer = ImageEnhance.Contrast(frame)
    frame = enhancer.enhance(contrast)
    
    # Adjust saturation
    enhancer = ImageEnhance.Color(frame)
    frame = enhancer.enhance(saturation)
    
    # Adjust brightness
    enhancer = ImageEnhance.Brightness(frame)
    frame = enhancer.enhance(brightness)
    
    return frame


def add_vignette(frame, strength: float = 0.3):
    """Add vignette darkening to edges (optimized)"""
    from PIL import Image
    import numpy as np
    
    width, height = frame.size
    
    # Create vignette mask using numpy (MUCH faster)
    x = np.linspace(-1, 1, width)
    y = np.linspace(-1, 1, height)
    X, Y = np.meshgrid(x, y)
    
    # Calculate distance from center
    dist = np.sqrt(X**2 + Y**2)
    dist = np.minimum(dist / dist.max(), 1.0)
    
    # Create vignette
    vignette = 1 - (dist * strength)
    vignette = np.tile(vignette[:, :, np.newaxis], (1, 1, 3))
    
    # Apply vignette to frame
    frame_array = np.array(frame).astype(float)
    result = (frame_array * vignette).astype(np.uint8)
    
    return Image.fromarray(result, 'RGB')


# ================ VIDEO TEMPLATES ================



class VideoTemplate(Enum):
    """Available video templates"""
    GRADIENT_SUNSET = "gradient_sunset"
    GRADIENT_OCEAN = "gradient_ocean"
    GRADIENT_FOREST = "gradient_forest"
    GRADIENT_SPACE = "gradient_space"
    GRADIENT_CITY = "gradient_city"
    PARTICLE_STARS = "particle_stars"
    PARTICLE_RAIN = "particle_rain"
    ANIMATED_SHAPES = "animated_shapes"
    WAVES = "waves"
    RAINBOW = "rainbow"


class VideoGenerator:
    """Advanced local video generator with templates"""
    
    def __init__(self, output_path: str = 'output.mp4'):
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
    
    def parse_prompt(self, prompt: str) -> VideoTemplate:
        """Parse prompt and return matching template"""
        prompt_lower = prompt.lower()
        
        # Keywords for template selection
        templates = {
            "sunset": VideoTemplate.GRADIENT_SUNSET,
            "ocean": VideoTemplate.GRADIENT_OCEAN,
            "water": VideoTemplate.GRADIENT_OCEAN,
            "sea": VideoTemplate.GRADIENT_OCEAN,
            "mountain": VideoTemplate.GRADIENT_FOREST,
            "forest": VideoTemplate.GRADIENT_FOREST,
            "tree": VideoTemplate.GRADIENT_FOREST,
            "nature": VideoTemplate.GRADIENT_FOREST,
            "space": VideoTemplate.GRADIENT_SPACE,
            "star": VideoTemplate.PARTICLE_STARS,
            "night": VideoTemplate.GRADIENT_SPACE,
            "sky": VideoTemplate.GRADIENT_SPACE,
            "city": VideoTemplate.GRADIENT_CITY,
            "urban": VideoTemplate.GRADIENT_CITY,
            "rain": VideoTemplate.PARTICLE_RAIN,
            "storm": VideoTemplate.PARTICLE_RAIN,
            "wave": VideoTemplate.WAVES,
            "particle": VideoTemplate.PARTICLE_STARS,
            "shape": VideoTemplate.ANIMATED_SHAPES,
            "color": VideoTemplate.RAINBOW,
        }
        
        # Find matching template
        for keyword, template in templates.items():
            if keyword in prompt_lower:
                logger.info(f"Matched template: {template.value} (keyword: {keyword})")
                return template
        
        # Default to random if no match
        template = random.choice(list(VideoTemplate))
        logger.info(f"No match found, using random template: {template.value}")
        return template
    
    def generate_gradient_sunset(self, duration: int, fps: int = 24, width: int = 1280, height: int = 720) -> List:
        """Generate sunset gradient animation frames with enhanced effects"""
        from PIL import Image, ImageDraw
        
        frames = []
        total_frames = duration * fps
        
        for frame_num in range(total_frames):
            progress = frame_num / total_frames
            
            # Create image with multiple layers
            img = Image.new('RGB', (width, height))
            pixels = img.load()
            
            # Enhanced sunset gradient with more colors and depth
            for y in range(height):
                y_progress = y / height
                
                if y_progress < 0.25:  # Sky - deeper gradient
                    r = int(25 + (100 - 25) * y_progress / 0.25)
                    g = int(35 + (150 - 35) * y_progress / 0.25)
                    b = int(120 + (220 - 120) * y_progress / 0.25)
                elif y_progress < 0.5:  # Upper gradient
                    local_prog = (y_progress - 0.25) / 0.25
                    r = int(100 + (255 - 100) * local_prog)
                    g = int(150 + (180 - 150) * local_prog)
                    b = int(220 + (50 - 220) * local_prog)
                elif y_progress < 0.75:  # Sunset middle
                    local_prog = (y_progress - 0.5) / 0.25
                    phase = progress * 2 * math.pi
                    intensity = 0.6 + 0.4 * math.sin(phase)
                    r = int(255 * intensity)
                    g = int(140 * (1 - local_prog * 0.5) * intensity)
                    b = int(20 * (1 - local_prog) * intensity)
                else:  # Lower gradient - ocean/land
                    local_prog = (y_progress - 0.75) / 0.25
                    r = int(200 * (1 - local_prog * 0.5))
                    g = int(50 * (1 - local_prog * 0.3))
                    b = int(30 + local_prog * 50)
                
                for x in range(width):
                    pixels[x, y] = (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))
            
            # Add light rays from sun position
            if progress < 0.5:
                sun_x = 0.3 + progress * 0.2
                img = add_god_rays(img, light_source_x=sun_x, light_source_y=0.35, intensity=0.2)
            
            # Add animated wave effects with glow
            img = img.convert('RGBA')
            draw = ImageDraw.Draw(img)
            
            # Multiple wave layers for depth
            for wave_layer in range(3):
                offset = wave_layer * 20
                wave_speed = 2 + wave_layer * 0.5
                
                for x in range(0, width, 40):
                    wave_height = int(15 * math.sin(x / 120 + progress * wave_speed * math.pi) + 30 - offset)
                    wave_y = int(height * 0.45 - wave_height)
                    
                    # Glow effect - draw twice with opacity
                    draw.line([(x, wave_y), (x + 40, wave_y + int(math.sin((x + 40) / 120 + progress * wave_speed * math.pi) * 15 + 30 - offset))],
                             fill=(255, 200, 100, 80 - wave_layer * 20), width=3)
            
            # Add particles for depth - more and better animated
            for i in range(30):
                particle_x = int((progress * width + i * 50) % width)
                particle_y = int(height * 0.4 + 30 * math.sin(progress * 2 * math.pi + i))
                size = 2 + (i % 3)
                opacity = int(200 * (0.5 + 0.5 * math.sin(progress * 3 * math.pi + i)))
                draw.ellipse([particle_x - size, particle_y - size, particle_x + size, particle_y + size],
                            fill=(255, 255, 200, opacity))
            
            # Convert back and apply effects
            img = img.convert('RGB')
            img = add_vignette(img, strength=0.25)
            img = add_glow_effect(img, radius=12, intensity=0.25)
            img = add_atmospheric_particles(img, count=60, opacity=0.1)
            img = add_color_grading(img, saturation=1.3, contrast=1.15, brightness=1.05)
            
            frames.append(img)
        
        return frames
    
    def generate_particle_stars(self, duration: int, fps: int = 24, width: int = 1280, height: int = 720) -> List:
        """Generate animated starfield with glowing nebula and enhanced effects"""
        from PIL import Image, ImageDraw
        
        frames = []
        total_frames = duration * fps
        
        # Create persistent stars with colors
        stars = [(random.randint(0, width), random.randint(0, height), random.random(), random.choice(['white', 'blue', 'cyan', 'yellow', 'red']))
                for _ in range(300)]
        
        # Create nebula clouds
        nebulas = [(random.randint(0, width), random.randint(0, height), random.randint(60, 150))
                  for _ in range(5)]
        
        for frame_num in range(total_frames):
            progress = frame_num / total_frames
            
            # Dark space background with gradient
            img = Image.new('RGB', (width, height))
            pixels = img.load()
            
            # Gradient background - darker at edges
            for y in range(height):
                for x in range(width):
                    # Create a gradient that's darker at edges (vignette effect)
                    dx = (x - width / 2) / (width / 2)
                    dy = (y - height / 2) / (height / 2)
                    dist = math.sqrt(dx**2 + dy**2) * 0.5
                    brightness = max(3, int(15 - dist * 10))
                    pixels[x, y] = (brightness, brightness, brightness + 5)
            
            # Add light rays from top for more cinematic feel
            img = add_god_rays(img, light_source_x=0.5, light_source_y=-0.2, intensity=0.1)
            
            # Draw nebula
            img = img.convert('RGBA')
            draw = ImageDraw.Draw(img)
            
            for nx, ny, radius in nebulas:
                nebula_progress = (progress + random.random()) % 1.0
                moving_x = int(nx + 50 * math.sin(nebula_progress * 2 * math.pi))
                moving_y = int(ny + 30 * math.cos(nebula_progress * 2 * math.pi))
                
                # Multiple nebula layers for depth
                for layer in range(3):
                    r_mult = 1 - (layer / 3)
                    alpha = int(80 * (1 - layer / 3))
                    draw.ellipse([moving_x - radius * r_mult, moving_y - radius * r_mult,
                                moving_x + radius * r_mult, moving_y + radius * r_mult],
                               fill=(80 + layer * 30, 30 + layer * 40, 150 - layer * 30, alpha))
            
            # Draw stars with glow and colors
            for x, y, twinkle_phase, color in stars:
                brightness = int(255 * (0.3 + 0.7 * math.sin(twinkle_phase + progress * 5 * math.pi)))
                size = max(1, int(2 + 2 * math.sin(twinkle_phase + progress * 3 * math.pi)))
                
                # Color mapping
                if color == 'blue':
                    star_color = (brightness // 2, brightness // 2, brightness)
                elif color == 'cyan':
                    star_color = (brightness // 2, brightness, brightness)
                elif color == 'yellow':
                    star_color = (brightness, brightness, brightness // 2)
                elif color == 'red':
                    star_color = (brightness, brightness // 3, brightness // 4)
                else:  # white
                    star_color = (brightness, brightness, brightness)
                
                # Glow
                draw.ellipse([x - size - 2, y - size - 2, x + size + 2, y + size + 2],
                           fill=(star_color[0] // 3, star_color[1] // 3, star_color[2] // 3, 100))
                
                # Star core
                draw.ellipse([x - size, y - size, x + size, y + size],
                           fill=star_color + (255,))
            
            img = img.convert('RGB')
            img = add_glow_effect(img, radius=10, intensity=0.2)
            img = add_atmospheric_particles(img, count=40, opacity=0.08)
            img = add_color_grading(img, saturation=1.1, contrast=1.2, brightness=0.95)
            frames.append(img)
        
        return frames
    
    def generate_waves(self, duration: int, fps: int = 24, width: int = 1280, height: int = 720) -> List:
        """Generate animated wave pattern with reflections and enhanced effects"""
        from PIL import Image, ImageDraw
        
        frames = []
        total_frames = duration * fps
        
        for frame_num in range(total_frames):
            progress = frame_num / total_frames
            
            # Create gradient background
            img = Image.new('RGB', (width, height))
            pixels = img.load()
            
            # Water gradient background
            for y in range(height):
                y_prog = y / height
                r = int(10 + y_prog * 30)
                g = int(30 + y_prog * 50)
                b = int(80 + y_prog * 100)
                for x in range(width):
                    pixels[x, y] = (r, g, b)
            
            # Add god rays for dramatic effect
            img = add_god_rays(img, light_source_x=0.5, light_source_y=0.1, intensity=0.15)
            
            img = img.convert('RGBA')
            draw = ImageDraw.Draw(img)
            
            # Draw multiple wave layers with glow
            for layer in range(6):
                offset = layer * 30 + progress * 250
                base_color = 80 + layer * 25
                wave_amplitude = 80 - layer * 10
                
                points = []
                for x in range(0, width + 50, 50):
                    wave = math.sin((x + offset) / 100 + progress * 2 * math.pi)
                    y = int(height // 2 + wave_amplitude * wave + layer * 40 - 120)
                    points.append((x, y))
                
                if len(points) > 1:
                    # Glow layer
                    for i in range(len(points) - 1):
                        x1, y1 = points[i]
                        x2, y2 = points[i + 1]
                        draw.line([(x1, y1), (x2, y2)], fill=(base_color, base_color, 200, 100), width=6)
                    
                    # Main wave
                    for i in range(len(points) - 1):
                        x1, y1 = points[i]
                        x2, y2 = points[i + 1]
                        draw.line([(x1, y1), (x2, y2)], fill=(base_color + 50, base_color + 50, 255, 200), width=3)
            
            # Add caustic-like light patterns
            for i in range(15):
                caustic_x = int((progress * width + i * 100) % width)
                caustic_y = int(height * 0.6 + 40 * math.sin(progress * 2 * math.pi + i))
                draw.ellipse([caustic_x - 20, caustic_y - 10, caustic_x + 20, caustic_y + 10],
                           fill=(200, 230, 255, 80))
            
            img = img.convert('RGB')
            img = add_vignette(img, strength=0.15)
            img = add_glow_effect(img, radius=14, intensity=0.2)
            img = add_atmospheric_particles(img, count=50, opacity=0.12)
            img = add_color_grading(img, saturation=1.25, contrast=1.2, brightness=1.0)
            frames.append(img)
        
        return frames
    
    def generate_animated_shapes(self, duration: int, fps: int = 24, width: int = 1280, height: int = 720) -> List:
        """Generate animated geometric shapes with enhanced glowing effects"""
        from PIL import Image, ImageDraw
        
        frames = []
        total_frames = duration * fps
        
        for frame_num in range(total_frames):
            progress = frame_num / total_frames
            
            # Create dynamic background gradient
            img = Image.new('RGB', (width, height))
            pixels = img.load()
            
            for y in range(height):
                for x in range(width):
                    # Animated gradient based on progress
                    hue_shift = (progress * 360) % 360
                    r = int(30 + 40 * math.sin(hue_shift * math.pi / 180))
                    g = int(30 + 40 * math.sin((hue_shift + 120) * math.pi / 180))
                    b = int(50 + 40 * math.sin((hue_shift + 240) * math.pi / 180))
                    pixels[x, y] = (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))
            
            # Add dramatic lighting
            img = add_god_rays(img, light_source_x=0.5, light_source_y=0.5, intensity=0.1)
            
            img = img.convert('RGBA')
            draw = ImageDraw.Draw(img)
            
            center_x, center_y = width // 2, height // 2
            
            # Rotating polygons
            for poly in range(3):
                angle = progress * 2 * math.pi + (poly * 2 * math.pi / 3)
                radius = 150 + poly * 50
                sides = 5 + poly
                
                points = []
                for i in range(sides):
                    angle_i = angle + (i * 2 * math.pi / sides)
                    x = int(center_x + radius * math.cos(angle_i))
                    y = int(center_y + radius * math.sin(angle_i))
                    points.append((x, y))
                
                # Color based on position
                color = (150 + poly * 30, 100 + poly * 20, 200 - poly * 20)
                
                if len(points) > 1:
                    # Glow
                    for i in range(len(points)):
                        x1, y1 = points[i]
                        x2, y2 = points[(i + 1) % len(points)]
                        draw.line([(x1, y1), (x2, y2)], fill=(*color, 100), width=6)
                    
                    # Main outline
                    for i in range(len(points)):
                        x1, y1 = points[i]
                        x2, y2 = points[(i + 1) % len(points)]
                        draw.line([(x1, y1), (x2, y2)], fill=(*color, 255), width=2)
            
            # Expanding and contracting circles with glow
            for i in range(8):
                circle_progress = (progress + i / 8) % 1.0
                radius = int(30 + circle_progress * 200)
                opacity = int(255 * (1 - circle_progress))
                
                if opacity > 20:
                    color = (200, 100 + i * 10, 255 - i * 10)
                    # Glow
                    draw.ellipse([center_x - radius - 5, center_y - radius - 5,
                                center_x + radius + 5, center_y + radius + 5],
                               outline=(color[0], color[1], color[2], opacity // 3), width=3)
                    # Main
                    draw.ellipse([center_x - radius, center_y - radius,
                                center_x + radius, center_y + radius],
                               outline=(*color, opacity), width=2)
            
            # Particle effects
            for i in range(30):
                particle_angle = (progress * 2 * math.pi + i * 2 * math.pi / 30) % (2 * math.pi)
                particle_distance = 100 + progress * 150
                px = int(center_x + particle_distance * math.cos(particle_angle))
                py = int(center_y + particle_distance * math.sin(particle_angle))
                
                size = 2 + (i % 3)
                draw.ellipse([px - size, py - size, px + size, py + size],
                           fill=(255, 200, 100, 200))
            
            img = img.convert('RGB')
            img = add_glow_effect(img, radius=13, intensity=0.25)
            img = add_atmospheric_particles(img, count=70, opacity=0.15)
            img = add_color_grading(img, saturation=1.4, contrast=1.25, brightness=1.1)
            frames.append(img)
        
        return frames
    
    def add_text_overlay(self, frames: List, text: str, font_size: int = 60) -> List:
        """Add animated text overlay to frames with better styling"""
        from PIL import ImageDraw, ImageFont
        
        for frame_num, frame in enumerate(frames):
            progress = frame_num / len(frames)
            
            # Convert to RGBA if needed
            if frame.mode != 'RGBA':
                frame = frame.convert('RGBA')
            
            draw = ImageDraw.Draw(frame)
            
            # Animate text opacity and scale
            alpha = int(255 * math.sin(progress * math.pi) ** 0.5)  # Smoother fade
            scale = 0.8 + 0.15 * math.sin(progress * 2 * math.pi)
            
            # Try to use a font, fall back to default if not available
            try:
                font = ImageFont.truetype("arial.ttf", int(font_size * scale))
            except:
                font = ImageFont.load_default()
            
            # Get text bounding box
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Center text
            x = (frame.width - text_width) // 2
            y = (frame.height - text_height) // 2
            
            # Add background blur/glow effect
            for offset in range(5, 0, -1):
                shadow_alpha = int(alpha * (1 - offset / 5) * 0.3)
                draw.text((x + offset, y + offset), text, font=font, fill=(0, 0, 0, shadow_alpha))
            
            # Draw text with shadow for depth
            draw.text((x + 2, y + 2), text, font=font, fill=(0, 0, 0, alpha // 2))
            draw.text((x, y), text, font=font, fill=(255, 255, 255, alpha))
            
            # Convert back to RGB for video encoding
            frames[frame_num] = frame.convert('RGB')
        
        return frames
    
    def save_video(self, frames: List, fps: int = 24) -> bool:
        """Save frames as video"""
        try:
            from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
            import numpy as np
            
            logger.info(f"Creating video with {len(frames)} frames at {fps} fps")
            
            # Convert PIL images to numpy arrays
            frame_arrays = [np.array(frame) for frame in frames]
            
            # Create video clip
            video = ImageSequenceClip(frame_arrays, fps=fps)
            
            # Write video file
            logger.info(f"Encoding video: {self.output_path}")
            video.write_videofile(str(self.output_path), codec='libx264')
            
            logger.info(f"✓ Video saved successfully: {self.output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving video: {e}", exc_info=True)
            return False
    
    def generate(self, prompt: str, duration: int = 10, fps: int = 24, 
                width: int = 1280, height: int = 720) -> bool:
        """Generate video from prompt"""
        try:
            logger.info(f"Generating video from prompt: {prompt}")
            logger.info(f"Duration: {duration}s, Resolution: {width}x{height}")
            
            # Parse prompt to get template
            template = self.parse_prompt(prompt)
            
            # Generate frames based on template
            if template == VideoTemplate.GRADIENT_SUNSET:
                frames = self.generate_gradient_sunset(duration, fps, width, height)
            elif template == VideoTemplate.PARTICLE_STARS:
                frames = self.generate_particle_stars(duration, fps, width, height)
            elif template == VideoTemplate.WAVES:
                frames = self.generate_waves(duration, fps, width, height)
            elif template == VideoTemplate.ANIMATED_SHAPES:
                frames = self.generate_animated_shapes(duration, fps, width, height)
            else:
                # Default to sunset for unknown templates
                frames = self.generate_gradient_sunset(duration, fps, width, height)
            
            logger.info(f"Generated {len(frames)} frames")
            
            # Add text overlay
            # Extract main keywords from prompt for display
            text = prompt[:50]  # First 50 chars
            frames = self.add_text_overlay(frames, text)
            
            # Save as video
            return self.save_video(frames, fps)
            
        except Exception as e:
            logger.error(f"Error generating video: {e}", exc_info=True)
            return False


def main():
    """CLI interface"""
    parser = argparse.ArgumentParser(
        description='Advanced local video generation with templates - No API required'
    )
    
    parser.add_argument(
        '--prompt',
        type=str,
        required=True,
        help='Video description (keywords: sunset, ocean, forest, space, stars, rain, waves, etc.)'
    )
    parser.add_argument(
        '--duration',
        type=int,
        default=10,
        help='Video duration in seconds (default: 10)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='output.mp4',
        help='Output video file path'
    )
    parser.add_argument(
        '--width',
        type=int,
        default=1280,
        help='Video width in pixels (default: 1280)'
    )
    parser.add_argument(
        '--height',
        type=int,
        default=720,
        help='Video height in pixels (default: 720)'
    )
    parser.add_argument(
        '--fps',
        type=int,
        default=24,
        help='Frames per second (default: 24)'
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    if len(args.prompt) < 5:
        logger.error("Prompt must be at least 5 characters")
        sys.exit(1)
    
    if args.duration < 1 or args.duration > 300:
        logger.error("Duration must be between 1 and 300 seconds")
        sys.exit(1)
    
    # Generate video
    generator = VideoGenerator(output_path=args.output)
    success = generator.generate(
        prompt=args.prompt,
        duration=args.duration,
        fps=args.fps,
        width=args.width,
        height=args.height
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
