import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Function to add regions to the plot
def add_region(ax, start, duration, y, label, color):
    ax.add_patch(
        patches.Rectangle(
            (start, y), duration, 0.5, color=color, edgecolor='black', linewidth=1
        )
    )
    ax.text(start + duration / 2, y + 0.55, label, ha='center', va='bottom', color='black', fontsize=7, rotation=45, bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

# Data from the given log
data = [
    ('Writer 0', 0.000114, 'write', 'Value 10 to location 3'),
    ('Writer 1', 0.000192, 'write', 'Value 20 to location 1'),
    ('Writer 0', 0.000246, 'write', 'Value 10 to location 2'),
    ('Writer 2', 0.000265, 'write', 'Value 30 to location 0'),
    ('Writer 1', 0.000286, 'write', 'Value 20 to location 3'),
    ('Writer 3', 0.000336, 'write', 'Value 40 to location 0'),
    ('Writer 2', 0.000355, 'write', 'Value 30 to location 1'),
    ('Writer 0', 0.000359, 'write', 'Value 10 to location 2'),
    ('Writer 1', 0.000375, 'write', 'Value 20 to location 4'),
    ('Snapshot 0', 0.000429, 'snapshot', 'Collected at 0.000429, duration: 0.000016'),
    ('Writer 3', 0.000448, 'write', 'Value 40 to location 1'),
    ('Writer 0', 0.000457, 'write', 'Value 10 to location 2'),
    ('Writer 2', 0.000481, 'write', 'Value 30 to location 2'),
    ('Writer 1', 0.000485, 'write', 'Value 20 to location 0'),
    ('Snapshot 1', 0.000479, 'snapshot', 'Collected at 0.000479, duration: 0.000013'),
    ('Writer 3', 0.000553, 'write', 'Value 40 to location 4'),
    ('Writer 0', 0.000570, 'write', 'Value 10 to location 3'),
    ('Snapshot 2', 0.000556, 'snapshot', 'Collected at 0.000556, duration: 0.000019'),
    ('Writer 2', 0.000582, 'write', 'Value 30 to location 1'),
    ('Writer 1', 0.000583, 'write', 'Value 20 to location 0'),
    ('Snapshot 0', 0.000580, 'snapshot', 'Collected at 0.000580, duration: 0.000003'),
    ('Snapshot 1', 0.000596, 'snapshot', 'Collected at 0.000596, duration: 0.000004'),
    ('Snapshot 3', 0.000641, 'snapshot', 'Collected at 0.000641, duration: 0.000015')
]

# Function to simulate register state
register_state = [0, 0, 0, 0, 0]

# Function to update register state after each write and check snapshot consistency
def update_register_state_and_check(data):
    state_history = []
    for entry in data:
        thread, time, action, description = entry
        if action == 'write':
            # Parse value and location
            value = int(description.split()[1])
            location = int(description.split()[-1])
            # Update the register state
            register_state[location] = value
            state_history.append((time, list(register_state)))
        elif action == 'snapshot':
            # Parse snapshot start time and duration
            duration = float(description.split('duration: ')[-1]) / 1000000  # convert microseconds to seconds
            start_time = time
            snapshot_state = list(register_state)
            state_history.append((start_time, snapshot_state))
    return state_history

# Get the state history
state_history = update_register_state_and_check(data)

# Print the register state after each write and snapshot
for time, state in state_history:
    print(f'Time: {time:.6f}, Register State: {state}')

# Plot settings
fig, ax = plt.subplots(figsize=(15, 10))
ax.set_xlim(0, 0.001)
ax.set_ylim(0, 8)
ax.set_xlabel('Time (seconds)')
ax.set_yticks([0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5])
ax.set_yticklabels(['Snapshot 3', 'Snapshot 2', 'Snapshot 1', 'Snapshot 0', 'Writer 3', 'Writer 2', 'Writer 1', 'Writer 0'])
ax.set_title('Linearization Diagram')

# Adding regions for each writer and snapshot thread
writer_positions = {'Writer 0': 7, 'Writer 1': 6, 'Writer 2': 5, 'Writer 3': 4}
snapshot_positions = {'Snapshot 0': 3, 'Snapshot 1': 2, 'Snapshot 2': 1, 'Snapshot 3': 0}
colors = {'write': 'blue', 'snapshot': 'green'}

for entry in data:
    thread, time, action, description = entry
    if action == 'write':
        y_pos = writer_positions.get(thread, None)
        if y_pos is not None:
            add_region(ax, start=time, duration=0.00001, y=y_pos, label=description, color=colors[action])
    elif action == 'snapshot':
        y_pos = snapshot_positions.get(thread, None)
        if y_pos is not None:
            start_time = time
            duration = float(description.split('duration: ')[-1]) / 1000000  # convert microseconds to seconds
            add_region(ax, start=start_time, duration=duration, y=y_pos, label=f'{thread} {description}', color=colors[action])

# Display the plot
plt.tight_layout()
plt.show()