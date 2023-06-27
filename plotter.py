import datetime
import os
import matplotlib
import matplotlib.font_manager as font_manager
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class Plotter:
    def __init__(self, x, y, title, xlabel='', ylabel=''):
        self.x = x
        self.y = y
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
    
    def generate_plot(self):
        plt.plot(self.x, self.y)
        plt.title(self.title, fontfamily='serif', fontsize=12)
        plt.xlabel(self.xlabel, fontfamily='serif', fontsize=8)
        plt.ylabel(self.ylabel, fontfamily='serif', fontsize=10)
        return plt.gcf()  # Return the Figure object
    
    def format_date(self, date_str):
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        return date.strftime("%y-%m-%d")  # Format the date as yy-mm-dd
    
    def save_plot(self, filename):
        filepath = os.path.join('static', 'image', filename)  # Use forward slashes in the file path
        print('filepath:', filepath) 
        
        fig = self.generate_plot()  # Generate the plot
        
        # Format the x-axis labels as dates without time
        x_labels = [self.format_date(date) for date in self.x]
        fig.axes[0].set_xticklabels(x_labels, rotation='vertical', fontsize=7)  # Adjust rotation and fontsize
        
        fig.savefig(filepath, format='jpg')
        plt.close(fig)
        
