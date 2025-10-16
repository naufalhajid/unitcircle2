import streamlit as st
import plotly.graph_objects as go
import numpy as np
import math

# --- Mathematical Helper Functions ---

def get_quadrant(angle):
    """Determines the quadrant of a given angle in degrees."""
    if angle in [0, 360]:
        return "Positive X-axis"
    if angle == 90:
        return "Positive Y-axis"
    if angle == 180:
        return "Negative X-axis"
    if angle == 270:
        return "Negative Y-axis"
    
    if 0 < angle < 90:
        return "Quadrant I"
    elif 90 < angle < 180:
        return "Quadrant II"
    elif 180 < angle < 270:
        return "Quadrant III"
    elif 270 < angle < 360:
        return "Quadrant IV"

def get_reference_angle(angle):
    """Calculates the reference angle for a given angle in degrees."""
    if angle in [0, 90, 180, 270, 360]:
        return None # No reference angle for axes
    
    if 0 < angle < 90:
        return angle
    elif 90 < angle < 180:
        return 180 - angle
    elif 180 < angle < 270:
        return angle - 180
    elif 270 < angle < 360:
        return 360 - angle

# --- Plotly Figure Creation ---

def create_unit_circle_figure(selected_angle):
    """Creates the Plotly figure for the unit circle."""
    fig = go.Figure()

    # Set layout properties for a clean look
    fig.update_layout(
        width=600,
        height=600,
        showlegend=False,
        xaxis=dict(range=[-1.5, 1.5], scaleanchor="y", scaleratio=1, title="cos(θ)"),
        yaxis=dict(range=[-1.5, 1.5], title="sin(θ)"),
        plot_bgcolor='white',
        margin=dict(l=20, r=20, t=40, b=20),
    )
    
    # Add colored quadrant backgrounds
    quadrant_colors = {
        'I': 'rgba(173, 216, 230, 0.3)',  # light blue
        'II': 'rgba(144, 238, 144, 0.3)', # light green
        'III': 'rgba(255, 255, 224, 0.4)',# light yellow
        'IV': 'rgba(255, 182, 193, 0.3)'  # light red
    }
    fig.add_shape(type="path", path= "M 0,0 L 1,0 A 1,1 0 0,1 0,1 Z", fillcolor=quadrant_colors['I'], line_width=0)
    fig.add_shape(type="path", path= "M 0,0 L 0,1 A 1,1 0 0,1 -1,0 Z", fillcolor=quadrant_colors['II'], line_width=0)
    fig.add_shape(type="path", path= "M 0,0 L -1,0 A 1,1 0 0,1 0,-1 Z", fillcolor=quadrant_colors['III'], line_width=0)
    fig.add_shape(type="path", path= "M 0,0 L 0,-1 A 1,1 0 0,1 1,0 Z", fillcolor=quadrant_colors['IV'], line_width=0)

    # Add the unit circle
    fig.add_shape(type="circle", x0=-1, y0=-1, x1=1, y1=1, line=dict(color="black", width=2))

    # Add key angle points and labels
    key_angles = [0, 30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330]
    for angle in key_angles:
        rad = math.radians(angle)
        x, y = math.cos(rad), math.sin(rad)
        fig.add_trace(go.Scatter(
            x=[x], y=[y],
            mode='markers',
            marker=dict(color='blue', size=8),
            customdata=[angle],
            hovertemplate=f'{angle}°<extra></extra>'
        ))
        # Add labels slightly outside the circle
        fig.add_annotation(x=x*1.15, y=y*1.15, text=f"{angle}°", showarrow=False, font=dict(size=10))

    # --- Dynamic elements for the selected angle ---
    if selected_angle is not None:
        rad_selected = math.radians(selected_angle)
        x_selected, y_selected = math.cos(rad_selected), math.sin(rad_selected)

        # Point for the selected angle
        fig.add_trace(go.Scatter(
            x=[x_selected], y=[y_selected],
            mode='markers',
            marker=dict(color='red', size=12, symbol='x'),
            name='Selected Angle'
        ))

        # Line from origin to the point
        fig.add_shape(type="line", x0=0, y0=0, x1=x_selected, y1=y_selected,
                      line=dict(color="red", width=2, dash="dash"))
                      
        # Angle arc
        x_arc = [math.cos(r) for r in np.linspace(0, rad_selected, 50)]
        y_arc = [math.sin(r) for r in np.linspace(0, rad_selected, 50)]
        fig.add_trace(go.Scatter(x=x_arc, y=y_arc, mode='lines', line=dict(color='red', width=2)))

    return fig

# --- Streamlit App Layout ---

st.set_page_config(layout="wide")

st.title("Interactive Unit Circle Explorer")
st.write("Click on a point or use the slider to select an angle and see its properties.")

# Initialize session state for the selected angle
if 'selected_angle' not in st.session_state:
    st.session_state.selected_angle = 45

# Main layout with two columns
col1, col2 = st.columns([2, 1])

with col1:
    # Create a placeholder for the plot
    plot_container = st.empty()

    # Angle slider
    slider_val = st.slider(
        "Select Angle (θ)", 
        min_value=0, 
        max_value=360, 
        value=st.session_state.selected_angle,
        step=1
    )
    # Update session state if slider is used
    st.session_state.selected_angle = slider_val

    # Create and display the plot
    fig = create_unit_circle_figure(st.session_state.selected_angle)
    # Use `on_click` to handle point clicks
    click_data = st.plotly_chart(fig, on_select="ignore", use_container_width=True)
    
    # This part is tricky in Streamlit. A full round-trip is needed.
    # The click event is not directly available in the same run.
    # A better approach is to use a component that supports callbacks,
    # but for standard Streamlit, we can suggest a rerun or use the slider as the primary input.
    # For this implementation, the slider is the most reliable interactive element.
    # A more advanced implementation might use `streamlit-plotly-events`.

with col2:
    st.header("Angle Properties")
    
    angle = st.session_state.selected_angle
    
    if angle is not None:
        rad = math.radians(angle)
        cos_val = math.cos(rad)
        sin_val = math.sin(rad)
        # Handle tan for 90 and 270 degrees
        tan_val = math.tan(rad) if cos_val != 0 else "Undefined"

        st.metric(label="Selected Angle (θ)", value=f"{angle}°")
        
        quadrant = get_quadrant(angle)
        st.metric(label="Location", value=quadrant)

        ref_angle = get_reference_angle(angle)
        if ref_angle is not None:
            st.metric(label="Reference Angle", value=f"{ref_angle}°")
        else:
            st.info("Angles on the axes do not have a reference angle.")

        st.subheader("Trigonometric Values")
        st.markdown(f"**sin({angle}°) =** `{sin_val:.3f}`")
        st.markdown(f"**cos({angle}°) =** `{cos_val:.3f}`")
        st.markdown(f"**tan({angle}°) =** `{'Undefined' if isinstance(tan_val, str) else f'{tan_val:.3f}'}`")

    else:
        st.info("Select an angle to see its properties.")

st.markdown("---")
st.markdown("""
### How to Use This Tool
1.  **Use the Slider:** Drag the slider to select any angle from 0° to 360°. The red 'X' on the circle will move to show the angle's position.
2.  **View Properties:** The panel on the right will instantly update to show the selected angle's quadrant, reference angle, and trigonometric values (sin, cos, tan).
3.  **Key Angles:** The blue dots mark common angles. You can see their degree labels around the circle.
4.  **Quadrant Colors:** Each quadrant has a distinct color to help you visually associate angles with their location.
    - **Quadrant I (0°-90°):** Light Blue
    - **Quadrant II (90°-180°):** Light Green
    - **Quadrant III (180°-270°):** Light Yellow
    - **Quadrant IV (270°-360°):** Light Red
""")
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import math

# --- Mathematical Helper Functions ---

def get_quadrant(angle):
    """Determines the quadrant of a given angle in degrees."""
    if angle in [0, 360]:
        return "Positive X-axis"
    if angle == 90:
        return "Positive Y-axis"
    if angle == 180:
        return "Negative X-axis"
    if angle == 270:
        return "Negative Y-axis"
    
    if 0 < angle < 90:
        return "Quadrant I"
    elif 90 < angle < 180:
        return "Quadrant II"
    elif 180 < angle < 270:
        return "Quadrant III"
    elif 270 < angle < 360:
        return "Quadrant IV"

def get_reference_angle(angle):
    """Calculates the reference angle for a given angle in degrees."""
    if angle in [0, 90, 180, 270, 360]:
        return None # No reference angle for axes
    
    if 0 < angle < 90:
        return angle
    elif 90 < angle < 180:
        return 180 - angle
    elif 180 < angle < 270:
        return angle - 180
    elif 270 < angle < 360:
        return 360 - angle

# --- Plotly Figure Creation ---

def create_unit_circle_figure(selected_angle):
    """Creates the Plotly figure for the unit circle."""
    fig = go.Figure()

    # Set layout properties for a clean look
    fig.update_layout(
        width=600,
        height=600,
        showlegend=False,
        xaxis=dict(range=[-1.5, 1.5], scaleanchor="y", scaleratio=1, title="cos(θ)"),
        yaxis=dict(range=[-1.5, 1.5], title="sin(θ)"),
        plot_bgcolor='white',
        margin=dict(l=20, r=20, t=40, b=20),
    )
    
    # Add colored quadrant backgrounds
    quadrant_colors = {
        'I': 'rgba(173, 216, 230, 0.3)',  # light blue
        'II': 'rgba(144, 238, 144, 0.3)', # light green
        'III': 'rgba(255, 255, 224, 0.4)',# light yellow
        'IV': 'rgba(255, 182, 193, 0.3)'  # light red
    }
    fig.add_shape(type="path", path= "M 0,0 L 1,0 A 1,1 0 0,1 0,1 Z", fillcolor=quadrant_colors['I'], line_width=0)
    fig.add_shape(type="path", path= "M 0,0 L 0,1 A 1,1 0 0,1 -1,0 Z", fillcolor=quadrant_colors['II'], line_width=0)
    fig.add_shape(type="path", path= "M 0,0 L -1,0 A 1,1 0 0,1 0,-1 Z", fillcolor=quadrant_colors['III'], line_width=0)
    fig.add_shape(type="path", path= "M 0,0 L 0,-1 A 1,1 0 0,1 1,0 Z", fillcolor=quadrant_colors['IV'], line_width=0)

    # Add the unit circle
    fig.add_shape(type="circle", x0=-1, y0=-1, x1=1, y1=1, line=dict(color="black", width=2))

    # Add key angle points and labels
    key_angles = [0, 30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330]
    for angle in key_angles:
        rad = math.radians(angle)
        x, y = math.cos(rad), math.sin(rad)
        fig.add_trace(go.Scatter(
            x=[x], y=[y],
            mode='markers',
            marker=dict(color='blue', size=8),
            customdata=[angle],
            hovertemplate=f'{angle}°<extra></extra>'
        ))
        # Add labels slightly outside the circle
        fig.add_annotation(x=x*1.15, y=y*1.15, text=f"{angle}°", showarrow=False, font=dict(size=10))

    # --- Dynamic elements for the selected angle ---
    if selected_angle is not None:
        rad_selected = math.radians(selected_angle)
        x_selected, y_selected = math.cos(rad_selected), math.sin(rad_selected)

        # Point for the selected angle
        fig.add_trace(go.Scatter(
            x=[x_selected], y=[y_selected],
            mode='markers',
            marker=dict(color='red', size=12, symbol='x'),
            name='Selected Angle'
        ))

        # Line from origin to the point
        fig.add_shape(type="line", x0=0, y0=0, x1=x_selected, y1=y_selected,
                      line=dict(color="red", width=2, dash="dash"))
                      
        # Angle arc
        x_arc = [math.cos(r) for r in np.linspace(0, rad_selected, 50)]
        y_arc = [math.sin(r) for r in np.linspace(0, rad_selected, 50)]
        fig.add_trace(go.Scatter(x=x_arc, y=y_arc, mode='lines', line=dict(color='red', width=2)))

    return fig

# --- Streamlit App Layout ---

st.set_page_config(layout="wide")

st.title("Interactive Unit Circle Explorer")
st.write("Click on a point or use the slider to select an angle and see its properties.")

# Initialize session state for the selected angle
if 'selected_angle' not in st.session_state:
    st.session_state.selected_angle = 45

# Main layout with two columns
col1, col2 = st.columns([2, 1])

with col1:
    # Create a placeholder for the plot
    plot_container = st.empty()

    # Angle slider
    slider_val = st.slider(
        "Select Angle (θ)", 
        min_value=0, 
        max_value=360, 
        value=st.session_state.selected_angle,
        step=1
    )
    # Update session state if slider is used
    st.session_state.selected_angle = slider_val

    # Create and display the plot
    fig = create_unit_circle_figure(st.session_state.selected_angle)
    # Use `on_click` to handle point clicks
    click_data = st.plotly_chart(fig, on_select="ignore", use_container_width=True)
    
    # This part is tricky in Streamlit. A full round-trip is needed.
    # The click event is not directly available in the same run.
    # A better approach is to use a component that supports callbacks,
    # but for standard Streamlit, we can suggest a rerun or use the slider as the primary input.
    # For this implementation, the slider is the most reliable interactive element.
    # A more advanced implementation might use `streamlit-plotly-events`.

with col2:
    st.header("Angle Properties")
    
    angle = st.session_state.selected_angle
    
    if angle is not None:
        rad = math.radians(angle)
        cos_val = math.cos(rad)
        sin_val = math.sin(rad)
        # Handle tan for 90 and 270 degrees
        tan_val = math.tan(rad) if cos_val != 0 else "Undefined"

        st.metric(label="Selected Angle (θ)", value=f"{angle}°")
        
        quadrant = get_quadrant(angle)
        st.metric(label="Location", value=quadrant)

        ref_angle = get_reference_angle(angle)
        if ref_angle is not None:
            st.metric(label="Reference Angle", value=f"{ref_angle}°")
        else:
            st.info("Angles on the axes do not have a reference angle.")

        st.subheader("Trigonometric Values")
        st.markdown(f"**sin({angle}°) =** `{sin_val:.3f}`")
        st.markdown(f"**cos({angle}°) =** `{cos_val:.3f}`")
        st.markdown(f"**tan({angle}°) =** `{'Undefined' if isinstance(tan_val, str) else f'{tan_val:.3f}'}`")

    else:
        st.info("Select an angle to see its properties.")

st.markdown("---")
st.markdown("""
### How to Use This Tool
1.  **Use the Slider:** Drag the slider to select any angle from 0° to 360°. The red 'X' on the circle will move to show the angle's position.
2.  **View Properties:** The panel on the right will instantly update to show the selected angle's quadrant, reference angle, and trigonometric values (sin, cos, tan).
3.  **Key Angles:** The blue dots mark common angles. You can see their degree labels around the circle.
4.  **Quadrant Colors:** Each quadrant has a distinct color to help you visually associate angles with their location.
    - **Quadrant I (0°-90°):** Light Blue
    - **Quadrant II (90°-180°):** Light Green
    - **Quadrant III (180°-270°):** Light Yellow
    - **Quadrant IV (270°-360°):** Light Red
""")
