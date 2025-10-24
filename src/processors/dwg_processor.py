import ezdxf
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
import matplotlib.pyplot as plt
import os

def process(file_path: str, output_folder: str) -> str | None:
    """
    Converts a .dwg file to a .png image.
    
    Args:
        file_path: The absolute path to the .dwg file.
        output_folder: The folder to save the output .png image.

    Returns:
        The path to the generated .png file, or None if conversion fails.
    """
    try:
        print(f"Processing DWG file: {file_path}")
        doc = ezdxf.readfile(file_path)
        msp = doc.modelspace()
        
        # Create the output folder if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Prepare output path
        filename = os.path.basename(file_path)
        output_filename = os.path.splitext(filename)[0] + ".png"
        output_path = os.path.join(output_folder, output_filename)

        # Render the DWG to a PNG
        fig = plt.figure()
        ax = fig.add_axes([0, 0, 1, 1])
        ctx = RenderContext(doc)
        out = MatplotlibBackend(ax)
        Frontend(ctx, out).draw_layout(msp, finalize=True)

        fig.savefig(output_path, dpi=300)
        plt.close(fig)
        
        print(f"Successfully converted {file_path} to {output_path}")
        return output_path

    except IOError:
        print(f"Could not open DWG file: {file_path}. It might be a version not supported by ezdxf.")
        return None
    except Exception as e:
        print(f"An error occurred while processing DWG file {file_path}: {e}")
        return None
