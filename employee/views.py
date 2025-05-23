# employee/views.py
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from .models import LeaveRequest, EmployeeProfile
from .forms import LeaveRequestForm

@login_required
def dashboard(request):
    leave_balance = LeaveRequest.objects.filter(employee=request.user, status='approved')
    leave_history = LeaveRequest.objects.filter(employee=request.user).order_by('-applied_at')
    profile = request.user.employeeprofile  # 🔑 Fetch remaining leaves from profile
    return render(request, 'employee/dashboard.html', {
        'leave_balance': leave_balance,
        'leave_history': leave_history,
        'remaining_leaves': profile.remaining_leaves,  # ✅ Pass it to template
    })


@login_required
def apply_leave(request):
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.employee = request.user

            days_requested = (leave_request.end_date - leave_request.start_date).days + 1
            profile = request.user.employeeprofile

            # ❌ Check for overlapping leaves
            overlapping = LeaveRequest.objects.filter(
                employee=request.user,
                status__in=['pending', 'approved'],  # only block active leaves
                start_date__lte=leave_request.end_date,
                end_date__gte=leave_request.start_date
            ).exists()

            if overlapping:
                form.add_error(None, 'You already have a leave request that overlaps with these dates.')
            elif days_requested > profile.remaining_leaves:
                form.add_error(None, 'You do not have enough leave balance.')
            else:
                leave_request.save()
                profile.remaining_leaves -= days_requested
                profile.save()
                return redirect('dashboard')

    else:
        form = LeaveRequestForm()
    return render(request, 'employee/apply_leave.html', {'form': form})


@login_required
def edit_leave(request, pk):
    leave_request = get_object_or_404(LeaveRequest, pk=pk, employee=request.user, status='pending')
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST, instance=leave_request)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = LeaveRequestForm(instance=leave_request)
    return render(request, 'employee/edit_leave.html', {'form': form})

@login_required
def cancel_leave(request, pk):
    leave_request = get_object_or_404(LeaveRequest, pk=pk, employee=request.user)

    if leave_request.status != 'pending':
        return render(request, 'employee/cancel_leave.html', {
            'error': 'You can only cancel pending leave requests.'
        })

    if request.method == 'POST':
        # Optional: Add back leave days if already deducted
        days_requested = (leave_request.end_date - leave_request.start_date).days + 1
        profile = request.user.employeeprofile
        profile.remaining_leaves += days_requested
        profile.save()

        leave_request.delete()
        return redirect('dashboard')

    return render(request, 'employee/cancel_leave.html', {'leave_request': leave_request})

