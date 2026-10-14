"""
Workout Generation Service for VisionFit AI
Handles workout parameter collection, Gemini multimodal invocation,
response parsing, and realistic demo simulation fallback.
"""

from typing import Dict, Any, Tuple
from PIL import Image
from services.gemini_service import GeminiService
from utils.prompts import build_workout_prompt
from utils.formatting import extract_json_from_response


DEMO_WORKOUTS = {
    "Strength": {
        "title": "Iron & Core Strength Sculptor",
        "description": "A high-efficiency dumbbell and kettlebell workout designed to build lean functional muscle, fortify posture, and elevate metabolic rate.",
        "goal": "Strength",
        "experience_level": "Intermediate",
        "estimated_duration_minutes": 30,
        "workout_focus": "Full Body",
        "location": "Home Gym",
        "target_muscle_groups": ["Quadriceps", "Chest", "Upper Back / Lats", "Shoulders", "Core"],
        "visually_identified_equipment": [
            "Adjustable Hex Dumbbells (10kg)",
            "Cast Iron Kettlebell (16kg)",
            "Exercise Mat"
        ],
        "uncertain_equipment": [
            "Resistance bands in background (ensure elastic integrity before heavy pulling)"
        ],
        "warmup": [
            {
                "name": "Arm Circles & Torso Twists",
                "duration": "60 seconds",
                "instructions": "Stand with feet shoulder-width apart. Rotate arms in wide smooth circles, then gently twist torso side to side."
            },
            {
                "name": "Bodyweight Hip Openers (World's Greatest Stretch)",
                "duration": "60 seconds (30s each side)",
                "instructions": "Step into a deep lunge, place hands on mat, and reach your inside arm toward the ceiling to open your thoracic spine."
            },
            {
                "name": "Glute Bridges & Bird-Dogs",
                "duration": "90 seconds",
                "instructions": "Lie on mat to activate glutes, then shift to all fours to activate spinal stabilizers."
            }
        ],
        "main_exercises": [
            {
                "name": "Kettlebell Goblet Squats",
                "sets": "3",
                "reps_or_duration": "10-12 reps",
                "rest_seconds": "60s",
                "target_muscles": "Quadriceps, Glutes, Core",
                "technique_cues": "Hold the kettlebell horns close to your chest. Keep elbows tucked. Drive through whole feet to stand tall.",
                "common_mistake": "Rounding lower back or letting knees collapse inward.",
                "easier_alternative": "Bodyweight squats to a bench or chair."
            },
            {
                "name": "Dual Dumbbell Romanian Deadlifts",
                "sets": "3",
                "reps_or_duration": "10 reps",
                "rest_seconds": "60s",
                "target_muscles": "Hamstrings, Gluteus Maximus, Lower Back",
                "technique_cues": "Hinge at hips, push glutes backward while keeping spine neutral and dumbbells close to your shins.",
                "common_mistake": "Bending knees too early turning it into a squat rather than a hip hinge.",
                "easier_alternative": "Single kettlebell deadlift from an elevated block."
            },
            {
                "name": "Dumbbell Floor Press",
                "sets": "3",
                "reps_or_duration": "10-12 reps",
                "rest_seconds": "60s",
                "target_muscles": "Pectorals, Anterior Deltoids, Triceps",
                "technique_cues": "Lie flat on mat with knees bent. Press dumbbells up until arms are fully extended, then lower until triceps gently touch the floor.",
                "common_mistake": "Flaring elbows out at 90 degrees (keep at a 45-60 degree angle to safeguard shoulders).",
                "easier_alternative": "Kneeling push-ups or hands-elevated push-ups."
            },
            {
                "name": "Single-Arm Kettlebell / Dumbbell Row",
                "sets": "3",
                "reps_or_duration": "10 reps per side",
                "rest_seconds": "45s",
                "target_muscles": "Latissimus Dorsi, Rhomboids, Biceps",
                "technique_cues": "Brace one hand on your thigh or sturdy surface. Pull elbow back toward your hip pocket, squeezing shoulder blade.",
                "common_mistake": "Jerking the weight using momentum from the hips.",
                "easier_alternative": "Two-handed kettlebell row or light resistance band row."
            },
            {
                "name": "Deadbugs or Hollow Body Hold",
                "sets": "3",
                "reps_or_duration": "45 seconds",
                "rest_seconds": "45s",
                "target_muscles": "Transverse Abdominis, Deep Core",
                "technique_cues": "Press lower back firmly into the exercise mat. Extend opposite arm and leg slowly while maintaining core brace.",
                "common_mistake": "Arching lower back off the mat.",
                "easier_alternative": "Standard bent-knee tabletop toe taps."
            }
        ],
        "cooldown": [
            {
                "name": "Child's Pose with Lat Reach",
                "duration": "45 seconds",
                "instructions": "Kneel on mat, sink hips back onto heels, reach hands forward and gently walk hands to the right, then left."
            },
            {
                "name": "Kneeling Hip Flexor & Quad Stretch",
                "duration": "30s per side",
                "instructions": "Tuck pelvis under to stretch front of thigh and hip."
            }
        ],
        "safety_reminders": [
            "Ensure the floor mat is dry and non-slip before starting.",
            "Inspect dumbbells and kettlebell handle grip before lifting.",
            "Stop immediately if you experience acute joint discomfort, sharp spinal pain, or dizziness."
        ]
    },
    "General Fitness": {
        "title": "Full-Body Metabolic Conditioning & Flow",
        "description": "A high-energy, functional routine combining resistance intervals with active mobility to boost cardiovascular endurance and functional strength.",
        "goal": "General Fitness",
        "experience_level": "Beginner / Intermediate",
        "estimated_duration_minutes": 25,
        "workout_focus": "Full Body",
        "location": "Home",
        "target_muscle_groups": ["Total Body Conditioning"],
        "visually_identified_equipment": [
            "Dumbbells",
            "Exercise Mat"
        ],
        "uncertain_equipment": [
            "Assess dumbbell weight suitability for beginners"
        ],
        "warmup": [
            {
                "name": "Jumping Jacks / Step Jacks",
                "duration": "60 seconds",
                "instructions": "Light rhythmic movement to elevate heart rate and body temperature."
            },
            {
                "name": "Inchworms with Shoulder Taps",
                "duration": "60 seconds",
                "instructions": "From standing, fold forward, walk hands out to plank, tap each shoulder, and walk back."
            }
        ],
        "main_exercises": [
            {
                "name": "Dumbbell Thrusters (Squat to Overhead Press)",
                "sets": "3",
                "reps_or_duration": "10 reps",
                "rest_seconds": "60s",
                "target_muscles": "Legs, Shoulders, Core, Heart Rate",
                "technique_cues": "Hold dumbbells at shoulder height. Squat down smoothly, then use leg drive to press dumbbells overhead.",
                "common_mistake": "Pausing between squat and press rather than utilizing fluid upward momentum.",
                "easier_alternative": "Squat to chest press, or bodyweight air squat followed by overhead reach."
            },
            {
                "name": "Dumbbell Suitcase Reverse Lunges",
                "sets": "3",
                "reps_or_duration": "8 reps per leg",
                "rest_seconds": "45s",
                "target_muscles": "Glutes, Hamstrings, Quadriceps, Balance",
                "technique_cues": "Hold weights by your sides. Step backward into a 90-degree lunge, driving through front heel to return.",
                "common_mistake": "Front knee sliding forward beyond toes.",
                "easier_alternative": "Stationary split squats without dumbbells."
            },
            {
                "name": "Dumbbell Renegade Rows on Knees",
                "sets": "3",
                "reps_or_duration": "10 total reps",
                "rest_seconds": "45s",
                "target_muscles": "Upper Back, Lats, Anti-rotational Core",
                "technique_cues": "Set up in plank on knees with hands on dumbbells. Row one weight to ribcage without twisting hips.",
                "common_mistake": "Excessive hip sway from side to side.",
                "easier_alternative": "Bird-Dog hold on mat."
            },
            {
                "name": "Forearm Plank to Pike",
                "sets": "3",
                "reps_or_duration": "40 seconds",
                "rest_seconds": "30s",
                "target_muscles": "Rectus Abdominis, Shoulders",
                "technique_cues": "Hold solid forearm plank, then lift hips toward ceiling and slowly return to level.",
                "common_mistake": "Sagging hips below neutral line.",
                "easier_alternative": "Static knee plank on mat."
            }
        ],
        "cooldown": [
            {
                "name": "Cat-Cow & Cobra Stretch",
                "duration": "60 seconds",
                "instructions": "Gentle flexion and extension of spine to relax nervous system."
            }
        ],
        "safety_reminders": [
            "Maintain controlled breathing throughout every repetition.",
            "Keep water bottle nearby for hydration intervals."
        ]
    }
}


def generate_workout(
    image: Image.Image,
    params: Dict[str, Any],
    gemini_service: GeminiService
) -> Tuple[bool, Dict[str, Any], str]:
    """
    Main workout generation coordinator.
    Returns: (success: bool, workout_data: Dict[str, Any], notice_or_error: str)
    """
    if gemini_service.is_configured:
        prompt = build_workout_prompt(params)
        success, raw_text, meta = gemini_service.generate_multimodal_content(image, prompt)
        
        if not success:
            return False, {}, meta.get("message", "Failed to generate workout from AI.")

        parsed_workout = extract_json_from_response(raw_text)
        if not parsed_workout or not isinstance(parsed_workout, dict) or "title" not in parsed_workout:
            return False, {}, "The AI generated text but the structured workout could not be parsed. Please try again."

        parsed_workout["is_demo"] = False
        parsed_workout["model_used"] = meta.get("model_used", "Gemini Vision")
        return True, parsed_workout, "Workout routine generated successfully using Gemini Multimodal Vision!"

    else:
        # Offline Demo Mode Simulation
        goal = params.get("goal", "Strength")
        if "Fitness" in goal or "Endurance" in goal:
            demo_data = DEMO_WORKOUTS["General Fitness"].copy()
        else:
            demo_data = DEMO_WORKOUTS["Strength"].copy()

        demo_data["estimated_duration_minutes"] = params.get("available_time", 30)
        demo_data["experience_level"] = params.get("experience_level", "Intermediate")
        demo_data["is_demo"] = True
        demo_data["provider"] = "Demo Mode (Mock Simulation - No API Key Set)"

        notice = (
            "DEMO MODE: Running with simulated visual equipment analysis because no GEMINI_API_KEY was provided. "
            "To unlock live multimodal vision, paste your API key in the sidebar!"
        )
        return True, demo_data, notice

