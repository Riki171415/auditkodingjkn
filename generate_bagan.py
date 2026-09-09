import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

def create_flowchart():
    os.makedirs('assets', exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 4))
    
    # Hide axes
    ax.axis('off')
    
    steps = [
        "1. Ekstraksi\nData Klaim",
        "2. Penerapan\nAturan KNAVP",
        "3. Analisis\nReviewer",
        "4. Dokumentasi\n(KKR-DR01)",
        "5. Penyusunan\nRekomendasi"
    ]
    
    # Draw boxes
    for i, step in enumerate(steps):
        # Create a rectangle patch
        rect = mpatches.FancyBboxPatch((i*2, 0.5), 1.5, 0.8, 
                                       boxstyle="round,pad=0.1", 
                                       ec="black", fc="#4f81bd", lw=1.5)
        ax.add_patch(rect)
        
        # Add text
        ax.text(i*2 + 0.75, 0.9, step, ha='center', va='center', 
                color='white', fontsize=10, fontweight='bold')
        
        # Draw arrows
        if i < len(steps) - 1:
            ax.annotate('', xy=((i+1)*2, 0.9), xytext=(i*2 + 1.5, 0.9),
                        arrowprops=dict(facecolor='black', edgecolor='black', arrowstyle="->", lw=1.5))
            
    plt.xlim(-0.5, len(steps)*2)
    plt.ylim(0, 2)
    
    output_path = os.path.join('assets', 'bagan_metode.png')
    plt.savefig(output_path, bbox_inches='tight', dpi=300, transparent=True)
    print(f"Chart saved to {output_path}")

if __name__ == '__main__':
    create_flowchart()
