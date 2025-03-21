from flask import Flask, render_template, request

app = Flask(__name__)

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

@app.route('/')
def home():
    return render_template('index.html')

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

if __name__ == '__main__':
    app.run(debug=True, port=5001)
