import json
import os


class Student:
    """Represents a single student with marks"""

    def __init__(self, roll_no, name, age, course, email="", marks=None):
        self.roll_no = roll_no
        self.name = name
        self.age = age
        self.course = course
        self.email = email
        # marks is a dict like {"Math": 85, "Science": 90}
        self.marks = marks if marks else {}

    def add_mark(self, subject, mark):
        """Add or update a mark"""
        self.marks[subject] = mark

    def calculate_total(self):
        """Sum of all marks"""
        return sum(self.marks.values())

    def calculate_percentage(self):
        """Percentage (each subject out of 100)"""
        if not self.marks:
            return 0
        max_marks = len(self.marks) * 100
        return (self.calculate_total() / max_marks) * 100

    def calculate_grade(self):
        """Grade based on percentage"""
        p = self.calculate_percentage()
        if p >= 90: return 'A+'
        elif p >= 80: return 'A'
        elif p >= 70: return 'B'
        elif p >= 60: return 'C'
        elif p >= 50: return 'D'
        else: return 'F'

    def get_status(self):
        """Pass if all subjects >= 35, else Fail"""
        if not self.marks:
            return "No Marks"
        for mark in self.marks.values():
            if mark < 35:
                return "Fail"
        return "Pass"

    def to_dict(self):
        """Convert to dictionary (for JSON)"""
        return {
            'roll_no': self.roll_no,
            'name': self.name,
            'age': self.age,
            'course': self.course,
            'email': self.email,
            'marks': self.marks
        }

    @classmethod
    def from_dict(cls, data):
        """Create Student from dict"""
        return cls(
            roll_no=data['roll_no'],
            name=data['name'],
            age=data['age'],
            course=data['course'],
            email=data.get('email', ''),
            marks=data.get('marks', {})
        )


class FileStorage:
    """Handles JSON file read/write"""

    def __init__(self, file_path):
        self.file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Create file & folder if missing"""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump([], f)

    def read_all(self):
        """Read all data from JSON"""
        try:
            with open(self.file_path, 'r') as f:
                raw = f.read().strip()
                return json.loads(raw) if raw else []
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error reading file: {e}")
            return []

    def write_all(self, data):
        """Write all data to JSON"""
        try:
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error writing file: {e}")
            return False


class StudentManager:
    """Manages CRUD + reports for students"""

    def __init__(self, storage):
        self.storage = storage
        self.students = self._load_students()

    def _load_students(self):
        """Load all students from storage"""
        data = self.storage.read_all()
        return [Student.from_dict(item) for item in data]

    def _save_students(self):
        """Save all students to storage"""
        data = [s.to_dict() for s in self.students]
        return self.storage.write_all(data)

    # ---- CRUD ----
    def add_student(self, roll_no, name, age, course, email=""):
        if self.search_student(roll_no):
            return False, "Student with this Roll No already exists!"
        student = Student(roll_no, name, age, course, email)
        self.students.append(student)
        self._save_students()
        return True, "Student added successfully!"

    def update_student(self, roll_no, name, age, course, email):
        student = self.search_student(roll_no)
        if not student:
            return False, "Student not found!"
        student.name = name
        student.age = age
        student.course = course
        student.email = email
        self._save_students()
        return True, "Student updated successfully!"

    def delete_student(self, roll_no):
        student = self.search_student(roll_no)
        if not student:
            return False, "Student not found!"
        self.students.remove(student)
        self._save_students()
        return True, "Student deleted successfully!"

    def search_student(self, roll_no):
        for s in self.students:
            if s.roll_no == roll_no:
                return s
        return None

    def get_all_students(self):
        return self.students

    # ---- Marks ----
    def add_marks(self, roll_no, subject, mark):
        student = self.search_student(roll_no)
        if not student:
            return False, "Student not found!"
        try:
            mark = float(mark)
            if mark < 0 or mark > 100:
                return False, "Mark must be between 0 and 100!"
        except ValueError:
            return False, "Invalid mark value!"
        student.add_mark(subject, mark)
        self._save_students()
        return True, f"Marks added for {subject}!"

    # ---- Reports ----
    def get_topper_list(self, n=5):
        with_marks = [s for s in self.students if s.marks]
        if not with_marks:
            return []
        return sorted(with_marks, key=lambda s: s.calculate_percentage(), reverse=True)[:n]

    def get_average_marks(self):
        with_marks = [s for s in self.students if s.marks]
        if not with_marks:
            return 0
        return sum(s.calculate_percentage() for s in with_marks) / len(with_marks)

    def get_subject_statistics(self):
        stats = {}
        for s in self.students:
            for subject, mark in s.marks.items():
                stats.setdefault(subject, []).append(mark)
        result = {}
        for subject, marks in stats.items():
            result[subject] = {
                'count': len(marks),
                'average': sum(marks) / len(marks),
                'highest': max(marks),
                'lowest': min(marks)
            }
        return result

    def get_pass_fail_count(self):
        p = f = nm = 0
        for s in self.students:
            st = s.get_status()
            if st == "Pass": p += 1
            elif st == "Fail": f += 1
            else: nm += 1
        return {'pass': p, 'fail': f, 'no_marks': nm}