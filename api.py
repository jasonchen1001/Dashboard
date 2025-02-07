import pandas as pd

class DeliveryAPI:
    def __init__(self, filepath):
        """初始化 API"""
        self.data = pd.read_csv(filepath)
    
    def get_data_by_filters(self, agent=None, location=None, order_type=None, rating_range=None):
        """根据条件获取数据"""
        filtered_data = self.data.copy()
        
        # 应用过滤条件
        if agent and agent != 'All':
            filtered_data = filtered_data[filtered_data['Agent Name'] == agent]
            
        if location and location != 'All':
            filtered_data = filtered_data[filtered_data['Location'] == location]
            
        if order_type and order_type != 'All':
            filtered_data = filtered_data[filtered_data['Order Type'] == order_type]
            
        if rating_range:
            min_rating, max_rating = rating_range
            filtered_data = filtered_data[
                (filtered_data['Rating'] >= min_rating) & 
                (filtered_data['Rating'] <= max_rating)
            ]
            
        return filtered_data 