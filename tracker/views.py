# tracker/views.py
import json
from datetime import date, datetime
from django.shortcuts import render, redirect, get_object_or_404
from .models import WaterIntake
from .forms import WaterIntakeForm

def index(request):
    # --- Conversion factors and color mappings ---
    conversion = {
        'water': 1.0,
        'sparkling water': 0.95,
        'coffee': 0.8,
        'tea': 0.8,
        'juice': 0.75,
        'soda': 0.3,
        'wine': 0.3,
        'beer': 0.3,
        'other': 1.0,
    }
    color_mapping = {
        'water': 'rgba(0, 123, 255, 0.6)',
        'sparkling water': 'rgba(100, 149, 237, 0.6)',
        'coffee': 'rgba(210, 180, 140, 0.6)',
        'tea': 'rgba(205, 133, 63, 0.6)',
        'juice': 'rgba(255, 165, 0, 0.6)',
        'soda': 'rgba(220, 20, 60, 0.6)',
        'wine': 'rgba(128, 0, 128, 0.6)',
        'beer': 'rgba(255, 215, 0, 0.6)',
        'other': 'rgba(128, 128, 128, 0.6)',
    }
    border_mapping = {k: v.replace('0.6', '1') for k, v in color_mapping.items()}

    # --- Determine the selected date for the bottle chart ---
    today = date.today()
    selected_date_str = request.GET.get('date')
    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = today
    else:
        selected_date = today

    # --- Handle new entry submission ---
    if request.method == 'POST':
        form = WaterIntakeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = WaterIntakeForm()

    # --- Compute effective totals for the selected day ---
    def effective_total(person, day):
        entries = WaterIntake.objects.filter(person=person, entry_date=day)
        return sum(entry.amount * conversion.get(entry.liquid_type, 1.0) for entry in entries)

    selected_sebo_total = effective_total('sebo', selected_date)
    selected_alomi_total = effective_total('alomi', selected_date)
    sebo_goal = 100
    alomi_goal = 64
    selected_sebo_percentage = min((selected_sebo_total / sebo_goal) * 100, 100)
    selected_alomi_percentage = min((selected_alomi_total / alomi_goal) * 100, 100)

    # --- Compute breakdown for the selected day for water bottle segments ---
    def get_breakdown(person, day):
        breakdown = {}
        entries = WaterIntake.objects.filter(person=person, entry_date=day)
        for entry in entries:
            eff = entry.amount * conversion.get(entry.liquid_type, 1.0)
            breakdown[entry.liquid_type] = breakdown.get(entry.liquid_type, 0) + eff
        return breakdown

    sebo_breakdown = get_breakdown('sebo', selected_date)
    alomi_breakdown = get_breakdown('alomi', selected_date)

    def compute_segments(breakdown, goal):
        segments = []
        for lt in conversion.keys():
            if lt in breakdown:
                eff = breakdown[lt]
                pct = (eff / goal) * 100
                segments.append({
                    'liquid_type': lt,
                    'percentage': pct,
                    'color': color_mapping[lt],
                })
        return segments

    sebo_segments = compute_segments(sebo_breakdown, sebo_goal)
    alomi_segments = compute_segments(alomi_breakdown, alomi_goal)

    def add_offsets(segments):
        cum = 0
        for seg in segments:
            seg['offset'] = cum
            cum += seg['percentage']
        return segments

    sebo_segments = add_offsets(sebo_segments)
    alomi_segments = add_offsets(alomi_segments)

    # --- Compute all-time totals for each person ---
    all_entries = WaterIntake.objects.all()
    total_sebo = sum(entry.amount * conversion.get(entry.liquid_type, 1.0) for entry in all_entries if entry.person == 'sebo')
    total_alomi = sum(entry.amount * conversion.get(entry.liquid_type, 1.0) for entry in all_entries if entry.person == 'alomi')

    # --- Compute historical daily consumption (for the grouped, stacked bar chart) ---
    distinct_dates = sorted({entry.entry_date for entry in all_entries})
    labels = [d.strftime("%b %d") for d in distinct_dates]

    # Build a data structure: daily_data[date][person][liquid_type] = effective amount
    daily_data = {}
    for d in distinct_dates:
        daily_data[d] = {
            'sebo': {lt: 0 for lt in conversion.keys()},
            'alomi': {lt: 0 for lt in conversion.keys()},
        }
    for entry in all_entries:
        eff = entry.amount * conversion.get(entry.liquid_type, 1.0)
        daily_data[entry.entry_date][entry.person][entry.liquid_type] += eff

    # Compute total effective consumption per person for each day
    daily_totals = {'sebo': [], 'alomi': []}
    for d in distinct_dates:
        total_sebo_day = sum(daily_data[d]['sebo'].values())
        total_alomi_day = sum(daily_data[d]['alomi'].values())
        daily_totals['sebo'].append(total_sebo_day)
        daily_totals['alomi'].append(total_alomi_day)

    # Create historical datasets for the grouped, stacked bar chart.
    # (We no longer override the color to red.)
    historical_datasets = []
    for person in ['sebo', 'alomi']:
        for lt in conversion.keys():
            data = [daily_data[d][person][lt] for d in distinct_dates]
            bg_colors = [color_mapping[lt]] * len(distinct_dates)
            historical_datasets.append({
                'label': f"{person.capitalize()} - {lt.title()}",
                'data': data,
                'backgroundColor': bg_colors,
                'borderColor': border_mapping[lt],
                'borderWidth': 1,
                'stack': person,  # Groups all beverage segments for a person.
            })

    context = {
        # ... your previously computed context items ...
        'form': form,
        'selected_date': selected_date.strftime('%Y-%m-%d'),
        'selected_sebo_total': selected_sebo_total,
        'selected_alomi_total': selected_alomi_total,
        'selected_sebo_percentage': selected_sebo_percentage,
        'selected_alomi_percentage': selected_alomi_percentage,
        'sebo_segments': sebo_segments,
        'alomi_segments': alomi_segments,
        'total_sebo': total_sebo,
        'total_alomi': total_alomi,
        'historical_labels': json.dumps(labels),
        'historical_datasets': json.dumps(historical_datasets),
        'historical_totals': json.dumps(daily_totals),  # NEW: daily totals per person.
        'sebo_goal': sebo_goal,
        'alomi_goal': alomi_goal,
    }
    return render(request, 'tracker/index.html', context)



from django.shortcuts import get_object_or_404, redirect

def entry_list(request):
    # List all WaterIntake entries, ordered by date (newest first)
    entries = WaterIntake.objects.all().order_by('-entry_date', '-id')
    return render(request, 'tracker/entry_list.html', {'entries': entries})

def entry_update(request, pk):
    # Allow editing of an entry identified by its primary key (pk)
    entry = get_object_or_404(WaterIntake, pk=pk)
    if request.method == 'POST':
        form = WaterIntakeForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect('entry_list')
    else:
        form = WaterIntakeForm(instance=entry)
    return render(request, 'tracker/entry_form.html', {'form': form, 'entry': entry})

def entry_delete(request, pk):
    # Allow deletion of an entry identified by its primary key (pk)
    entry = get_object_or_404(WaterIntake, pk=pk)
    if request.method == 'POST':
        entry.delete()
        return redirect('entry_list')
    return render(request, 'tracker/entry_confirm_delete.html', {'entry': entry})
