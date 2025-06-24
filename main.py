from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import os
import anthropic
from typing import Optional
import uvicorn
import random
import time

# Simple models for basic functionality
class SignupRequest(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    message: str

class ScriptGenerationRequest(BaseModel):
    user_email: str
    topic: str
    platform: str
    duration: int  # in seconds
    audience: Optional[str] = ""
    tone: str = "engaging"
    style: str = "educational"

class ScriptResponse(BaseModel):
    script: str
    metadata: dict

# Create FastAPI app
app = FastAPI(
    title="AI Script Strategist API",
    version="1.0.0",
    description="Simple backend for AI Script Strategist"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic routes
@app.get("/")
async def root():
    return {
        "message": "AI Script Strategist API", 
        "version": "1.0.0", 
        "status": "running",
        "environment_check": {
            "supabase_url": "✅" if os.getenv("SUPABASE_URL") else "❌",
            "supabase_key": "✅" if os.getenv("SUPABASE_KEY") else "❌",
            "jwt_secret": "✅" if os.getenv("JWT_SECRET_KEY") else "❌",
            "claude_api_key": "✅" if os.getenv("CLAUDE_API_KEY") else "❌"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AI Script Strategist API"}

# Simple auth endpoints (mock for now)
@app.post("/api/v1/auth/signup", response_model=UserResponse)
async def signup(request: SignupRequest):
    """Simple signup endpoint - returns success for any valid email"""
    try:
        # Basic validation
        if not request.email or "@" not in request.email:
            raise HTTPException(status_code=400, detail="Invalid email format")
        
        if not request.password or len(request.password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
        
        # Mock successful signup
        return UserResponse(
            id="user_123",
            email=request.email,
            message="User registered successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/auth/login", response_model=UserResponse)
async def login(request: LoginRequest):
    """Simple login endpoint - returns success for any valid credentials"""
    try:
        # Basic validation
        if not request.email or "@" not in request.email:
            raise HTTPException(status_code=400, detail="Invalid email format")
        
        if not request.password:
            raise HTTPException(status_code=400, detail="Password is required")
        
        # Mock successful login
        return UserResponse(
            id="user_123",
            email=request.email,
            message="Login successful"
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/api/v1/scripts")
async def get_scripts():
    """Simple scripts endpoint"""
    return {
        "scripts": [],
        "message": "Scripts endpoint working",
        "total": 0
    }

@app.get("/api/v1/test")
async def test_endpoint():
    """Test endpoint to verify API is working"""
    return {
        "status": "success",
        "message": "API is working correctly",
        "timestamp": "2025-06-24",
        "endpoints": [
            "/",
            "/health", 
            "/api/v1/auth/signup",
            "/api/v1/auth/login",
            "/api/v1/scripts",
            "/api/v1/scripts/generate",
            "/api/v1/test"
        ]
    }

def generate_video_script(topic: str, platform: str, duration: int, audience: str, tone: str, style: str) -> str:
    """Generate a video script using Claude AI"""
    
    # Initialize Claude
    claude_api_key = os.getenv("CLAUDE_API_KEY")
    if not claude_api_key or claude_api_key == "your-claude-api-key-here":
        # Fallback to template if no valid API key
        return generate_template_script(topic, platform, duration, audience, tone, style)
    
    try:
        # Configure Claude client
        client = anthropic.Anthropic(api_key=claude_api_key)
        
        # Create detailed prompt for specific content generation
        prompt = f"""You are an expert video script writer specializing in {platform} content. Create a highly specific, detailed, and actionable video script for the following parameters:

TOPIC: {topic}
PLATFORM: {platform}
DURATION: {duration} seconds
TARGET AUDIENCE: {audience}
TONE: {tone}
STYLE: {style}

CRITICAL REQUIREMENTS:
1. Generate SPECIFIC, DETAILED content related to the exact topic - absolutely NO generic placeholders
2. Include actual facts, techniques, steps, code examples, or insights specific to the topic
3. Use platform-specific language and format optimized for {platform}
4. Time each section precisely to total exactly {duration} seconds
5. Include specific examples, actionable advice, or real-world applications
6. Make it engaging for {audience} with {tone} tone
7. Use {style} approach throughout
8. NO placeholders like [insert example] or [explain concept] - everything must be specific and complete

PLATFORM OPTIMIZATION FOR {platform.upper()}:
- YouTube: Strong hook, clear structure, engagement prompts
- TikTok: Fast-paced, trending language, visual cues
- Instagram: Story-driven, aesthetic language, save-worthy content
- LinkedIn: Professional insights, industry relevance, thought leadership

STRUCTURE (time precisely for {duration} seconds):
- Hook (first 3-5 seconds): Specific attention-grabbing statement about the topic
- Introduction (5-10 seconds): Brief specific intro to what you'll cover
- Main Content (70-80% of duration): Detailed, specific information with real examples
- Call to Action (last 5-10 seconds): Specific engagement request related to the topic

OUTPUT FORMAT:
🎬 {platform.upper()} SCRIPT - {duration}s

📋 SCRIPT DETAILS:
• Topic: {topic}
• Platform: {platform.title()}
• Duration: {duration} seconds
• Target: {audience}
• Tone: {tone.title()}
• Style: {style.title()}

[Then provide the complete, specific script with exact timing and real content]

REMEMBER: This must be immediately usable without any editing. Include real facts, specific techniques, actual examples, and concrete advice. NO generic placeholders whatsoever."""

        # Generate content with Claude
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=2000,
            temperature=0.7,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        if response and response.content and len(response.content) > 0:
            return response.content[0].text
        else:
            return generate_template_script(topic, platform, duration, audience, tone, style)
            
    except Exception as e:
        print(f"Claude API error: {e}")
        # Fallback to template on error
        return generate_template_script(topic, platform, duration, audience, tone, style)

def generate_template_script(topic: str, platform: str, duration: int, audience: str, tone: str, style: str) -> str:
    """Fallback template-based script generation"""
    
    # Platform-specific optimizations
    platform_tips = {
        "youtube": {
            "hook": "Strong opening hook in first 15 seconds",
            "structure": "Introduction → Main content → Call to action",
            "engagement": "Ask viewers to like, subscribe, and comment"
        },
        "tiktok": {
            "hook": "Immediate visual impact, trending sounds",
            "structure": "Quick hook → Fast-paced content → Strong ending",
            "engagement": "Use trending hashtags and challenges"
        },
        "instagram": {
            "hook": "Eye-catching visuals, story-driven",
            "structure": "Visual storytelling → Key message → CTA",
            "engagement": "Encourage saves, shares, and comments"
        },
        "linkedin": {
            "hook": "Professional insight or industry trend",
            "structure": "Problem → Solution → Professional insight",
            "engagement": "Encourage professional discussion"
        }
    }
    
    # Duration-based structure
    if duration <= 30:
        structure = "Quick hook (3s) → Main message (20s) → CTA (7s)"
    elif duration <= 60:
        structure = "Hook (5s) → Introduction (10s) → Main content (35s) → CTA (10s)"
    elif duration <= 90:
        structure = "Hook (5s) → Intro (10s) → Main content (60s) → Conclusion (10s) → CTA (5s)"
    else:  # 3 minutes
        structure = "Hook (10s) → Intro (20s) → Main content (120s) → Examples (20s) → Conclusion (10s)"
    
    platform_info = platform_tips.get(platform, platform_tips["youtube"])
    
    # Generate script based on parameters
    script_templates = [
        f"""🎬 VIDEO SCRIPT - {platform.upper()}
📝 Topic: {topic}
⏱️ Duration: {duration} seconds
🎯 Audience: {audience or 'General audience'}
🎭 Tone: {tone.title()}
📋 Style: {style.title()}

═══════════════════════════════════════

🔥 HOOK (First {5 if duration > 30 else 3} seconds):
"Did you know that {topic.lower()} could completely change the way you think about [relevant area]? Stay tuned because I'm about to share something that will blow your mind!"

📖 INTRODUCTION ({10 if duration > 60 else 5} seconds):
"Hey everyone! Welcome back to my channel. Today we're diving deep into {topic}. Whether you're a beginner or already familiar with this topic, I guarantee you'll learn something new by the end of this video."

💡 MAIN CONTENT ({duration - 25 if duration > 60 else duration - 15} seconds):
Let me break down {topic} into {3 if duration > 90 else 2} key points that you need to know:

Point 1: The Foundation
{topic} is fundamentally about [explain core concept]. This is crucial because it affects [relevant impact]. Here's a practical example: [provide specific example].

{"Point 2: The Application" if duration > 60 else ""}
{"Now, how do you actually apply this? The key is to [provide actionable advice]. Many people make the mistake of [common mistake], but the right approach is [correct method]." if duration > 60 else ""}

{"Point 3: Advanced Insights" if duration > 90 else ""}
{"For those ready to take it to the next level, consider [advanced tip]. This separates beginners from experts in [relevant field]." if duration > 90 else ""}

🎯 CALL TO ACTION ({10 if duration > 60 else 7} seconds):
"If you found this helpful, {platform_info['engagement']}. What's your experience with {topic}? Let me know in the comments below!"

{"📱 PLATFORM-SPECIFIC NOTES:" if platform != "youtube" else ""}
{f"• {platform_info['hook']}" if platform != "youtube" else ""}
{f"• {platform_info['structure']}" if platform != "youtube" else ""}
{f"• {platform_info['engagement']}" if platform != "youtube" else ""}

═══════════════════════════════════════
✨ PRODUCTION TIPS:
• Keep energy high throughout
• Use visual aids and graphics
• Include relevant B-roll footage
• Maintain good lighting and audio quality
• Edit with jump cuts to maintain pace

🏷️ SUGGESTED HASHTAGS:
#{topic.replace(' ', '').lower()} #content #education #tips #viral #trending""",

        f"""🎥 {platform.upper()} SCRIPT GENERATOR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 SCRIPT DETAILS:
• Topic: {topic}
• Platform: {platform.title()}
• Duration: {duration}s
• Target: {audience or 'General viewers'}
• Tone: {tone.title()}
• Style: {style.title()}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 OPENING HOOK ({3 if duration <= 30 else 5} seconds):
*[Visual: Eye-catching graphic or action]*
"Stop scrolling! In the next {duration} seconds, I'm going to show you everything you need to know about {topic} that most people get completely wrong."

🎯 INTRODUCTION ({5 if duration <= 60 else 10} seconds):
*[Visual: Host on camera, confident and energetic]*
"What's up everyone! Today we're tackling {topic}, and I'm going to give you the {tone} breakdown that will change your perspective forever."

💎 MAIN CONTENT SECTION:
*[Visual: Mix of talking head, graphics, and demonstrations]*

{f"🔑 Key Point 1 ({(duration-20)//2} seconds):" if duration > 60 else f"🔑 Main Message ({duration-15} seconds):"}
"Let's start with the most important thing about {topic}: [core insight]. This is game-changing because [explain impact]. Here's exactly how it works..."

*[Visual: Demonstration or example]*
"For example, [specific example that relates to audience]. This is why [explain benefit]."

{f"🔑 Key Point 2 ({(duration-20)//2} seconds):" if duration > 60 else ""}
{f"Now, here's what most people don't realize about {topic}: [second insight]. The secret is [actionable tip]. Watch this..." if duration > 60 else ""}

{f"*[Visual: Another demonstration]*" if duration > 60 else ""}
{f"See how [explain what happened]? That's the power of understanding {topic} properly." if duration > 60 else ""}

🎬 CLOSING & CTA ({7 if duration <= 60 else 10} seconds):
*[Visual: Back to host, call-to-action graphics]*
"And that's how you master {topic}! If this helped you, {platform_info['engagement']}. Drop a comment and tell me: what's your biggest challenge with {topic}?"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 SCRIPT NOTES:
• Maintain {tone} tone throughout
• Use {style} approach for content delivery
• Include visual cues for editor
• Keep pace energetic and engaging
• End with strong call-to-action

🎨 VISUAL SUGGESTIONS:
• Dynamic text overlays for key points
• Smooth transitions between sections
• Relevant stock footage or graphics
• Consistent branding elements
• {platform_info['hook']}

📊 ENGAGEMENT STRATEGY:
• Hook viewers in first 3 seconds
• Provide immediate value
• Use pattern interrupts
• Include interactive elements
• {platform_info['engagement']}"""
    ]
    
    # Select random template and customize
    selected_template = random.choice(script_templates)
    
    return selected_template

@app.post("/api/v1/scripts/generate", response_model=ScriptResponse)
async def generate_script(request: ScriptGenerationRequest):
    """Generate a video script based on user parameters"""
    try:
        # Validate input
        if not request.topic.strip():
            raise HTTPException(status_code=400, detail="Topic is required")
        
        if request.platform not in ["youtube", "tiktok", "instagram", "linkedin"]:
            raise HTTPException(status_code=400, detail="Invalid platform")
        
        if request.duration not in [30, 60, 90, 180]:
            raise HTTPException(status_code=400, detail="Duration must be 30, 60, 90, or 180 seconds")
        
        # Simulate processing time
        time.sleep(2)  # Simulate AI processing
        
        # Generate the script
        script = generate_video_script(
            topic=request.topic,
            platform=request.platform,
            duration=request.duration,
            audience=request.audience,
            tone=request.tone,
            style=request.style
        )
        
        # Create metadata
        metadata = {
            "generated_at": time.time(),
            "user_email": request.user_email,
            "parameters": {
                "topic": request.topic,
                "platform": request.platform,
                "duration": request.duration,
                "audience": request.audience,
                "tone": request.tone,
                "style": request.style
            },
            "word_count": len(script.split()),
            "estimated_reading_time": f"{len(script.split()) // 150} minutes"
        }
        
        return ScriptResponse(
            script=script,
            metadata=metadata
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate script: {str(e)}")

@app.get("/api/v1/test")
async def test_endpoint():
    """Test endpoint to verify API is working"""
    return {
        "status": "success",
        "message": "API is working correctly",
        "timestamp": "2025-06-24",
        "endpoints": [
            "/",
            "/health", 
            "/api/v1/auth/signup",
            "/api/v1/auth/login",
            "/api/v1/scripts",
            "/api/v1/test"
        ]
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)

