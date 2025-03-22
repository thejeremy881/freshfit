from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime #Import datetime module

app = Flask(__name__)

app.secret_key = "hackMISSO"

#Global Data Storage
meal_logs = []
meal_totals = {"Breakfast": 0, "Lunch": 0, "Dinner": 0, "Snacks": 0}
challenges = [
    {"name": "10,000 Steps a Day", "joined": False, "progress": 0},
    {"name": "No Sugar for 7 Days", "joined": False, "progress": 0},
    {"name": "7-Day Beginner Workout", "joined": False, "progress": 0}
]
leaderboard = [
    {"name": "Alex", "points": 120},
    {"name": "Jordan", "points": 100},
    {"name": "Taylor", "points": 90}
]

# Activity Feed
activity_feed = []
last_reset_date = None

user_profile = {}

workout_data = {"count": 3}

# Default settings (this could be stored in a database or file in a more complex app)
DEFAULT_SETTINGS = {
    'workout_reminders': False,
    'dark_mode': True,
    'progress_emails': False
}

#Here, I will code a Workout Plan Generator
def generate_workout_plan(profile):
    if not profile:
        return "Full-body strength | 30 mins"
    
    goal = profile.get("goal")
    level = profile.get("fitness_level")
    equipment = profile.get("equipment")

    # Simple rule-based logic
    if goal == "Lose Weight":
        if equipment == "None":
            return "HIIT + Bodyweight Circuit | 25 mins"
        else:
            return "Cardio & Weights Split | 30 mins"
    elif goal == "Build Muscle":
        if level == "Beginner":
            return "Upper/Lower Split | Dumbbells | 35 mins"
        else:
            return "Push/Pull/Legs | Gym Machines | 45 mins"
    elif goal == "Get Toned":
        return "Full-body Sculpt + Core | 30 mins"

    return "General Fitness | 30 mins"

#The Home Routes
@app.route('/')
def home():
    workout_plan = generate_workout_plan(user_profile)
    return render_template(
        'index.html', 
        profile=user_profile, 
        workout_plan=workout_plan,
        workouts_completed=workout_data["count"]
    )

@app.route('/start-workout')
def start_workout():
    if workout_data["count"] < 5:
        workout_data["count"] += 1
        flash("Workout has been completed!")
    else:
        flash("You've already completed 5 workouts this week!")
    return redirect(url_for('home'))

@app.route('/reset-workouts', methods=['POST'])
def reset_workouts():
    workout_data["count"] = 0
    flash("Weekly workout count has been reset.")
    return redirect(url_for('progress'))

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    global user_profile

    if request.method == 'POST':
        fitness_level = request.form.get('fitness_level')
        goal = request.form.get('goal')
        equipment = request.form.get('equipment')

        user_profile = {
            "fitness_level": fitness_level,
            "goal": goal,
            "equipment": equipment,
        }

        #Call the function correctly
        workout_plan = generate_workout_plan(user_profile)

        return render_template('index.html', profile=user_profile, workout_plan=workout_plan)

    return render_template('setup.html')

@app.route('/nutrition', methods=['GET', 'POST'])
def nutrition():
    global meal_logs, meal_totals

    if request.method == 'POST':
        if request.form.get("reset"):
            meal_logs = []
            meal_totals = {"Breakfast": 0, "Lunch": 0, "Dinner": 0, "Snacks": 0}
        else:
            category = request.form.get('category')
            meal = request.form.get('meal')
            calories = request.form.get('calories')

            if meal and calories and category:
                try:
                    calorie_value = int(calories)
                    meal_logs.append({"category": category, "meal": meal, "calories": calorie_value})
                    meal_totals[category] += calorie_value
                except ValueError:
                    pass

    total_calories = sum(meal['calories'] for meal in meal_logs)

    return render_template('nutrition.html', meals=meal_logs, total_calories=total_calories, meal_totals=meal_totals)

@app.route('/challenges', methods=['GET', 'POST'])
def challenges_page():
    if request.method == 'POST':
        challenge_name = request.form.get('challenge')  # Get the challenge name
        # Find the challenge in the list
        for challenge in challenges:
            if challenge['name'] == challenge_name:
                # If the challenge is already joined, unjoin it, otherwise join it
                if challenge['joined']:
                    challenge['joined'] = False  # Unjoin
                else:
                    challenge['joined'] = True  # Join
                break  # Exit the loop once we update the challenge

    return render_template('challenges.html', challenges=challenges, leaderboard=leaderboard)

@app.route('/progress')
def progress():
    return render_template('progress.html', workouts_completed=workout_data["count"])

@app.route('/community', methods=['GET', 'POST'])
def community():
    global activity_feed, last_reset_date

    # Get the current date
    current_date = datetime.now().date()

    # Check if we need to reset the activity feed
    if last_reset_date != current_date:
        # Reset the activity feed if the date has changed
        activity_feed = []
        last_reset_date = current_date
        print(f"Activity feed reset on {current_date}")  # Debugging statement

    # Handle POST request for new posts
    if request.method == 'POST':
        post_message = request.form.get('post')
        if post_message:
            # Generate current timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d %I:%M %p')  # Format the timestamp

            # Generate a new id for the post based on the length of the feed (simple unique id)
            if activity_feed:
                new_id = max(post['id'] for post in activity_feed) + 1
            else:
                new_id = 1  # Start from 1 if no posts exist yet

            # Save the new post to activity feed
            activity_feed.append({
                "id": new_id,  # Assign unique id to each post
                "user": "Current User",  # Replace with actual logged-in user
                "message": post_message,
                "timestamp": timestamp
            })

    # Debugging: Print out the current activity_feed before rendering
    print(f"Activity Feed before rendering: {activity_feed}")

    # Render the updated activity feed in the template
    return render_template('community.html', activity_feed=activity_feed)


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    # Load current settings (from session or defaults)
    settings = session.get('settings', DEFAULT_SETTINGS)

    if request.method == 'POST':
        # Save the user's settings from the form submission
        settings['workout_reminders'] = 'workout_reminders' in request.form
        settings['dark_mode'] = 'dark_mode' in request.form
        settings['progress_emails'] = 'progress_emails' in request.form

        # Save settings to session
        session['settings'] = settings

        # Redirect back to the settings page to see changes
        return redirect(url_for('settings'))

    # Render the settings page with the current settings
    return render_template('settings.html', settings=settings)


@app.route('/bonus')
def bonus():
    return render_template('bonus.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
