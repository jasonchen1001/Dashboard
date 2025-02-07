# India Delivery Service Analytics Dashboard 🚚

An interactive dashboard built with Panel to analyze delivery service data across major Indian cities. The dashboard provides geographical visualization, order distribution, and detailed statistical analysis.

## Features ✨

- 🗺️ Interactive map showing delivery ratings across cities
- 📊 Order volume distribution pie chart
- 📈 Detailed statistical analysis
- 🔍 Filtering by delivery agent and order type
- 📱 Responsive design for all devices
- 🔔 Real-time update notifications
- 📊 Multi-tab interface for different views

## Requirements 📋

- Anaconda or Miniconda
- Python 3.7+
- Required packages:
  - panel
  - folium
  - plotly
  - pandas
  - bokeh

## Installation 🛠️

1. Clone this repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create and activate a Conda environment:
```bash
conda create -n delivery_dashboard python=3.9
conda activate delivery_dashboard
```

3. Install dependencies:
```bash
conda install -c conda-forge panel folium plotly pandas bokeh
# Or use requirements.txt
pip install -r requirements.txt
```

## Usage 🚀

1. Activate the Conda environment:
```bash
conda activate delivery_dashboard
```

2. Run the dashboard:
```bash
python dashboard.py
```

3. Open your browser and navigate to the displayed local address (typically http://localhost:5006)

## Project Structure 📁

```
.
├── README.md
├── dashboard.py           # Main dashboard application
├── delivery_api.py        # Data processing and API layer
├── requirements.txt       # Project dependencies
└── Fast Delivery Agent Reviews.csv  # Dataset
```

## Data Description 📝

The dashboard uses `Fast Delivery Agent Reviews.csv` which contains:
- Delivery agent information
- Order types (Electronics, Food, Grocery, etc.)
- City locations across India
- Customer ratings (1-5 scale)
- Order volumes per city

## Interactive Features 🎮

- **Filtering Options**:
  - Filter by delivery agent
  - Filter by order type
  - Real-time updates
- **Map Visualization**:
  - Color-coded markers based on ratings
  - Hover tooltips with city information
  - Click markers for detailed stats
- **Analytics**:
  - Interactive pie charts
  - Detailed statistics view
  - Top performing city metrics

## Tech Stack 🛠️

- **Panel**: Main dashboard framework
- **Folium**: Interactive map visualization
- **Plotly**: Interactive charts and pie diagrams
- **Pandas**: Data processing and analysis
- **Bokeh**: Backend visualization engine and color palettes

## Contributing ��

Contributions are welcome! Please feel free to submit a Pull Request.

## Author 👨‍💻

Yanzhen Chen

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.