import matplotlib.pyplot as plt

# Sample values
t_mean = 46
c_mean = 54
total = t_mean + c_mean
t_pct = (t_mean / total) * 100
c_pct = (c_mean / total) * 100

fig, ax = plt.subplots(figsize=(8, 1))  # 1 inch tall = thinner
ax.barh(0, t_pct, color='#D8FFFD', edgecolor='black', height=0.1)
ax.barh(0, -c_pct, color='#7493A9', edgecolor='black', height=0.1)

# Middle vertical line
ax.axvline(x=0, color='black', linewidth=2)

# Outside labels
ax.text(-105, 0, f'Target: {t_pct:.0f}%', va='center', ha='left', fontsize=11, color='black')
ax.text(105, 0, f'Compensation: {c_pct:.0f}%', va='center', ha='right', fontsize=11, color='black')

# Clean layout
ax.set_xlim(-120, 120)  # expand for spacing around labels
ax.set_ylim(-0.5, 0.5)
ax.set_yticks([])
ax.set_xticks([])
ax.set_frame_on(False)

plt.tight_layout(pad=1.0)
plt.savefig("slim_ratio_bar.jpg", bbox_inches='tight', dpi=200)
plt.show()

