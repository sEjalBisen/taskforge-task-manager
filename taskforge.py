import json
import os
from datetime import datetime, timedelta

class Task:
    """Represents a single task with data and serialization methods."""
    def __init__(self, task_id, title, priority, due_date, status="Pending"):
        self.id = task_id
        self.title = title
        self.priority = priority
        self.due_date = due_date
        self.status = status

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(data):
        return Task(**data)

    def __str__(self):
        return f"[{self.id}] {self.title} | {self.priority} | {self.due_date} | {self.status}"

class TaskManager:
    """Handles all task operations and file persistence."""
    def __init__(self, file="tasks.json"):
        self.task_list = []
        self.file = file
        self.load_from_file()

    def _generate_id(self):
        """Unique task ID generation - max existing ID + 1"""
        return max([t.id for t in self.task_list], default=0) + 1

    def _get_task_by_id(self, task_id):
        return next((t for t in self.task_list if t.id == task_id), None)

    def _validate_date(self, date_str):
        """Input validation for date format YYYY-MM-DD"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def _validate_priority(self, priority):
        return priority.capitalize() in ["Low", "Medium", "High"]

    def add_task(self):
        title = input("Enter task title: ").strip()
        if not title:
            print("Title cannot be empty.")
            return

        priority = input("Enter priority (Low/Medium/High): ").strip().capitalize()
        if not self._validate_priority(priority):
            print("Invalid priority. Use Low, Medium, or High.")
            return

        due_date = input("Enter due date (YYYY-MM-DD): ").strip()
        if not self._validate_date(due_date):
            print("Invalid date format. Use YYYY-MM-DD.")
            return

        task_id = self._generate_id()
        task = Task(task_id, title, priority, due_date)
        self.task_list.append(task)
        self.save_to_file()
        print("Task added successfully.")

    def view_tasks(self):
        print("\n1. View All\n2. Filter by Status\n3. Filter by Due Date")
        choice = input("Choose option: ").strip()
        
        tasks = self.task_list
        if choice == "2":
            status = input("Enter status (Pending/Completed): ").strip().capitalize()
            tasks = [t for t in self.task_list if t.status == status]
        elif choice == "3":
            filter_type = input("Filter by 'today', 'this week', or specific date YYYY-MM-DD: ").strip()
            today = datetime.now().date()
            if filter_type == "today":
                tasks = [t for t in self.task_list if t.due_date == str(today)]
            elif filter_type == "this week":
                week_end = today + timedelta(days=7)
                tasks = [t for t in self.task_list 
                         if today <= datetime.strptime(t.due_date, "%Y-%m-%d").date() <= week_end]
            else:
                tasks = [t for t in self.task_list if t.due_date == filter_type]
        
        self._print_table(tasks)

    def _print_table(self, tasks):
        if not tasks:
            print("No tasks found.")
            return
        print("\nID  | Title           | Priority | Due Date   | Status")
        print("-" * 55)
        for t in tasks:
            print(f"{t.id:<3} | {t.title:<15} | {t.priority:<8} | {t.due_date:<10} | {t.status}")

    def update_task(self):
        try:
            task_id = int(input("Enter task ID to update: "))
        except ValueError:
            print("Invalid ID. Enter a number.")
            return
        
        task = self._get_task_by_id(task_id)
        if not task:
            print("Task not found.")
            return
        
        print("Press Enter to keep current value.")
        title = input(f"Title [{task.title}]: ").strip()
        priority = input(f"Priority [{task.priority}]: ").strip().capitalize()
        due_date = input(f"Due date [{task.due_date}]: ").strip()
        
        if title: task.title = title
        if priority and self._validate_priority(priority): task.priority = priority
        elif priority: print("Invalid priority, keeping old value.")
        if due_date and self._validate_date(due_date): task.due_date = due_date
        elif due_date: print("Invalid date, keeping old value.")
        
        self.save_to_file()
        print("Task updated.")

    def mark_complete(self):
        try:
            task_id = int(input("Enter task ID to mark complete: "))
        except ValueError:
            print("Invalid ID.")
            return
        
        task = self._get_task_by_id(task_id)
        if task:
            task.status = "Completed"
            self.save_to_file()
            print("Task marked as completed.")
        else:
            print("Task not found.")

    def delete_task(self):
        try:
            task_id = int(input("Enter task ID to delete: "))
        except ValueError:
            print("Invalid ID.")
            return
        
        original_len = len(self.task_list)
        self.task_list = [t for t in self.task_list if t.id != task_id]
        
        if len(self.task_list) < original_len:
            self.save_to_file()
            print("Task deleted.")
        else:
            print("Task not found.")

    def save_to_file(self):
        try:
            with open(self.file, "w") as f:
                json.dump([t.to_dict() for t in self.task_list], f, indent=4)
        except IOError:
            print("Error saving to file.")

    def load_from_file(self):
        if os.path.exists(self.file):
            try:
                with open(self.file, "r") as f:
                    data = json.load(f)
                    self.task_list = [Task.from_dict(t) for t in data]
            except (IOError, json.JSONDecodeError):
                self.task_list = []

def main():
    manager = TaskManager()
    while True:
        print("\n1. Add Task\n2. View Tasks\n3. Update Task\n4. Mark Complete\n5. Delete Task\n6. Exit")
        choice = input("Choose an option: ").strip()
        
        if choice == "1": manager.add_task()
        elif choice == "2": manager.view_tasks()
        elif choice == "3": manager.update_task()
        elif choice == "4": manager.mark_complete()
        elif choice == "5": manager.delete_task()
        elif choice == "6": 
            print("Goodbye!")
            break
        else: 
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()