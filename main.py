import gradio as gr
from geographiclib.geodesic import Geodesic
import math

about_text = """
This tool is designed to calculate and compare the deviation from a target destination when a heading deviation is introduced during a journey. The application of this tool can be in various fields, including navigation, geography, aviation, and more. The default values are set to mimic Amelia Earhart's last flight.

### Process
The calculation is performed in several steps:

1. **Input Parameters**: The user enters the initial coordinates of the journey (in the format latitude, longitude), the initial heading (in degrees from North), the distance travelled (in miles), the heading deviation (in degrees), and the number of decimal places to which the output should be rounded.

2. **Conversion of Heading Deviation**: The heading deviation is converted from degrees to radians, which is the standard unit for trigonometric calculations in Python's `math` module.

3. **End Point Calculation**: The geodesic (i.e., the shortest path over the earth's surface) end points are calculated for both the actual and the correct journeys. The actual end point is calculated using the initial heading plus the heading deviation, and the correct end point is calculated using only the initial heading.

4. **Deviation Distance Calculation**: The deviation distance is calculated as the great-circle distance (i.e., the shortest distance over the earth's surface) between the actual and the correct end points. This distance is calculated in miles.

5. **Trigonometric Deviation Calculation**: The trigonometric deviation is calculated using the tangent of the heading deviation and the distance travelled.

6. **Deviation Difference Calculation**: The difference in deviations is calculated as the absolute difference between the great-circle deviation and the trigonometric deviation.

All calculated values are then rounded to the specified number of decimal places.

### Units
* Initial Coordinates: Latitude and longitude in decimal degrees.
* Initial Heading: Degrees from North, ranging from 0 to 360.
* Distance Travelled: Miles.
* Heading Deviation: Degrees, ranging from -180 to 180. Positive values indicate a clockwise deviation, and negative values indicate a counterclockwise deviation.
* Decimal Places: The number of decimal places to round the output to.

Please note that due to the spherical nature of the Earth, the trigonometric calculation might not always give the exact deviation especially for longer distances. The great circle distance is a more accurate measure of the deviation.
"""

def calculate_deviation(initial_coordinates: str, initial_heading: float, distance: float, heading_deviation: float,
                        decimal_places: int):
    # Convert heading deviations to radians
    heading_deviation_rad = math.radians(heading_deviation)

    starting_lat, starting_lon = map(float, initial_coordinates.split(','))

    # Create a Geodesic object
    geo = Geodesic.WGS84

    # Calculate the actual and the correct end points
    actual_end_point = geo.Direct(starting_lat, starting_lon, initial_heading + heading_deviation, distance * 1609.34)  # Convert miles to meters
    correct_end_point = geo.Direct(starting_lat, starting_lon, initial_heading, distance * 1609.34)  # Convert miles to meters

    # Calculate the deviation distance
    deviation_distance = geo.Inverse(actual_end_point['lat2'], actual_end_point['lon2'],
                                     correct_end_point['lat2'], correct_end_point['lon2'])['s12'] / 1609.34  # Convert meters to miles

    # Trigonometric calculation
    trig_deviation_distance = abs(distance * math.tan(heading_deviation_rad))

    # Calculate the difference in deviations
    deviation_difference = abs(deviation_distance - trig_deviation_distance)

    # Round to significant figures
    deviation_distance = round(deviation_distance, decimal_places)
    trig_deviation_distance = round(trig_deviation_distance, decimal_places)
    deviation_difference = round(deviation_difference, decimal_places)

    # Prepare Google Maps links
    starting_link = f"https://www.google.com/maps/?q={starting_lat},{starting_lon}"
    actual_end_link = f"https://www.google.com/maps/?q={actual_end_point['lat2']},{actual_end_point['lon2']}"
    correct_end_link = f"https://www.google.com/maps/?q={correct_end_point['lat2']},{correct_end_point['lon2']}"

    links = f"Starting Point: [Link]({starting_link})\n"
    links += f"Planned Ending Point: [Link]({correct_end_link})\n"
    links += f"Actual Ending Point: [Link]({actual_end_link})"

    return deviation_distance, trig_deviation_distance, deviation_difference, links


with gr.Interface(fn=calculate_deviation,
                  inputs=[gr.Textbox(value="-6.728, 146.994", label="Initial Coordinates (lat, long)"),
                          gr.Slider(0, 360, value=78, label="Initial Heading (degrees from North)"),
                          gr.Slider(0, 10000, value=2556, label="Distance Travelled (miles)"),
                          gr.Slider(-180, 180, value=1, label="Heading Deviation (degrees)"),
                          gr.Slider(1, 10, value=2, step=1, label="Decimal Places")],
                  outputs=[gr.Textbox(label="Deviation from Target Destination (Geographic Library)"),
                           gr.Textbox(label="Deviation from Target Destination (Trigonometric)"),
                           gr.Textbox(label="Difference in Deviations"),
                           gr.Markdown(label="Location Links")],  # New Markdown component
                  title="Deviation Calculator",
                  allow_flagging="never") as iface:
    with gr.Accordion("About this Tool"):
        gr.Markdown(about_text)

    iface.launch()
