from flask import Flask, render_template, request, redirect, url_for, flash

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

user_profile = {}

workout_data = {"count": 3}

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
        challenge_name = request.form.get('challenge')
        update_challenge = request.form.get('update_challenge')

        for challenge in challenges:
            if challenge['name'] == challenge_name:
                challenge['joined'] = True
            if update_challenge and challenge['name'] == update_challenge:
                if challenge['progress'] < 100:
                    challenge['progress'] += 10

    return render_template('challenges.html', challenges=challenges, leaderboard=leaderboard)

@app.route('/progress')
def progress():
    return render_template('progress.html', workouts_completed=workout_data["count"])

@app.route('/community')
def community():
    return render_template('community.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/bonus')
def bonus():
    return render_template('bonus.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
