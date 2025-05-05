import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import os

# Create visualizations directory if it doesn't exist
if not os.path.exists('visualizations'):
    os.makedirs('visualizations')

# Training metrics data
epochs = [1, 2, 3]
accuracy = [92.8, 93.6, 94.2]  # Latest accuracy metrics
loss = [0.3245, 0.1834, 0.1645]  # Loss values
speed = [2.29, 2.40, 2.44]  # Batch processing speed

# Set style
plt.style.use('seaborn')
sns.set_palette("husl")

# Figure 1: Training Metrics
plt.figure(figsize=(12, 6))
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

# Accuracy and Loss Plot
ax1.plot(epochs, accuracy, 'b-o', label='Accuracy (%)', linewidth=2)
ax1_twin = ax1.twinx()
ax1_twin.plot(epochs, loss, 'r-o', label='Loss', linewidth=2)
ax1.set_xlabel('Epoch')
ax1.set_ylabel('Accuracy (%)')
ax1_twin.set_ylabel('Loss')
ax1.set_title('Training Accuracy and Loss')
ax1.grid(True)

# Add both legends
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax1_twin.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

# Speed Plot
ax2.plot(epochs, speed, 'g-o', label='Processing Speed', linewidth=2)
ax2.set_xlabel('Epoch')
ax2.set_ylabel('Batches/Second')
ax2.set_title('Training Speed')
ax2.grid(True)
ax2.legend()

plt.tight_layout()
plt.savefig('visualizations/training_metrics.png')
plt.close()

# Figure 2: GPU Performance
plt.figure(figsize=(10, 6))
metrics = ['Memory Usage', 'Power Usage', 'Temperature']
values = [3.8/8*100, 118/150*100, 72/100*100]  # Convert to percentages

colors = ['#2ecc71', '#3498db', '#e74c3c']
plt.bar(metrics, values, color=colors)
plt.axhline(y=80, color='r', linestyle='--', alpha=0.5, label='Optimal Range')
plt.title('GPU Resource Utilization')
plt.ylabel('Percentage (%)')
plt.ylim(0, 100)

# Add value labels on top of each bar
for i, v in enumerate(values):
    plt.text(i, v + 1, f'{v:.1f}%', ha='center')

plt.legend()
plt.tight_layout()
plt.savefig('visualizations/gpu_metrics.png')
plt.close()

print("Training visualization charts have been generated in the 'visualizations' directory.")
