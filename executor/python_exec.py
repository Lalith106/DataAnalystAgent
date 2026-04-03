import pandas as pd
import numpy as np
from data.dataset_store import get_df

import re
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO


def _format_value(value):
    try:
        if isinstance(value, (int, float, np.integer, np.floating)):
            return f"{float(value):.2f}" if float(value) % 1 else str(int(float(value)))
    except Exception:
        pass
    return str(value)


def _apply_visual_theme(fig):
    """Apply a clean, high-contrast presentation theme to generated figures."""
    fig.patch.set_facecolor("#ffffff")

    for ax in fig.get_axes():
        ax.set_facecolor("#f8fafc")
        ax.grid(True, linestyle="--", linewidth=0.6, alpha=0.22, color="#94a3b8")

        title = ax.get_title()
        if title:
            ax.set_title(title, color="#0f172a", fontsize=max(ax.title.get_fontsize(), 13), fontweight="bold")

        if ax.get_xlabel():
            ax.set_xlabel(ax.get_xlabel(), color="#334155", fontsize=11)
        if ax.get_ylabel():
            ax.set_ylabel(ax.get_ylabel(), color="#334155", fontsize=11)

        ax.tick_params(axis="both", colors="#475569", labelsize=9)

        for spine in ax.spines.values():
            spine.set_color("#cbd5e1")

        for text in list(ax.texts):
            try:
                text.set_color("#0f172a")
            except Exception:
                pass

        legend = ax.get_legend()
        if legend:
            frame = legend.get_frame()
            frame.set_facecolor("#ffffff")
            frame.set_edgecolor("#cbd5e1")
            for text in legend.get_texts():
                text.set_color("#0f172a")


def _summarize_axes(ax) -> str:
    title = ax.get_title().strip() or "Visualization"
    xlabel = ax.get_xlabel().strip()
    ylabel = ax.get_ylabel().strip()

    # Bar / histogram-like plots
    bars = [patch for patch in ax.patches if hasattr(patch, "get_height")]
    if bars:
        widths = [getattr(p, "get_width", lambda: 0)() for p in bars]
        heights = [getattr(p, "get_height", lambda: 0)() for p in bars]
        horizontal = sum(widths) > sum(heights)

        labels = [t.get_text().strip() for t in (ax.get_yticklabels() if horizontal else ax.get_xticklabels()) if t.get_text().strip()]
        if not labels:
            labels = [t.get_text().strip() for t in (ax.get_xticklabels() if horizontal else ax.get_yticklabels()) if t.get_text().strip()]

        values = widths if horizontal else heights
        if not any(values):
            values = heights if horizontal else widths

        paired = []
        for i, value in enumerate(values):
            label = labels[i] if i < len(labels) else f"Item {i + 1}"
            paired.append((label, value))

        paired = [(lbl, val) for lbl, val in paired if val is not None]
        if paired:
            top_label, top_value = max(paired, key=lambda x: x[1])
            low_label, low_value = min(paired, key=lambda x: x[1])
            sample = ", ".join(f"{lbl}: {_format_value(val)}" for lbl, val in paired[:5])
            axis_context = (
                f"{ylabel or 'category'} by {xlabel or 'value'}"
                if horizontal
                else f"{xlabel or 'category'} by {ylabel or 'value'}"
            )
            return (
                f"{title}. This chart compares {axis_context}. "
                f"Key values: {sample}. "
                f"Highest is {top_label} ({_format_value(top_value)}); "
                f"lowest is {low_label} ({_format_value(low_value)})."
            )

    # Line plots
    if ax.lines:
        line = ax.lines[0]
        xdata = list(line.get_xdata())
        ydata = list(line.get_ydata())
        if xdata and ydata:
            first_x, first_y = xdata[0], ydata[0]
            last_x, last_y = xdata[-1], ydata[-1]
            direction = "increases" if last_y > first_y else "decreases" if last_y < first_y else "stays roughly stable"
            return (
                f"{title}. The line starts at {_format_value(first_y)} and ends at {_format_value(last_y)}; "
                f"overall it {direction} across the x-axis values from {_format_value(first_x)} to {_format_value(last_x)}."
            )

    # Heatmaps / image-like plots
    if ax.images:
        return f"{title}. The heatmap-like visualization shows a pattern across the plotted categories."

    # Scatter / bubble-like plots
    if ax.collections:
        try:
            offsets = ax.collections[0].get_offsets()
            if len(offsets):
                xs = [pt[0] for pt in offsets]
                ys = [pt[1] for pt in offsets]
                return (
                    f"{title}. The scatter plot shows {len(offsets)} points spanning "
                    f"x values from {_format_value(min(xs))} to {_format_value(max(xs))} and "
                    f"y values from {_format_value(min(ys))} to {_format_value(max(ys))}."
                )
        except Exception:
            pass

    return f"{title}. X-axis: {xlabel or 'not labeled'}; Y-axis: {ylabel or 'not labeled'}."


def build_visualization_summary(fig) -> str:
    axes = fig.get_axes()
    if not axes:
        return "A visualization was generated, but no chart details could be extracted."

    parts = [_summarize_axes(ax) for ax in axes]
    if len(parts) == 1:
        return parts[0]

    return " | ".join(parts)

def clean_code(code: str):
    # Remove markdown blocks
    code = re.sub(r"```python", "", code)
    code = re.sub(r"```", "", code)

    return code.strip()

def execute_python(code: str, is_visualization: bool = False) -> dict:
    """
    Execute Python code and capture results or visualizations
    Returns: dict with 'type' (text/visualization), 'content' (result/image), and 'plot_object' (matplotlib figure if viz)
    """
    # Get the dataset from the store
    df = get_df()
    
    # Create a local namespace for code execution
    local_namespace = {
        'pd': pd, 
        'np': np, 
        'df': df,
        'plt': plt,
        'sns': sns
    }
    
    code = clean_code(code)
    print("------------------code to execute------------------")
    print(code)
    print("---------------------------------------------")
    
    try:
        # Execute the code in the local namespace
        exec(code, {}, local_namespace)
        
        if is_visualization:
            # Get current figure
            fig = plt.gcf()
            
            # Check if figure has content (axes with data)
            if len(fig.get_axes()) > 0:
                try:
                    # Force figure draw to ensure all elements are rendered
                    fig.canvas.draw()

                    _apply_visual_theme(fig)

                    viz_summary = build_visualization_summary(fig)
                    
                    # Convert figure to base64 PNG
                    buffer = BytesIO()
                    fig.savefig(buffer, format='png', dpi=180, bbox_inches='tight', facecolor='white')
                    buffer.seek(0)
                    image_base64 = base64.b64encode(buffer.read()).decode()
                    buffer.close()
                    
                    # Close the figure to free memory
                    plt.close(fig)
                    plt.close('all')
                    
                    return {
                        'type': 'visualization',
                        'content': image_base64,
                        'summary': viz_summary,
                        'plot_object': None,
                        'message': 'Visualization generated successfully'
                    }
                except Exception as e:
                    plt.close('all')
                    return {
                        'type': 'error',
                        'content': f"Error saving figure: {str(e)}",
                        'plot_object': None
                    }
            else:
                plt.close('all')
                return {
                    'type': 'text',
                    'content': 'Code executed but no plot was generated',
                    'plot_object': None
                }
        else:
            # Capture the result if it's stored in a variable named 'result'
            result = local_namespace.get('result', 'Code executed successfully. No result variable found.')
            return {
                'type': 'text',
                'content': str(result),
                'plot_object': None
            }
    
    except Exception as e:
        plt.close('all')
        return {
            'type': 'error',
            'content': f"Error executing code: {str(e)}",
            'plot_object': None
        }
