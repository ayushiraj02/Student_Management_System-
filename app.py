from functools import wraps
from flask import (Flask, render_template, request, redirect,
                   url_for, session, flash)
from models import StudentManager, FileStorage
from auth import UserAuth

app = Flask(__name__)
app.secret_key = 'change_this_in_production_123'

# Initialize storage & managers
student_storage = FileStorage('data/students.json')
student_manager = StudentManager(student_storage)
auth = UserAuth('data/users.json')


# ---- Login required decorator ----
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            flash('Please login first!', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


# ========== AUTH ROUTES ==========

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if auth.verify_user(username, password):
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid username or password!', 'error')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


# ========== DASHBOARD ==========

@app.route('/dashboard')
@login_required
def dashboard():
    students = student_manager.get_all_students()
    pf = student_manager.get_pass_fail_count()
    return render_template('dashboard.html',
                           total_students=len(students),
                           pass_count=pf['pass'],
                           fail_count=pf['fail'],
                           username=session.get('username'))


# ========== STUDENT CRUD ==========

@app.route('/students')
@login_required
def list_students():
    students = student_manager.get_all_students()
    return render_template('list_students.html', students=students)


@app.route('/students/add', methods=['GET', 'POST'])
@login_required
def add_student():
    if request.method == 'POST':
        roll_no = request.form.get('roll_no')
        name    = request.form.get('name')
        age     = request.form.get('age')
        course  = request.form.get('course')
        email   = request.form.get('email')
        success, msg = student_manager.add_student(roll_no, name, age, course, email)
        flash(msg, 'success' if success else 'error')
        if success:
            return redirect(url_for('list_students'))
    return render_template('add_student.html')


@app.route('/students/edit/<roll_no>', methods=['GET', 'POST'])
@login_required
def edit_student(roll_no):
    student = student_manager.search_student(roll_no)
    if not student:
        flash('Student not found!', 'error')
        return redirect(url_for('list_students'))
    if request.method == 'POST':
        name   = request.form.get('name')
        age    = request.form.get('age')
        course = request.form.get('course')
        email  = request.form.get('email')
        success, msg = student_manager.update_student(roll_no, name, age, course, email)
        flash(msg, 'success' if success else 'error')
        if success:
            return redirect(url_for('list_students'))
    return render_template('edit_student.html', student=student)


@app.route('/students/delete/<roll_no>', methods=['POST'])
@login_required
def delete_student(roll_no):
    success, msg = student_manager.delete_student(roll_no)
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('list_students'))


@app.route('/students/search', methods=['GET', 'POST'])
@login_required
def search_student():
    results = []
    if request.method == 'POST':
        query = request.form.get('query', '').lower()
        for s in student_manager.get_all_students():
            if query in s.roll_no.lower() or query in s.name.lower():
                results.append(s)
        if not results:
            flash('No students found!', 'error')
    return render_template('search.html', results=results)


@app.route('/students/<roll_no>', methods=['GET', 'POST'])
@login_required
def student_details(roll_no):
    student = student_manager.search_student(roll_no)
    if not student:
        flash('Student not found!', 'error')
        return redirect(url_for('list_students'))

    if request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age')
        course = request.form.get('course')
        email = request.form.get('email')
        success, msg = student_manager.update_student(roll_no, name, age, course, email)
        flash(msg, 'success' if success else 'error')
        return redirect(url_for('student_details', roll_no=roll_no))

    return render_template('student_details.html', student=student)


# ========== MARKS ==========

@app.route('/students/<roll_no>/marks', methods=['GET', 'POST'])
@login_required
def add_marks(roll_no):
    student = student_manager.search_student(roll_no)
    if not student:
        flash('Student not found!', 'error')
        return redirect(url_for('list_students'))
    if request.method == 'POST':
        subject = request.form.get('subject')
        mark    = request.form.get('mark')
        success, msg = student_manager.add_marks(roll_no, subject, mark)
        flash(msg, 'success' if success else 'error')
        return redirect(url_for('add_marks', roll_no=roll_no))
    return render_template('add_marks.html', student=student)


@app.route('/students/<roll_no>/marks/delete/<subject>', methods=['POST'])
@login_required
def delete_mark(roll_no, subject):
    student = student_manager.search_student(roll_no)
    if student and subject in student.marks:
        del student.marks[subject]
        student_manager._save_students()
        flash(f'{subject} marks deleted!', 'success')
    return redirect(url_for('add_marks', roll_no=roll_no))


# ========== REPORTS ==========

@app.route('/reports')
@login_required
def reports():
    return render_template('reports.html',
                           topper_list=student_manager.get_topper_list(5),
                           average=student_manager.get_average_marks(),
                           subject_stats=student_manager.get_subject_statistics(),
                           pass_fail=student_manager.get_pass_fail_count())


if __name__ == '__main__':
    app.run(debug=True)