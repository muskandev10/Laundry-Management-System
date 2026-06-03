from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import (
    SignUpForm, LoginForm, LaundryRequestForm,
    TrackingForm, AdminLoginForm,
)
from .models import LaundryOrder, OrderTracking


# ── Authentication Views ──────────────────────────────────────────────


def signup_view(request):
    """Register a new user account."""
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('home')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! Please sign in.')
            return redirect('login')
    else:
        form = SignUpForm()

    return render(request, 'signup_page.html', {'form': form})


def login_view(request):
    """Authenticate and log in a user."""
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_staff:
                    return redirect('admin_dashboard')
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'login_page.html', {'form': form})


@login_required
def logout_view(request):
    """Log out the current user."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


# ── Page Views ─────────────────────────────────────────────────────────
@login_required
def home_view(request):
    return render(request, 'welcome.html')



@login_required
def about_view(request):

    if request.user.is_staff:
        return redirect('admin_dashboard')

    return render(request, 'about.html')
def services_view(request):
    """Display the list of services and their prices."""
    services_data = [
        {'name': 'Washing', 'price': 40, 'icon': 'fa-soap', 'description': 'Standard machine wash with premium detergents.'},
        {'name': 'Ironing', 'price': 30, 'icon': 'fa-fire', 'description': 'Steam ironing for crisp, wrinkle-free clothes.'},
        {'name': 'Dry Cleaning', 'price': 80, 'icon': 'fa-wind', 'description': 'Specialized cleaning for delicate fabrics.'},
        {'name': 'Wash & Iron', 'price': 60, 'icon': 'fa-tshirt', 'description': 'Complete package: washed, dried, and ironed.'},
    ]
    return render(request, 'services.html', {'services': services_data})
# ── Laundry Request Views ─────────────────────────────────────────────
@login_required
def request_view(request):
    """Display and process the laundry request form."""

    if request.user.is_staff:
        return redirect('admin_dashboard')

    if request.method == 'POST':
        form = LaundryRequestForm(request.POST)

        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()   

            # Tracking create AFTER saving order
            OrderTracking.objects.create(order=order, status=0)

            return render(request, 'requestdone.html', {
                'TrackingId': order.pk,
                'Name': order.full_name,
                'Address': order.address,
                'Price': order.price,
            })

    else:
        form = LaundryRequestForm()

    return render(request, 'request.html', {'form': form})

# ── Tracking Views ─────────────────────────────────────────────────────
@login_required
def track_view(request):

    if request.user.is_staff:
        return redirect('admin_dashboard')

    form = TrackingForm()
    return render(request, 'trackstatus.html', {'form': form})

@login_required
def tracking_details_view(request):
    """Look up order status by tracking ID."""

    if request.user.is_staff:
        return redirect('admin_dashboard')

    status_label = ''
    error = ''

    if request.method == 'POST':
        form = TrackingForm(request.POST)
        if form.is_valid():
            tracking_id = form.cleaned_data['tracking_id']
            try:
                tracking = OrderTracking.objects.get(order__pk=tracking_id)
                status_label = tracking.get_status_display_label()
            except OrderTracking.DoesNotExist:
                error = 'No order found with that Tracking ID.'
    else:
        form = TrackingForm()

    return render(request, 'statusshow.html', {
        'Status': status_label,
        'error': error,
        'form': form,
    })


@login_required
def my_orders_view(request):
    """Display the order history for the logged-in user."""
    
    if request.user.is_staff:
        return redirect('admin_dashboard')

    # Get orders with related tracking and bill info for efficient database access
    # 'bill' is accessed via the related OneToOne relationship if it exists
    orders = LaundryOrder.objects.filter(user=request.user).select_related('tracking')
    
    return render(request, 'my_orders.html', {'orders': orders})



# ── Admin Views ────────────────────────────────────────────────────────


def admin_login_view(request):
    """Admin login page (uses Django's built-in auth, checks is_staff)."""
    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_staff:
                login(request, user)
                return redirect('admin_dashboard')
            else:
                messages.error(request, 'Invalid admin credentials.')
    else:
        form = AdminLoginForm()

    return render(request, 'AdminLogin.html', {'form': form})


@login_required
def admin_dashboard_view(request):
    """Admin dashboard showing all laundry orders."""
    if not request.user.is_staff:
        messages.error(request, 'You do not have admin privileges.')
        return redirect('home')

    orders = LaundryOrder.objects.select_related('tracking').all()
    return render(request, 'WelcomeAdmin.html', {'orders': orders})


@login_required
def delete_order_view(request, order_id):
    """Delete a laundry order (admin only)."""
    if not request.user.is_staff:
        messages.error(request, 'You do not have admin privileges.')
        return redirect('home')

    try:
        order = LaundryOrder.objects.get(pk=order_id)
        order.delete()
        messages.success(request, f'Order #{order_id} has been deleted.')
    except LaundryOrder.DoesNotExist:
        messages.error(request, 'Order not found.')

    return redirect('admin_dashboard')
    
@login_required
def update_status_view(request, order_id):
    if not request.user.is_staff:
        messages.error(request, 'You do not have admin privileges.')
        return redirect('home')

    if request.method == 'POST':
        status = request.POST.get('status')

        tracking = OrderTracking.objects.get(order__pk=order_id)
        tracking.status = status
        tracking.save()

    return redirect('admin_dashboard')

