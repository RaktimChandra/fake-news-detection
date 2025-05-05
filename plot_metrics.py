import matplotlib.pyplot as plt
import os

# Create visualizations directory if it doesn't exist
if not os.path.exists('visualizations'):
    os.makedirs('visualizations')

# Training metrics data
epochs = [1, 2, 3]
accuracy = [92.8, 93.6, 94.2]
loss = [0.3245, 0.1834, 0.1645]
speed = [2.29, 2.40, 2.44]

# Plot 1: Training Metrics
plt.figure(figsize=(10, 6))
plt.plot(epochs, accuracy, 'b-o', label='Accuracy (%)')
plt.plot(epochs, [l * 100 for l in loss], 'r-o', label='Loss x100')
plt.xlabel('Epoch')
plt.ylabel('Value')
plt.title('Training Metrics Progress')
plt.grid(True)
plt.legend()
plt.savefig('visualizations/training_progress.png')
plt.close()

# Plot 2: Processing Speed
plt.figure(figsize=(10, 6))
plt.plot(epochs, speed, 'g-o')
plt.xlabel('Epoch')
plt.ylabel('Batches/Second')
plt.title('Training Speed')
plt.grid(True)
plt.savefig('visualizations/training_speed.png')
plt.close()

# Plot 3: GPU Metrics
metrics = ['Memory', 'Power', 'Temperature']
values = [47.5, 78.7, 72.0]  # Percentages

plt.figure(figsize=(10, 6))
plt.bar(metrics, values)
plt.ylabel('Percentage (%)')
plt.title('GPU Resource Utilization')
for i, v in enumerate(values):
    plt.text(i, v + 1, f'{v}%', ha='center')
plt.savefig('visualizations/gpu_metrics.png')
plt.close()

print("Generated visualization charts in 'visualizations' directory")
