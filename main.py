import gradio as gr
from geopy.point import Point
from geopy.distance import geodesic, great_circle
import math

about_text = "This tool calculates the deviation from the target destination given a variation in the heading of an " \
             "airplane on a straight course, using both the Great Circle method and a simple trigonometric method.\n" +\
             "Enter the initial coordinates as latitude, longitude (in decimal degrees). Adjust the sliders to set " \
             "the initial " \
             "heading (degrees from North), the distance travelled and the initial heading deviation. Set the number " \
             "of significant figures to be shown in the results.\n" + \
             "The tool calculates the end point using the entered heading deviation and the 'correct' end point (with "\
             "no heading " \
             "deviation). The deviation is the difference between these two end points. The Great Circle method takes "\
             "into account the curvature of the Earth, while the trigonometric method assumes a flat Earth. "


def calculate_deviation(initial_coordinates: str, initial_heading: float, distance: float, heading_deviation: float,
                        decimal_places: int):
    # Convert heading deviations to radians
    heading_deviation_rad = math.radians(heading_deviation)

    starting_point = Point(*list(map(float, initial_coordinates.split(','))))

    # Calculate the actual and the correct end points
    actual_end_point = geodesic(miles=distance).destination(starting_point, initial_heading + heading_deviation)
    correct_end_point = geodesic(miles=distance).destination(starting_point, initial_heading)

    # Calculate the deviation distance
    deviation_distance = great_circle(actual_end_point, correct_end_point).miles

    # Trigonometric calculation
    trig_deviation_distance = abs(distance * math.tan(heading_deviation_rad))

    # Calculate the difference in deviations
    deviation_difference = abs(deviation_distance - trig_deviation_distance)

    # Round to significant figures
    deviation_distance = round(deviation_distance, decimal_places)
    trig_deviation_distance = round(trig_deviation_distance, decimal_places)
    deviation_difference = round(deviation_difference, decimal_places)

    return deviation_distance, trig_deviation_distance, deviation_difference


with gr.Interface(fn=calculate_deviation,
                  inputs=[gr.Textbox(value="-6.728, 146.994", label="Initial Coordinates (lat, long)"),
                          gr.Slider(0, 360, value=78, label="Initial Heading (degrees from North)"),
                          gr.Slider(0, 10000, value=2556, label="Distance Travelled (miles)"),
                          gr.Slider(-180, 180, value=1, label="Heading Deviation (degrees)"),
                          gr.Slider(1, 10, value=2, step=1, label="Decimal Places")],
                  outputs=[gr.Textbox(label="Deviation from Target Destination (Great Circle)"),
                           gr.Textbox(label="Deviation from Target Destination (Trigonometric)"),
                           gr.Textbox(label="Difference in Deviations")],
                  title="Deviation Calculator") as iface:
    with gr.Accordion("About this Tool"):
        gr.Markdown(about_text)

    iface.launch()
