import pandas as pd

class DeliveryAPI:
    def __init__(self, filepath):
        """Initialize data and city coordinates"""
        self.data = pd.read_csv(filepath)
        
        # City coordinates data
        self.CITY_COORDS = {
            'Delhi': [28.6139, 77.2090],
            'Mumbai': [19.0760, 72.8777],
            'Bangalore': [12.9716, 77.5946],
            'Hyderabad': [17.3850, 78.4867],
            'Chennai': [13.0827, 80.2707],
            'Kolkata': [22.5726, 88.3639],
            'Ahmedabad': [23.0225, 72.5714],
            'Pune': [18.5204, 73.8567],
            'Jaipur': [26.9124, 75.7873],
            'Lucknow': [26.8467, 80.9462]
        }
        
        # Add latitude and longitude
        self.data['Latitude'] = self.data['Location'].map(lambda x: self.CITY_COORDS[x][0])
        self.data['Longitude'] = self.data['Location'].map(lambda x: self.CITY_COORDS[x][1])
    
    def get_filtered_data(self, agent=None, order_type=None):
        """Get filtered data based on conditions"""
        filtered_data = self.data.copy()
        
        if agent and agent != 'All':
            filtered_data = filtered_data[filtered_data['Agent Name'] == agent]
        if order_type and order_type != 'All':
            filtered_data = filtered_data[filtered_data['Order Type'] == order_type]
            
        return filtered_data
    
    def get_city_stats(self, agent=None, order_type=None):
        """Get city statistics"""
        filtered_data = self.get_filtered_data(agent, order_type)
        return filtered_data.groupby('Location').agg({
            'Rating': 'mean',
            'Latitude': 'first',
            'Longitude': 'first',
            'Order Type': 'count'
        }).reset_index()
    
    def get_order_type_distribution(self, agent=None, order_type=None):
        """Get order type distribution"""
        filtered_data = self.get_filtered_data(agent, order_type)
        return (filtered_data['Order Type']
                .value_counts()
                .reset_index()
                .rename(columns={'index': 'Order Type', 
                               'Order Type': 'Count'}))
    
    def get_top_stats(self, agent=None, order_type=None):
        """Get top performance statistics"""
        filtered_data = self.get_filtered_data(agent, order_type)
        
        if filtered_data.empty:
            return {
                'top_city': 'N/A',
                'top_city_orders': 0,
                'top_rating_city': 'N/A',
                'top_city_rating': 0
            }
            
        city_orders = filtered_data.groupby('Location')['Order Type'].count()
        city_ratings = filtered_data.groupby('Location')['Rating'].mean()
        
        return {
            'top_city': city_orders.idxmax(),
            'top_city_orders': city_orders.max(),
            'top_rating_city': city_ratings.idxmax(),
            'top_city_rating': city_ratings.max()
        } 