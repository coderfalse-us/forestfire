import unittest
import sys
import os
from unittest.mock import MagicMock, patch
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for testing

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from forestfire.plots.graph import PathVisualizer
from forestfire.utils.config import NUM_PICKERS, PICKER_LOCATIONS

class TestPathVisualizer(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.path_visualizer = PathVisualizer()
        
        # Sample data for testing
        self.final_solution = [0, 1, 2]  # Each order assigned to a different picker
        self.orders_assign = [
            [(5, 5)],    # Order 0 location
            [(15, 15)],  # Order 1 location
            [(25, 25)]   # Order 2 location
        ]
    
    @patch('matplotlib.pyplot.figure')
    @patch('matplotlib.pyplot.subplot')
    @patch('matplotlib.pyplot.plot')
    @patch('matplotlib.pyplot.scatter')
    @patch('matplotlib.pyplot.title')
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_plot_routes(self, mock_close, mock_savefig, mock_title, mock_scatter, 
                         mock_plot, mock_subplot, mock_figure):
        """Test route plotting"""
        # Mock the route optimizer
        mock_route_optimizer = MagicMock()
        mock_routes = [
            MagicMock(picker_id=0, locations=[(5, 5), (40, 40)], assigned_orders=[0]),
            MagicMock(picker_id=1, locations=[(15, 15), (40, 40)], assigned_orders=[1]),
            MagicMock(picker_id=2, locations=[(25, 25), (40, 40)], assigned_orders=[2])
        ]
        mock_route_optimizer.calculate_shortest_route.return_value = (60.0, mock_routes, [])
        
        # Replace the route optimizer in the visualizer
        self.path_visualizer.route_optimizer = mock_route_optimizer
        
        # Call the method
        self.path_visualizer.plot_routes(self.final_solution)
        
        # Check that the route optimizer was called
        mock_route_optimizer.calculate_shortest_route.assert_called_once()
        
        # Check that matplotlib functions were called
        mock_figure.assert_called()
        mock_subplot.assert_called()
        mock_plot.assert_called()
        mock_scatter.assert_called()
        mock_title.assert_called()
        mock_savefig.assert_called()
        mock_close.assert_called()
    
    @patch('matplotlib.pyplot.figure')
    @patch('matplotlib.pyplot.subplot')
    @patch('matplotlib.pyplot.plot')
    @patch('matplotlib.pyplot.scatter')
    @patch('matplotlib.pyplot.title')
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_plot_routes_with_empty_solution(self, mock_close, mock_savefig, mock_title, 
                                            mock_scatter, mock_plot, mock_subplot, mock_figure):
        """Test route plotting with empty solution"""
        # Empty solution
        final_solution = []
        
        # Mock the route optimizer
        mock_route_optimizer = MagicMock()
        mock_route_optimizer.calculate_shortest_route.return_value = (0.0, [], [])
        
        # Replace the route optimizer in the visualizer
        self.path_visualizer.route_optimizer = mock_route_optimizer
        
        # Call the method
        self.path_visualizer.plot_routes(final_solution)
        
        # Check that the route optimizer was not called (empty solution)
        mock_route_optimizer.calculate_shortest_route.assert_not_called()
        
        # Check that matplotlib functions were still called (for empty plot)
        mock_figure.assert_called()
    
    @patch('matplotlib.pyplot.figure')
    @patch('matplotlib.pyplot.subplot')
    @patch('matplotlib.pyplot.plot')
    @patch('matplotlib.pyplot.scatter')
    @patch('matplotlib.pyplot.title')
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_plot_picker_paths(self, mock_close, mock_savefig, mock_title, 
                              mock_scatter, mock_plot, mock_subplot, mock_figure):
        """Test picker path plotting"""
        # Mock data
        routes = [
            MagicMock(picker_id=0, locations=[(5, 5), (40, 40)], assigned_orders=[0]),
            MagicMock(picker_id=1, locations=[(15, 15), (40, 40)], assigned_orders=[1]),
            MagicMock(picker_id=2, locations=[(25, 25), (40, 40)], assigned_orders=[2])
        ]
        
        # Call the method
        self.path_visualizer._plot_picker_paths(routes)
        
        # Check that matplotlib functions were called
        mock_figure.assert_called()
        mock_subplot.assert_called()
        mock_plot.assert_called()
        mock_scatter.assert_called()
        mock_title.assert_called()
        mock_savefig.assert_called()
        mock_close.assert_called()
    
    @patch('matplotlib.pyplot.figure')
    @patch('matplotlib.pyplot.subplot')
    @patch('matplotlib.pyplot.plot')
    @patch('matplotlib.pyplot.scatter')
    @patch('matplotlib.pyplot.title')
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_plot_picker_paths_with_empty_routes(self, mock_close, mock_savefig, mock_title, 
                                               mock_scatter, mock_plot, mock_subplot, mock_figure):
        """Test picker path plotting with empty routes"""
        # Empty routes
        routes = []
        
        # Call the method
        self.path_visualizer._plot_picker_paths(routes)
        
        # Check that matplotlib functions were still called (for empty plot)
        mock_figure.assert_called()
    
    @patch('matplotlib.pyplot.figure')
    @patch('matplotlib.pyplot.subplot')
    @patch('matplotlib.pyplot.plot')
    @patch('matplotlib.pyplot.scatter')
    @patch('matplotlib.pyplot.title')
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_plot_picker_assignments(self, mock_close, mock_savefig, mock_title, 
                                    mock_scatter, mock_plot, mock_subplot, mock_figure):
        """Test picker assignment plotting"""
        # Call the method
        self.path_visualizer._plot_picker_assignments(self.final_solution)
        
        # Check that matplotlib functions were called
        mock_figure.assert_called()
        mock_subplot.assert_called()
        mock_scatter.assert_called()
        mock_title.assert_called()
        mock_savefig.assert_called()
        mock_close.assert_called()

if __name__ == '__main__':
    unittest.main()
