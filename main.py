import gradio as gr
from geographiclib.geodesic import Geodesic
import math

METERS_TO_MILES = 1609.34

about_text = """
## About the Deviation Finder App

The Deviation Finder App is designed mainly for aviation purposes, to assist in calculating the deviation from a target destination based on input parameters such as initial coordinates, initial heading, distance travelled, and heading deviation. The app uses two methods for calculating the deviation: the Geographic Library method and a simple trigonometric method. It highlights the differences between the two methods and provides Google Maps links for the starting point, planned ending point, and actual ending point.

### Geographic Library Method

The Geographic Library method employs the Inverse and Direct functions from the Geographic Library, which work with the Earth's ellipsoidal shape to provide accurate results even for long distances. The Inverse function calculates the geodesic (shortest) distance between two points on the Earth's surface by implementing a highly accurate algorithm called the Karney Inverse solution. This iterative method converges quickly to find the shortest distance and angles between two points, taking into account factors such as the Earth's semi-major and semi-minor axes and the flattening factor.

The Direct function solves the direct geodesic problem, computing the destination point given a starting point, an initial azimuth (direction), and distance travelled along the Earth's surface. This function can be useful in navigation systems, surveying, and mapping applications.

### Trigonometric Method

The trigonometric method calculates the deviation using a simple mathematical equation based on the tangent function. This method is less accurate than the Geographic Library method, as it does not consider the Earth's ellipsoidal shape and curvature.

### Input Parameters

- Initial Coordinates (lat, long): The starting point of the journey, provided in latitude and longitude decimal format (e.g., 40.7128, -74.0060).
- Initial Heading (degrees from North): The direction of travel at the start of the journey, expressed in degrees from true North (0° to 360°).
- Distance Travelled (miles): The total distance travelled, in miles.
- Heading Deviation (degrees): The deviation from the initial heading, in degrees. Positive values represent a deviation to the right, while negative values represent a deviation to the left.
- Decimal Places: The number of significant decimal places to round the results.

### Output Parameters

- Deviation from Target Destination (Geographic Library): The calculated deviation from the target destination using the Geographic Library method, in miles.
- Deviation from Target Destination (Trigonometric): The calculated deviation from the target destination using the trigonometric method, in miles.
- Difference in Deviations: The difference in deviation calculations between the Geographic Library and trigonometric methods, in miles.
- Location Links: Google Maps links for the starting point, planned ending point, and actual ending point.

The app's sample inputs are taken from Amelia Earhart's final planned flight, illustrating the significance of accurate deviation calculations in aviation.
"""


def calculate_deviation(initial_coordinates: str, initial_heading: float, distance: float, heading_deviation: float,
                        decimal_places: int):
    # Convert heading deviations to radians
    heading_deviation_rad = math.radians(heading_deviation)

    starting_lat, starting_lon = map(float, initial_coordinates.split(','))

    # Create a Geodesic object
    geo: Geodesic = Geodesic.WGS84

    # Calculate the actual and the correct end points
    actual_end_point = geo.Direct(starting_lat, starting_lon, initial_heading + heading_deviation, distance * METERS_TO_MILES)  # Convert miles to meters
    correct_end_point = geo.Direct(starting_lat, starting_lon, initial_heading, distance * METERS_TO_MILES)  # Convert miles to meters

    # Calculate the deviation distance
    deviation_distance = geo.Inverse(actual_end_point['lat2'], actual_end_point['lon2'],
                                     correct_end_point['lat2'], correct_end_point['lon2'])['s12'] / METERS_TO_MILES  # Convert meters to miles

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

    links = f"Starting Point: [Link]({starting_link})\n\n"
    links += f"Planned Ending Point: [Link]({correct_end_link})\n\n"
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
