import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime, date, timedelta
import pytz


class ClassSchedule:
    def __init__(self, name, days, start_time, end_time):
        self.name = name
        self.days = days
        self.start_time = start_time
        self.end_time = end_time


class Task:
    def __init__(self, name, deadline, tag, estimated_time, sections=1):
        self.name = name
        self.deadline = deadline
        self.tag = tag
        self.estimated_time = estimated_time
        self.sections = sections 
        self.priority = self.get_task_priority(deadline, estimated_time)
        self.finished = False
        self.actual_time = None
    
    def mark_finished(self, actual_time):
        self.finished = True
        self.actual_time = actual_time
    
    def get_task_priority(self, deadline, estimated_time):
        chicago_now = datetime.now(pytz.timezone('America/Chicago'))
        if isinstance(deadline, datetime):
            deadline = deadline.astimezone(pytz.timezone('America/Chicago'))
        days_before_DDL = (deadline.date() - chicago_now.date()).days
        if days_before_DDL <= 0:
            days_before_DDL = 0.000000001 # Avoid divide by zero
        priority = (1 / days_before_DDL) * 0.5 + estimated_time * 0.5 # priority based on 
        return priority


class RecommendationSystem:
    def __init__(self):
        self.tags = [] 

    def recommend_tasks(self, tasks, user_preferences):
        if not tasks:
            return []

        # Make Tags
        task_tags = [task.tag for task in tasks]
        self.tags = list(set(task_tags))
        
        task_features = []
        for task in tasks:
            task_vec = self.create_feature_vec(task)
            task_features.append(task_vec)
        
        # Create the user preference vec
        user_preference_vec = self.user_prefer_vec(user_preferences)

        # Similiarities between those (using package from Sklearn)
        prefer_similarity = cosine_similarity(task_features, [user_preference_vec])

        # Task Final Score
        task_scores = []
        for i, task in enumerate(tasks):
            days_before_DDL = (task.deadline.date() - datetime.now().date()).days
            if days_before_DDL == 0:
                days_before_DDL = 0.000000001  # Prevent division by zero
            score = (
                prefer_similarity[i][0] * 0.4 + # How close to user preference
                (1 / days_before_DDL) * 0.3 + # How urgent
                task.priority * 0.3 #How urgent+ How long
            )
            task_scores.append((task, score))

        return sorted(task_scores, key=lambda x: x[1], reverse=True) # highest to lowest
    
    def update_preferences(self, state, energy_level): 
        num_tasks, current_energy = state.split('_')
        self.user_preferences['estimated_time'] = self.energy_to_time(energy_level)
    
    def energy_to_time(self, energy_level):
        if energy_level == "low":
            return 30
        elif energy_level == "medium":
            return 60
        else:
            return 120
        
    def create_feature_vec(self, task):
        tag_vec = []
        for tag in self.tags:
            if tag == task.tag:
                tag_vec.append(1)
            else:
                tag_vec.append(0)
        priority_vec = [task.priority]
        estimated_time_vec = [task.estimated_time]

        # create vector for KNN 
        feature_vec = tag_vec + priority_vec + estimated_time_vec
        return feature_vec

    def user_prefer_vec(self, user_preferences):
        # Checking which Tag
        tag_prefer_vec = [1 if tag == user_preferences.get('tag', '') else 0 for tag in self.tags]
        
        # Check priority
        priority_prefer_vec = [user_preferences.get('priority', 1)]
        
        # Time for Completion
        estimated_time_prefer_vec = [user_preferences.get('estimated_time', 60)]

        # create vector for KNN 
        prefer_vec = tag_prefer_vec + priority_prefer_vec + estimated_time_prefer_vec
        return prefer_vec


## Code Provided by Claude AI
class ReinforcementLearningAgent:
    def __init__(self, n_actions, learning_rate=0.1, discount_factor=0.95, epsilon=0.1):
        self.n_actions = n_actions
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.q_table = {}

    def get_action(self, state):
        if np.random.random() < self.epsilon:
            return np.random.randint(self.n_actions)
        else:
            if state not in self.q_table:
                self.q_table[state] = np.zeros(self.n_actions)
            return np.argmax(self.q_table[state])

    def update(self, state, action, reward, next_state):
        if state not in self.q_table:
            self.q_table[state] = np.zeros(self.n_actions)
        if next_state not in self.q_table:
            self.q_table[next_state] = np.zeros(self.n_actions)
        
        current_q = self.q_table[state][action]
        max_next_q = np.max(self.q_table[next_state])
        new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_next_q - current_q)
        self.q_table[state][action] = new_q


## Smart Scheduler Core
class SmartScheduler:
    def __init__(self):
        # Time Zone to Ensure no Time offset
        self.timezone = pytz.timezone('America/Chicago')
        # For Webpage Visuzalization
        self.day_map = {
            0: 'Monday',
            1: 'Tuesday',
            2: 'Wednesday',
            3: 'Thursday',
            4: 'Friday',
            5: 'Saturday',
            6: 'Sunday',
        }
        self.classes = []
        self.tasks = []
        self.working_hours = {}
        self.tags = set(['reading', 'writing', 'project']) # initial tags
        self.recommendation_system = RecommendationSystem()
        self.rl_agent = ReinforcementLearningAgent(n_actions=3)
        self.energy_levels = ["low", "medium", "high"]
        self.task_history = []
        self.improvement_date = datetime.now(self.timezone).date()


    def get_current_time(self):
        return datetime.now(self.timezone)
        
    def set_working_hours(self, day, start_time, end_time):
        self.working_hours[day.capitalize()] = (start_time, end_time)
        
    def add_class(self, class_schedule):
        class_schedule.days = [day.capitalize() for day in class_schedule.days]
        self.classes.append(class_schedule)

    def add_task(self, task):
        self.tasks.append(task)
        self.tags.add(task.tag)

    def get_daily_schedule(self, date):
        day_name = self.day_map[date.weekday()]
        schedule = []

        # Add classes
        for class_schedule in self.classes:
            if day_name in class_schedule.days:
                # For Duration Calculation
                class_start_datetime = datetime.combine(date, class_schedule.start_time)
                class_end_datetime = datetime.combine(date, class_schedule.end_time)
                duration = (class_end_datetime - class_start_datetime).seconds // 60

                schedule.append({
                    'type': 'class',
                    'name': class_schedule.name,
                    'start_time': class_schedule.start_time.strftime('%H:%M'),
                    'end_time': class_schedule.end_time.strftime('%H:%M'),
                    'duration': duration
                })

        # Add working hours block
        if day_name in self.working_hours:
            start_time, end_time = self.working_hours[day_name]
            # For Duration Calculation
            work_start_datetime = datetime.combine(date, start_time)
            work_end_datetime = datetime.combine(date, end_time)
            work_duration = (work_end_datetime - work_start_datetime).seconds // 60

            schedule.append({
                'type': 'working_hours',
                'start_time': start_time.strftime('%H:%M'),
                'end_time': end_time.strftime('%H:%M'),
                'duration': work_duration,
                'tasks': []
            })

        return schedule

    def update_daily_schedule(self, date, user_preferences):
        # Get Workblock and Class
        schedule = self.get_daily_schedule(date)
        
        if not self.tasks and not self.task_history:
            return schedule

        # Get all tasks, including finished ones for today
        all_tasks = self.tasks.copy()
        
        # Add finished tasks 
        todays_finished_tasks = []
        for task in self.task_history:
            if task['completed_date'] == date:
                finished_task = Task(
                    name=task['name'],
                    deadline=task['deadline'],
                    tag=task['tag'],
                    estimated_time=task['estimated_time']
                )
                todays_finished_tasks.append(finished_task)
        
        # Mark tasks as finished and set their times
        for finished_task in todays_finished_tasks:
            finished_task.finished = True
            
            history = None
            
            for task in self.task_history:
                if task['name'] == finished_task.name and task['completed_date'] == date:
                    history = task
                    break  
                
            # Get Actual Time
            if history:
                finished_task.actual_time = history['actual_time']
        
        # Combine current tasks with finished tasks
        all_tasks.extend(todays_finished_tasks)

        recommended_tasks = self.recommendation_system.recommend_tasks(all_tasks, user_preferences)
        
        # Adding Tasks
        for block in schedule:
            # Ensur it is working hour
            if block['type'] == 'working_hours':
                start_time = block['start_time']
                end_time = block['end_time']

                # Weird Formate with Time
                if isinstance(start_time, str):
                    start_time = datetime.strptime(start_time, '%H:%M').time()
                if isinstance(end_time, str):
                    end_time = datetime.strptime(end_time, '%H:%M').time()
                work_start_datetime = datetime.combine(date, start_time)
                work_end_datetime = datetime.combine(date, end_time)
                available_time = (work_end_datetime - work_start_datetime).seconds // 60


                block['tasks'] = []

                # Adjust for class times
                for class_block in schedule:
                    if class_block['type'] == 'class':
                        class_start_time = datetime.strptime(class_block['start_time'], '%H:%M').time()
                        class_end_time = datetime.strptime(class_block['end_time'], '%H:%M').time()
                        
                        class_start_datetime = datetime.combine(date, class_start_time)
                        class_end_datetime = datetime.combine(date, class_end_time)
                        
                        # Avoid to do task while having a class
                        if class_start_datetime < work_end_datetime and class_end_datetime > work_start_datetime:
                            work_start_datetime = class_end_datetime

                available_time = (work_end_datetime - work_start_datetime).seconds // 60

                # Add all tasks 
                for task, score in recommended_tasks:
                    task_duration = task.actual_time if task.finished else task.estimated_time
                    
                    if task_duration <= available_time:
                        block['tasks'].append({
                            'name': task.name,
                            'deadline': task.deadline.strftime('%Y-%m-%d'),
                            'estimated_time': task.estimated_time,
                            'actual_time': task.actual_time if task.finished else None,
                            'score': round(score, 2),
                            'finished': task.finished
                        })
                        available_time -= task_duration
        
        return schedule


    def get_next_task(self, user_preferences, current_energy):
        unfinished_tasks = [task for task in self.tasks if not task.finished]
        if not unfinished_tasks:
            return None

        # Use Chicago time for deadline comparison
        chicago_now = self.get_current_time()
        sorted_tasks = sorted(unfinished_tasks, 
                            key=lambda t: (t.deadline.astimezone(self.timezone) if isinstance(t.deadline, datetime) else t.deadline, 
                                         -t.priority))

        # Filter tasks based on energy level
        energy_levels = ["low", "medium", "high"]
        current_energy_index = energy_levels.index(current_energy)
        
        print("All unfinished tasks:", sorted_tasks)
        
        eligible_tasks = [
            task for task in sorted_tasks 
            if energy_levels.index(self.get_task_energy_level(task)) == current_energy_index
        ]
        
        print(f"Eligible tasks for {current_energy} energy:", eligible_tasks)

        if not eligible_tasks:
            # If no tasks match the current energy level, look for tasks with lower energy requirements
            for energy_level in energy_levels[:current_energy_index]:
                eligible_tasks = [
                    task for task in sorted_tasks 
                    if self.get_task_energy_level(task) == energy_level
                ]
                if eligible_tasks:
                    print(f"No tasks for {current_energy} energy. Suggesting tasks for {energy_level} energy:", eligible_tasks)
                    break

        if not eligible_tasks:
            print("No eligible tasks found for the current or lower energy levels.")
            return None

        # Use the recommendation system to get the best task
        recommended_tasks = self.recommendation_system.recommend_tasks(eligible_tasks, user_preferences)
        
        if recommended_tasks:
            recommended_task = recommended_tasks[0][0]
            print(f"Recommended task: {recommended_task.name}")
            return recommended_task
        else:
            print(f"Returning first eligible task: {eligible_tasks[0].name}")
            return eligible_tasks[0]  # Return the first eligible task if recommendation fails

    def get_task_energy_level(self, task):
        if task.estimated_time <= 30:
            return "low"
        elif task.estimated_time <= 90:
            return "medium"
        else:
            return "high"
    
    def update_recommendation_system(self):
        current_date = self.get_current_time().date()
        if (current_date - self.improvement_date).days >= 7:
            print("Improving recommendation system based on the past week's data...")
            for state, actions in self.rl_agent.q_table.items():
                best_action = np.argmax(actions)
                self.recommendation_system.update_preferences(state, self.energy_levels[best_action])
            self.improvement_date = current_date

    def get_daily_summary(self, date):
        
        total_study_time = 0
        completed_tasks = []
        overdue_tasks = 0

        chicago_now = self.get_current_time()
        
        for task in self.task_history:
            completed_date = task['completed_date']
            
            # Convert string date to datetime.date if necessary
            if isinstance(completed_date, str):
                completed_date = datetime.strptime(completed_date, '%Y-%m-%d').date()
            elif isinstance(completed_date, datetime):
                completed_date = completed_date.astimezone(self.timezone).date()
                
            if completed_date == date:
                actual_time = task.get('actual_time', 0)
                if actual_time is not None:
                    total_study_time += actual_time
                    
                completed_tasks.append({
                    'name': task['name'],
                    'time_spent': actual_time,
                    'estimated_time': task['estimated_time'],
                    'completion_time': task.get('completion_time', '00:00')
                })

        return {
            'date': date.strftime('%Y-%m-%d'),
            'total_study_time': total_study_time,
            'completed_tasks': len(completed_tasks),
            'average_task_time': round(total_study_time / len(completed_tasks)) if completed_tasks else 0,
            'overdue_tasks': overdue_tasks,
            'tasks': completed_tasks
        }

    def mark_task_finished(self, task_name, actual_time):
        for task in self.tasks:
            if task.name == task_name:
                task.mark_finished(actual_time)
                completion_time = self.get_current_time()
                
                # Add to task history with all necessary details
                history_entry = {
                    'name': task.name,
                    'deadline': task.deadline,
                    'estimated_time': task.estimated_time,
                    'actual_time': actual_time,
                    'completed_date': completion_time.date(),
                    'completion_time': completion_time.strftime('%H:%M'),
                    'tag': task.tag
                }
                self.task_history.append(history_entry)
                
                # Update RL agent
                state = f"{len(self.tasks)}_{self.get_task_energy_level(task)}"
                action = self.energy_levels.index(self.get_task_energy_level(task))
                reward = 1 if actual_time <= task.estimated_time else -1
                next_state = f"{len(self.tasks) - 1}_{self.get_current_energy()}"
                self.rl_agent.update(state, action, reward, next_state)
                
                self.tasks.remove(task)
                break

            
            
    
    def get_weekly_summary(self, start_date=None):
        if start_date is None:
            chicago_now = self.get_current_time()
            start_date = chicago_now.date() - timedelta(days=chicago_now.weekday())

        end_date = start_date + timedelta(days=6)


        # Initialize counters and lists
        total_study_time = 0
        completed_tasks = []
        
        # Get all tasks completed within the week
        weekly_tasks = [
            task for task in self.task_history
            if start_date <= task['completed_date'] <= end_date
        ]
        
        # Process tasks
        for task in weekly_tasks:
            total_study_time += task['actual_time']
            completed_tasks.append({
                'name': task['name'],
                'completed_date': task['completed_date'],
                'actual_time': task['actual_time'],
                'estimated_time': task['estimated_time']
            })
        
        # Calculate daily breakdown
        daily_breakdown = []
        current_date = start_date

        while current_date <= end_date:
            day_tasks = [
                task for task in weekly_tasks
                if task['completed_date'] == current_date
            ]
            
            # Gather classes for this day
            day_name = current_date.strftime('%A')
            day_classes = [
                {
                    'name': cls.name,
                    'duration': int((datetime.combine(current_date, cls.end_time) - 
                                    datetime.combine(current_date, cls.start_time)).total_seconds() / 60)
                }
                for cls in self.classes
                if day_name in cls.days
            ]

            # Compute daily stats
            daily_stats = {
                'date': current_date.strftime('%Y-%m-%d'),
                'completed_tasks': len(day_tasks),
                'study_time': sum(task['actual_time'] for task in day_tasks),
                'class_time': sum(cls['duration'] for cls in day_classes)
            }
            
            daily_breakdown.append(daily_stats)
            current_date += timedelta(days=1)
        
        # Sort tasks by completion date
        completed_tasks.sort(key=lambda x: x['completed_date'])
        
        # Prepare response
        response = {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'total_study_time': total_study_time,
            'completed_tasks': len(completed_tasks),
            'daily_breakdown': daily_breakdown,
            'task_details': [{
                'name': task['name'],
                'completed_date': task['completed_date'].strftime('%Y-%m-%d'),
                'actual_time': task['actual_time'],
                'estimated_time': task.get('estimated_time', 0)
            } for task in completed_tasks]
        }
        
        return response


    
    def get_current_energy(self):
        return "medium"

    def get_tasks_for_date(self, date):
        return [task for task in self.tasks if task.deadline == date and not task.finished]

    def get_classes_for_day(self, day_name):
        return [class_schedule for class_schedule in self.classes if day_name in class_schedule.days]