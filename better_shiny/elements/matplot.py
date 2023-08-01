import base64
import io

from dominate.tags import html_tag, img
from matplotlib import pyplot


def _plt_to_data_uri(plt: pyplot, dpi: int) -> str:
    """
    Convert the given matplotlib figure into a base64-encoded PNG image data URI.
    :param plt: The matplotlib figure to convert.
    :return: The base64-encoded PNG image data URI.
    """
    # Create a buffer to hold the PNG image data
    buf = io.BytesIO()

    # Render the figure onto the canvas, use as little space as possible
    plt.savefig(buf, format='png', dpi=dpi, bbox_inches='tight')
    plt.close()

    # Get the PNG image data from the buffer
    buf.seek(0)
    png_data = buf.getvalue()

    # Encode the PNG image data into base64
    encoded_png_data = base64.b64encode(png_data).decode('utf-8')

    # Build the data URI with the base64-encoded PNG data
    data_uri = f"data:image/png;base64,{encoded_png_data}"

    return data_uri


def matplot(
        plt: pyplot, dpi: int = None,
) -> img:
    """
    Convert the given matplotlib figure into a DOM element.
    :param plt: The matplotlib figure to convert.
    :return: The DOM element containing the figure.
    """

    plt_data_uri = _plt_to_data_uri(plt, dpi)

    return img(
        src=plt_data_uri,
    )
