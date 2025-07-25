import numpy as np
import os
import matplotlib.pyplot as plt
from fpdf import FPDF  # For PDF export
from pathlib import Path


class SessionAnalyzer:
    def __init__(self, data, duration="00:00", repetitions=0, biofeedback_response="Unknown"):
   
        self.data = data
        self.duration = duration
        self.repetitions = repetitions
        self.biofeedback_response = biofeedback_response

    def calculate_avg_ratios(self):
        ratios = {}
        keys = list(self.data.keys())
        for i in range(len(keys)-1):
            t, c = keys[i], keys[i+1]
            target_mean = np.mean(self.data[t])
            comp_mean = np.mean(self.data[c])
            ratios[f"{t}/{c}"] = target_mean / comp_mean if comp_mean != 0 else np.inf
        return ratios

    # MVIC and Threshold calculations are commented out for now
    # def calculate_percent_mvic(self):
    #     percent = {}
    #     for muscle, signal in self.data.items():
    #         if muscle in self.mvic:
    #             peak = np.max(signal)
    #             percent[muscle] = (peak / self.mvic[muscle]) * 100
    #     return percent

    # def compare_to_threshold(self):
    #     comparison = {}
    #     for muscle, signal in self.data.items():
    #         if muscle in self.thresholds:
    #             ratio = np.mean(signal) / self.thresholds[muscle]
    #             comparison[muscle] = ratio
    #     return comparison

    # Calculate success rate based on repetitions
    def calculate_success_rate(self):
        keys = list(self.data.keys())
        if len(keys) < 2 or self.repetitions == 0:
            return 0.0

        target_data = np.array(self.data[keys[0]])
        comp_data = np.array(self.data[keys[1]])
        total_len = len(target_data)

        # Compute ratio curve: target / (target + comp)
        ratio = target_data / (target_data + comp_data + 1e-6)

        # Estimate samples per rep
        samples_per_rep = total_len // self.repetitions
        success_count = 0

        for i in range(self.repetitions):
            start = i * samples_per_rep
            end = (i + 1) * samples_per_rep
            rep_ratio = np.mean(ratio[start:end])
            if rep_ratio > 0.75:
                success_count += 1

        return (success_count / self.repetitions) * 100

    def generate_plot(self, save_path='plot.jpg'):
        import matplotlib.pyplot as plt
        import numpy as np
        from scipy.ndimage import gaussian_filter1d

        keys = list(self.data.keys())
        if len(keys) < 2:
            return  # not enough muscles to compare

        # Extract EMG signals
        target_data = np.array(self.data[keys[0]])
        comp_data = np.array(self.data[keys[1]])
        total_len = len(target_data)

        # Build x-axis as continuous rep progression, with clean integer ticks
        if self.repetitions <= 1:
            x = np.linspace(0, 1, total_len)  # 0 to 1 rep for partial sets
        else:
            x = np.linspace(0, self.repetitions, total_len)  # e.g. 0 to 1.5, 2.0, etc.

        # Compute target ratio = target / (target + compensation)
        ratio = target_data / (target_data + comp_data + 1e-6)

        # Optional smoothing
        ratio_smooth = gaussian_filter1d(ratio, sigma=3)

        # Plot setup
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(x, ratio_smooth, color='black', linewidth=1.5)

        # Shading: below curve = target dominant, above curve = compensation dominant
        ax.fill_between(x, 0, ratio_smooth, color='#009E73', alpha=0.4, label='Target (Under curve)')
        ax.fill_between(x, ratio_smooth, 1.0, color='#E69F00', alpha=0.4, label='Compensation (Above curve)')

        # Red threshold line at 0.75
        ax.axhline(y=0.75, color='red', linewidth=2)
        ax.text(x[-1], 0.77, 'Minimum', color='red', fontsize=12, va='bottom', ha='right')

        # Labels and title
        plt.xlabel("Repetition (#)", fontsize=12, weight='bold')
        plt.ylabel("Muscle Ratio\n(Target / [Target + Compensation])", fontsize=12, weight='bold')

        # Axis limits: autoscale based on data
        plt.xlim(0, np.ceil(self.repetitions))
        y_min = max(0, ratio_smooth.min() - 0.05)
        y_max = min(1.05, ratio_smooth.max() + 0.05)
        plt.ylim(y_min, y_max)

        # Set tick marks to integers only
        import matplotlib.ticker as ticker
        ax = plt.gca()
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

        # Top x-axis for elapsed time
        ax2 = ax.twiny()
        ax2.set_xlim(ax.get_xlim())  # sync limits

        rep_ticks = np.arange(0, np.ceil(self.repetitions) + 1)
        time_ticks = rep_ticks * 12 / 60  # convert to minutes
        time_labels = [f"{t:.1f}min" for t in time_ticks]

        ax2.set_xticks(rep_ticks)
        ax2.set_xticklabels(time_labels)
        ax2.set_xlabel("Elapsed Time (min)", fontsize=11, weight='bold')
        ax2.xaxis.set_ticks_position('top')
        ax2.tick_params(axis='x', labelrotation=0, labelsize=10)

        ax.legend()

        fig.subplots_adjust(top=0.78)  # move plot area down to make room
        fig.suptitle("Target vs. Compensation\nEMG Data Overview", fontsize=14, weight='bold', y=0.98)
        plt.savefig(save_path, dpi=300)
        plt.close()

    # Ratio bar with side labels
    def generate_ratio_bar(self, save_path='ratio_bar.jpg'):
        keys = list(self.data.keys())
        if len(keys) < 2:
            return  # not enough muscles to compare

        t, c = keys[0], keys[1]
        t_mean = np.mean(self.data[t])
        c_mean = np.mean(self.data[c])
        total = t_mean + c_mean if (t_mean + c_mean) != 0 else 1
        t_pct = (t_mean / total) * 100
        c_pct = (c_mean / total) * 100

        fig, ax = plt.subplots(figsize=(8, 1))

        # Center the bars around 0
        ax.barh(0, t_pct, color='#009E73', edgecolor='black', height=0.1, align='center', left=-t_pct)
        ax.barh(0, c_pct, color='#E69F00', edgecolor='black', height=0.1, align='center', left=0)

        # Draw vertical center line
        ax.axvline(x=0, color='black', linewidth=2)

        # Labels placed near ends
        ax.text(-t_pct - 10, 0, f'Target: {t_pct:.0f}%', va='center', ha='right', fontsize=11)
        ax.text(c_pct + 10, 0, f'Compensation: {c_pct:.0f}%', va='center', ha='left', fontsize=11)

        # Clean formatting
        ax.set_xlim(-120, 120)
        ax.set_ylim(-0.5, 0.5)
        ax.set_yticks([])
        ax.set_xticks([])
        ax.set_frame_on(False)
        plt.tight_layout(pad=1.0)
        plt.savefig(save_path, bbox_inches='tight', dpi=200)
        plt.close()

    def export_pdf(self, filename='session_summary.pdf'):
        # Use Desktop path for safe write access
        desktop_path = Path.home() / "Desktop"
        file_path = desktop_path / filename

        # Temp image paths (also on Desktop)
        plot_path = desktop_path / "plot.jpg"
        bar_path = desktop_path / "ratio_bar.jpg"

        print(f"📄 Saving PDF to: {file_path}")
        print(f"🖼 Saving plot image to: {plot_path}")
        print(f"🖼 Saving ratio bar image to: {bar_path}")

        # Generate images
        self.generate_plot(str(plot_path))
        self.generate_ratio_bar(str(bar_path))

        # Build PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        pdf.cell(200, 10, txt="sEMG Training Session Summary", ln=True, align='C')
        pdf.cell(200, 10, txt=f"Biofeedback Watched: {self.biofeedback_response}", ln=True, align='C')
        pdf.ln(10)
        pdf.cell(200, 10, txt=f"Time: {self.duration}", ln=True)
        pdf.cell(200, 10, txt=f"Repetitions: {self.repetitions}", ln=True)
        pdf.ln(5)

        for k, v in self.calculate_avg_ratios().items():
            pdf.cell(200, 10, f"Avg Activation Ratio {k}: {v:.2f}", ln=True)

        success_rate = self.calculate_success_rate()
        pdf.cell(200, 10, txt=f"Repetition Success Rate: {success_rate:.1f}%", ln=True)

        # Add images
        pdf.image(str(bar_path), x=10, y=None, w=180)
        pdf.ln(5)
        pdf.image(str(plot_path), x=10, y=None, w=180)

        # Save PDF
        pdf.output(str(file_path))
        print("✅ PDF export complete.")
