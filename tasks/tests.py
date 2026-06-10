from django.test import TestCase
from .models import Task
import csv
from io import StringIO


class ExportTasksCSVTestCase(TestCase):
    """Test the export_tasks_csv view for CSV export functionality."""

    def setUp(self):
        """Create test tasks for export."""
        self.task1 = Task.objects.create(title='Task 1', completed=False)
        self.task2 = Task.objects.create(title='Task 2', completed=True)
        self.task3 = Task.objects.create(title='Task 3', completed=False)

    def test_export_csv_without_format_parameter(self):
        """Test that export works when format query parameter is missing."""
        response = self.client.get('/export/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment; filename="tasks.csv"', response['Content-Disposition'])

    def test_export_csv_with_format_csv(self):
        """Test that export works with format=csv parameter."""
        response = self.client.get('/export/?format=csv')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment; filename="tasks.csv"', response['Content-Disposition'])

    def test_export_csv_with_format_json(self):
        """Test that export adjusts filename for non-csv formats."""
        response = self.client.get('/export/?format=json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('attachment; filename="tasks.json"', response['Content-Disposition'])

    def test_export_csv_content_structure(self):
        """Test that CSV content includes headers and task data."""
        response = self.client.get('/export/')
        content = response.content.decode('utf-8')
        lines = content.strip().split('\n')
        
        self.assertGreaterEqual(len(lines), 3)
        self.assertIn('ID', lines[0])
        self.assertIn('Title', lines[0])
        self.assertIn('Completed', lines[0])
        self.assertIn('Created At', lines[0])

    def test_export_csv_completion_rate_included(self):
        """Test that completion rate summary is included in CSV."""
        response = self.client.get('/export/')
        content = response.content.decode('utf-8')
        
        self.assertIn('Completion rate:', content)
        self.assertIn('33.3%', content)

    def test_export_csv_all_tasks_included(self):
        """Test that all tasks are included in the export."""
        response = self.client.get('/export/')
        content = response.content.decode('utf-8')
        
        self.assertIn('Task 1', content)
        self.assertIn('Task 2', content)
        self.assertIn('Task 3', content)

    def test_export_csv_format_parameter_case_insensitive(self):
        """Test that format parameter is case-insensitive."""
        response = self.client.get('/export/?format=CSV')
        self.assertEqual(response.status_code, 200)
        self.assertIn('attachment; filename="tasks.csv"', response['Content-Disposition'])

    def test_export_csv_empty_task_list(self):
        """Test that export handles empty task list gracefully."""
        Task.objects.all().delete()
        response = self.client.get('/export/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('ID', content)

