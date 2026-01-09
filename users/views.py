from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth import logout as django_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.mail import send_mail
import random
from django.utils import timezone
from datetime import timedelta
from courses.models import Course, Enrollment
from .forms import StudentRegistrationForm, RegisterForm  # Ensure RegisterForm is imported
from courses.models import Course
from django.contrib.auth import update_session_auth_hash

User = get_user_model()

# ==========================================
# 1. HELPER FUNCTIONS
# ==========================================
@login_required
def course_test_secure(request, course_id):  # Your view name might be different
    # 1. Fetch the course
    course = get_object_or_404(Course, id=course_id)

    # ================= PASTE CODE HERE =================
    # 🔒 SECURITY CHECK: Kick out students who haven't paid
    enrollment = Enrollment.objects.filter(
        user=request.user, 
        course=course,
        expires_at__gt=timezone.now()
    ).first()
    
    if not enrollment:
        messages.error(request, "Access Denied: You must enroll to take the test.")
        return redirect('course_detail', course_id=course_id)
    # ===================================================

    # 2. Your existing logic for the test (handling answers, calculating score, etc.)
    if request.method == 'POST':
        # ... logic to grade the test ...
        pass

    return render(request, 'users/course_test.html', {'course': course})



def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(user_email, otp_code):
    """Sends an OTP to the user's email address."""
    subject = 'Verify Your Account - Academic Factor'
    message = f'Hello,\n\nYour OTP Code is: {otp_code}\n\nPlease enter this on the website.'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user_email]
    
    try:
        send_mail(subject, message, email_from, recipient_list)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

# ==========================================
# 2. PASSWORD RESET FLOW
# ==========================================

def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "No user found with this email.")
            return render(request, 'users/forgot_password.html')

        # Generate and Send OTP
        otp = generate_otp()
        send_otp_email(email, otp)
        
        # Save state in session
        request.session['reset_otp'] = otp
        request.session['reset_email'] = email
        
        messages.success(request, f"OTP sent to {email}")
        return redirect('verify_reset_otp') # Redirect to specific reset verification

    return render(request, 'users/forgot_password.html')

def verify_reset_otp_view(request):
    """Specific view for verifying Password Reset OTPs"""
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        session_otp = request.session.get('reset_otp')
        
        if entered_otp and session_otp and entered_otp == session_otp:
            request.session['otp_verified'] = True
            return redirect('reset_new_password')
        else:
            messages.error(request, "Invalid OTP. Please try again.")
    
    return render(request, 'users/verify_otp.html')
def reset_new_password_view(request):
    # 1. Security check: User must have verified OTP
    if not request.session.get('otp_verified'):
        return redirect('forgot_password')

    email = request.session.get('reset_email')
    user = get_object_or_404(User, email=email)

    if request.method == 'POST':
        new_password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # 2. Validation: Ensure passwords match
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
        else:
            # 3. Hash and Save
            user.set_password(new_password)
            
            # ✅ THE IMPORTANT FIX: Ensure user is Active
            if not user.is_active:
                user.is_active = True
                
            user.save()
            
            # 4. Cleanup Session
            request.session['otp_verified'] = False
            if 'reset_otp' in request.session:
                del request.session['reset_otp']
            if 'reset_email' in request.session:
                del request.session['reset_email']
            
            # 5. Success Message & Redirect
            messages.success(request, "Password reset successful! Your account has been activated. Please log in.")
            return redirect('login')

    return render(request, 'users/reset_new_password.html', {'user': user})
# ==========================================
# 3. REGISTRATION FLOW (EMAIL OTP)
# ==========================================

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # 1. Create user instance
            user = form.save(commit=False)
            
            # 2. Set attributes
            user.is_active = False  # Set flag
            otp_code = generate_otp()
            user.otp = otp_code
            
            # 3. Save to Database
            user.save()

            # 🔒 FORCE LOCK: Explicitly update the DB column to False
            # This fixes the issue if signals or forms are interfering
            User.objects.filter(id=user.id).update(is_active=False)

            # 4. Send Email & Redirect
            send_otp_email(user.email, otp_code)
            request.session['email_to_verify'] = user.email
            
            messages.success(request, f"Verification code sent to {user.email}")
            return redirect('verify_registration_otp')
    else:
        form = RegisterForm()
    
    return render(request, 'users/register.html', {'form': form})

def verify_registration_otp(request):
    """Specific view for verifying Registration OTPs"""
    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        email_to_verify = request.session.get('email_to_verify')
        
        if not email_to_verify:
            messages.error(request, "Session expired. Please register again.")
            return redirect('register')

        try:
            user = User.objects.get(email=email_to_verify)
            
            # Check OTP match
            if user.otp == otp_input:
                # Activate User
                user.is_active = True
                user.otp = None  # Clear OTP
                user.save()
                
                # Clear session
                del request.session['email_to_verify']
                
                # Log them in automatically (optional)
                login(request, user)
                
                messages.success(request, "Account verified! Welcome to Academic Factor.")
                return redirect('courses')
            else:
                messages.error(request, "Invalid OTP. Please try again.")
        
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect('register')

    return render(request, 'users/verify_otp.html')

# ==========================================
# 4. AUTH & COURSE VIEWS
# ==========================================

def login_view(request):
    if request.method == "POST":
        u_name = request.POST.get('username', '').strip()
        p_word = request.POST.get('password', '').strip()

        # 1. Authenticate
        user = authenticate(request, username=u_name, password=p_word)

        if user is not None:
            # 🔒 SECURITY CHECK: Are they active?
            if not user.is_active:
                messages.error(request, "Your account is not verified. Please check your email for the OTP.")
                
                # Optional: Help them verify immediately
                request.session['email_to_verify'] = user.email
                return redirect('verify_registration_otp')

            # ✅ If Active, Log them in
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('courses')
        else:
            # 2. Handle Login Failures
            # Check if user exists but is inactive (for better error messages)
            existing_user = User.objects.filter(username=u_name).first()
            if existing_user and not existing_user.is_active:
                messages.error(request, "Account not verified. Please enter your OTP.")
                request.session['email_to_verify'] = existing_user.email
                return redirect('verify_registration_otp')

            messages.error(request, "Username or password is incorrect.")
    
    return render(request, "users/login.html")


def logout_view(request):
    django_logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('login')

def courses(request):
    if request.user.is_authenticated:
        # Courses user owns
        my_courses = request.user.enrolled_courses.all()
        # Courses user does NOT own (exclude existing IDs)
        recommended_courses = Course.objects.exclude(id__in=my_courses.values_list('id', flat=True))
    else:
        my_courses = []
        recommended_courses = Course.objects.all()

    context = {
        'my_courses': my_courses,
        'recommended_courses': recommended_courses
    }
    return render(request, 'users/courses.html', context)

def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    is_enrolled = False
    if request.user.is_authenticated:
        if course.students.filter(id=request.user.id).exists():
            is_enrolled = True

    context = {
        'course': course,
        'is_enrolled': is_enrolled,
    }
    return render(request, 'users/course_detail.html', context)

@login_required
def enroll_course(request, course_id):
    if request.method == 'POST':
        course = get_object_or_404(Course, id=course_id)
        course.students.add(request.user)
        messages.success(request, f"Success! You are now enrolled in {course.title}.")
        return redirect('course_detail', course_id=course_id)

    return redirect('course_detail', course_id=course_id)

@login_required
def lesson_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    # 1. CHECK ENROLLMENT & EXPIRY
    # We look for an enrollment that matches User + Course + Future Expiry Date
    enrollment = Enrollment.objects.filter(
        user=request.user, 
        course=course,
        expires_at__gt=timezone.now()  # "gt" means Greater Than (in the future)
    ).first()
    
    if not enrollment:
        messages.error(request, "Access Denied: You must buy this course or your subscription has expired.")
        return redirect('course_detail', course_id=course_id)
    
    context = {
        'course': course,
        'user_name': f"{request.user.first_name} {request.user.last_name}",
        'user_id': request.user.id_number,
        'days_left': (enrollment.expires_at - timezone.now()).days # Show days remaining
    }
    return render(request, 'users/lesson.html', context)

@login_required
def payment_checkout(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    # Check if already enrolled and active
    active_enrollment = Enrollment.objects.filter(
        user=request.user, 
        course=course, 
        expires_at__gt=timezone.now()
    ).exists()
    
    if active_enrollment:
        messages.info(request, "You already own this course!")
        return redirect('course_detail', course_id=course_id)

    return render(request, 'users/payment_checkout.html', {'course': course})


# 2. Process the "Fake" Payment
@login_required
def payment_success(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    # --- LOGIC: Give Access for 1 Year (365 Days) ---
    expiry_date = timezone.now() + timedelta(days=365)
    
    # Create or Update Enrollment
    Enrollment.objects.update_or_create(
        user=request.user,
        course=course,
        defaults={'expires_at': expiry_date}
    )
    
    # (Optional) Keep the old 'students' list for simple admin counting
    course.students.add(request.user) 
    
    messages.success(request, f"Payment Successful! Course expires on {expiry_date.strftime('%d %b %Y')}.")
    return redirect('course_detail', course_id=course_id)

