import plotly.graph_objects as go
import pandas as pd
from .utils import generate_row_labels, normalize_well, pad_or_check


class Plate:
    
    """
    Represents a microplate with configurable layout and visualization.
    Supports arbitrary row labels (A-Z, AA, AB...) and 1+ digit column indices.
    """

    def __init__(self, values=None, colors=None, overlay_text=None, n_rows=8, n_columns=12, fill_direction="horizontal"):
        self.values = values
        self.colors = colors
        self.overlay_text = overlay_text
        self.n_rows = n_rows
        self.n_columns = n_columns
        self.fill_direction = fill_direction


    def plot(self, **kwargs):
        
        """
        Create a Plotly figure representing the plate.
        This method generates a scatter plot with wells represented as markers,
        and optional overlay text for each well.

        Args:
            **kwargs: Additional keyword arguments to pass to the Plotly figure.

        Returns:
            go.Figure: A Plotly figure object representing the plate.
        """

        return self._plate_figure(
            values=self.values,
            colors=self.colors,
            overlay_text=self.overlay_text,
            n_rows=self.n_rows,
            n_columns=self.n_columns,
            fill_direction=self.fill_direction,
            **kwargs
        )


    def to_dict(self): 
        """
        Convert the Plate instance to a dictionary representation.
        The dictionary will contain well names as keys and a dictionary of
        content as values, where the content dictionary can contain keys
        "value", "color", and "text", representing the well's value,
        color, and overlay text respectively.

        Returns:
            dict: A dictionary representation of the Plate instance.
        """

        well_dict = {}
        
        for row in range(self.n_rows):

            row_label = generate_row_labels(self.n_rows)[row]
            
            for col in range(1, self.n_columns + 1):

                well_name = f"{row_label}{col}"
                idx = row * self.n_columns + (col - 1)
                well_dict[well_name] = {}
                
                if self.values is not None:
                    try:
                        well_dict[well_name]["value"] = self.values[idx]
                    except IndexError:
                        pass

                if self.colors is not None:
                    try:
                        well_dict[well_name]["color"] = self.colors[idx]
                    except IndexError:
                        pass

                if self.overlay_text is not None:
                    try:
                        well_dict[well_name]["text"] = self.overlay_text[idx]
                    except IndexError:
                        pass

        return well_dict


    @classmethod
    def from_dict(cls, well_dict, n_rows, n_columns):
       
        """
        Create a Plate instance from a dictionary of well data.
        The dictionary should have well names as keys and a dictionary of
        content as values, where the content dictionary can contain keys
        "value", "color", and "text", representing the well's value,
        color, and overlay text respectively.

        Args:
            well_dict (dict): Dictionary with well names as keys and content dicts as values.
            n_rows (int): Number of rows in the plate.
            n_columns (int): Number of columns in the plate.

        Returns:
            Plate: An instance of the Plate class populated with the provided data.
        """

        values = [None] * (n_rows * n_columns)
        colors = [None] * (n_rows * n_columns)
        text = [None] * (n_rows * n_columns)

        for well, content in well_dict.items():
            row_char, col_num = normalize_well(well)
            row_idx = cls._row_letters_to_index(row_char)
            col_idx = col_num - 1
            if row_idx >= n_rows or col_idx >= n_columns:
                continue
            idx = row_idx * n_columns + col_idx
            values[idx] = content.get("value")
            colors[idx] = content.get("color")
            text[idx] = content.get("text")

        return cls(values, colors, text, n_rows=n_rows, n_columns=n_columns)


    @classmethod
    def from_dataframe(cls, df: pd.DataFrame, well_col="well", value_col="value", color_col="color", text_col="text", n_rows=8, n_columns=12):
        
        """
        Create a Plate instance from a pandas DataFrame.
        The DataFrame should have a column for well names and optional columns
        for values, colors, and overlay text. The well names should be in a format
        that can be normalized (e.g., "A1", "B12", "AA02").

        Args:
            df (pd.DataFrame): DataFrame containing well data.
            well_col (str): Column name for well names.
            value_col (str): Column name for well values.
            color_col (str): Column name for well colors.
            text_col (str): Column name for overlay text.
            n_rows (int): Number of rows in the plate.
            n_columns (int): Number of columns in the plate.

        Returns:
            Plate: An instance of the Plate class populated with the DataFrame data.
        """

        record_dict = {
            row[well_col]: {
                "value": row.get(value_col),
                "color": row.get(color_col),
                "text": row.get(text_col),
            }
            for _, row in df.iterrows()
        }
        return cls.from_dict(record_dict, n_rows=n_rows, n_columns=n_columns)


    @staticmethod
    def _row_letters_to_index(row_letters):
        
        """
        Convert row letters (e.g., "A", "B", "AA") to a zero-based index.
        The conversion is based on a base-26 system where "A" is 0, "B" is 1, ..., "Z" is 25,
        "AA" is 26, "AB" is 27, and so on.
        Args:
            row_letters (str): The row letters to convert.
        Returns:
            int: The zero-based index corresponding to the row letters.
        """

        index = 0
        for char in row_letters:
            index = index * 26 + (ord(char.upper()) - ord('A') + 1)
        return index - 1


    @staticmethod
    def _plate_figure(
        values=None, 
        colors=None, 
        overlay_text=None, 
        n_rows=8, 
        n_columns=12, 
        marker=None, 
        scale=1.0, 
        marker_size=None, 
        showscale=False, 
        text_size=None, 
        text_color="black", 
        fill_direction="horizontal", 
        **kwargs
    ):
        
        """
        Create a Plotly figure representing a microplate with wells.

        Args:
            values (list): List of values for each well.
            colors (list): List of colors for each well.
            overlay_text (list): List of overlay text for each well.
            n_rows (int): Number of rows in the plate.
            n_columns (int): Number of columns in the plate.
            marker (dict, optional): Custom marker settings for the wells.
            scale (float): Scale factor for the figure size.
            marker_size (int, optional): Size of the markers.
            showscale (bool): Whether to show the color scale.
            text_size (int, optional): Size of the overlay text.
            text_color (str): Color of the overlay text.
            fill_direction (str): Direction to fill the wells ("horizontal" or "vertical").
            **kwargs: Additional keyword arguments for the Plotly figure.

        Returns:
            go.Figure: A Plotly figure object representing the plate.

        Raises:
            ValueError: If fill_direction is not "horizontal" or "vertical",
                        or if the length of values, colors, or overlay_text exceeds the number of wells.
        """

        if fill_direction not in ["horizontal", "vertical"]:
            raise ValueError("fill_direction must be 'horizontal' or 'vertical'")

        n_wells = n_rows * n_columns

        values = pad_or_check("values", values, n_wells)
        overlay_text = pad_or_check("overlay_text", overlay_text, n_wells)

        using_custom_colors = colors is not None
        if using_custom_colors:
            colors = pad_or_check("colors", colors, n_wells)
            if all(isinstance(c, (str, type(None))) for c in colors):
                colors = ['rgba(0,0,0,0)' if c is None else c for c in colors]
        else:
            colors = [0 if v is None else v for v in values]

        row_labels = generate_row_labels(n_rows)
        col_labels = list(range(1, n_columns + 1))
        x_offset = 0.4
        label_pad = 0.08 * scale

        x, y, hovertext = [], [], []

        if fill_direction == "horizontal":

            # Iterate by rows first (row-major order)
            for i, row in enumerate(row_labels):
                for j, col in enumerate(col_labels):
                    idx = i * n_columns + j
                    x.append(col + x_offset)
                    y.append(n_rows - i)
                    label = f"{row}{col}"
                    val = values[idx]
                    hovertext.append(f"{label}<br>{val}" if val is not None else label)

        elif fill_direction == "vertical":

            # Iterate by columns first (column-major order)
            for j, col in enumerate(col_labels):
                for i, row in enumerate(row_labels):
                    idx = j * n_rows + i
                    x.append(col + x_offset)
                    y.append(n_rows - i)
                    label = f"{row}{col}"
                    val = values[idx]
                    hovertext.append(f"{label}<br>{val}" if val is not None else label)

        else:
            raise ValueError("fill_direction must be either 'horizontal' or 'vertical'")

        if marker_size is None:
            marker_size = min(45, int(400 / max(n_rows, n_columns)))

        if marker is None:
            marker = dict(size=marker_size, symbol='circle', color=colors, line=dict(color='black', width=1))
            if using_custom_colors:
                marker['showscale'] = False
            else:
                marker['colorscale'] = 'Blues'
                marker['showscale'] = showscale
                if showscale:
                    marker['colorbar'] = dict(title="Value")
        else:
            marker = marker.copy()
            marker.setdefault("size", marker_size)
            marker.setdefault("line", {}).setdefault("width", 1)
            marker.setdefault("color", colors)

        scatter = go.Scatter(
            x=x, y=y, mode='markers', marker=marker, hovertext=hovertext, hoverinfo='text', **kwargs
        )

        font_size = min(14, max(int(160 / max(n_rows, n_columns)), 12))
        annotations = []

        for col in col_labels:
            annotations.append(dict(x=col + x_offset, y=n_rows + 0.4, text=str(col), showarrow=False, font=dict(size=font_size), yanchor='bottom'))
        
        for i, row in enumerate(row_labels):
            annotations.append(dict(x=0.5 + label_pad, y=n_rows - i, text=row, showarrow=False, font=dict(size=font_size), xanchor='left'))

        left_x = 0.5
        right_x = n_columns + x_offset + 0.5
        border_width = 4
        gray_frame_width = 2

        # Border shapes for drawing the plate's frame
        shapes = [
            # Light gray frame around the plate wells
            dict(
                type='rect', 
                x0=0.62 + x_offset, 
                x1=n_columns + x_offset + 0.38,
                y0=0.72, 
                y1=n_rows + 0.38, 
                line=dict(color='darkgray', width=gray_frame_width), 
                layer='below'
            ),

            # Bottom border of the plate
            dict(
                type='line',
                x0=left_x,
                y0=0.5,
                x1=right_x,
                y1=0.5,
                line=dict(color='black', width=border_width),
                layer='below'
            ),

            # Left border of the plate
            dict(
                type='line',
                x0=left_x,
                y0=0.5,
                x1=left_x,
                y1=n_rows + 0.5,
                line=dict(color='black', width=border_width),
                layer='below'
            ),

            # Top-right corner extension (diagonal or stepped effect)
            dict(
                type='line',
                x0=left_x,
                y0=n_rows + 0.5,
                x1=left_x + 0.5,
                y1=n_rows + 1.0,
                line=dict(color='black', width=border_width),
                layer='below'
            ),

            # Extended top border line
            dict(
                type='line',
                x0=left_x + 0.5,
                y0=n_rows + 1.0,
                x1=right_x,
                y1=n_rows + 1.0,
                line=dict(color='black', width=border_width),
                layer='below'
            ),

            # Right border of the plate
            dict(
                type='line',
                x0=right_x,
                y0=0.5,
                x1=right_x,
                y1=n_rows + 1.0,
                line=dict(color='black', width=border_width),
                layer='below'
            ),
        ]

        x_pad, y_pad = 1.0, 1.0
        margin = dict(l=scale * (20 + 5 * n_rows), r=scale * 20, t=scale * 20, b=scale * 20)
        cell_px = 60 * scale
        width = int(cell_px * n_columns + margin["l"] + margin["r"])
        height = int(cell_px * n_rows + margin["t"] + margin["b"])

        layout = dict(
            xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, range=[left_x - x_pad, right_x + x_pad]),
            yaxis=dict(showticklabels=False, showgrid=False, zeroline=False, range=[0.5 - y_pad, n_rows + 1.0 + y_pad]),
            annotations=annotations,
            shapes=shapes,
            plot_bgcolor='white',
            margin=margin,
            width=width,
            height=height,
            showlegend=False,
        )

        fig = go.Figure(data=[scatter], layout=layout)

        if overlay_text is not None:
            if isinstance(overlay_text, str) and overlay_text == "values":
                overlay_text = [str(v) if v is not None else "" for v in values]
            if text_size is None:
                text_size = font_size - 2
            text_trace = go.Scatter(
                x=x,
                y=y,
                mode="text",
                text=overlay_text,
                textposition="middle center",
                textfont=dict(size=text_size, color=text_color),
                hoverinfo='skip',
                showlegend=False
            )
            fig.add_trace(text_trace)

        return fig



