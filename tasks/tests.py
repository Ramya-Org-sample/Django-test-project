from django.test import TestCase
from django.urls import reverse
from .models import Task


class ExportTasksCSVTestCase(TestCase):
    """Tests for the export_tasks_csv endpoint."""

    def setUp(self):
        """Create test tasks for export scenarios."""
        self.task1 = Task.objects.create(title='Buy groceries', completed=True)
        self.task2 = Task.objects.create(title='Write report', completed=False)
        self.task3 = Task.objects.create(title='Call dentist', completed=True)

    def test_export_csv_without_format_parameter(self):
        """Test that export works when format query parameter is missing."""
        response = self.client.get(reverse('export_tasks_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('tasks.csv', response['Content-Disposition'])

    def test_export_csv_with_csv_format_parameter(self):
        """Test that export works when format is explicitly set to csv."""
        response = self.client.get(reverse('export_tasks_csv'), {'format': 'csv'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('tasks.csv', response['Content-Disposition'])

    def test_export_csv_with_xlsx_format_parameter(self):
        """Test that export changes filename when format is xlsx."""
        response = self.client.get(reverse('export_tasks_csv'), {'format': 'xlsx'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('tasks.xlsx', response['Content-Disposition'])

    def test_export_csv_contains_all_tasks(self):
        """Test that exported CSV contains all tasks and completion rate."""
        response = self.client.get(reverse('export_tasks_csv'))
        content = response.content.decode('utf-8')
        self.assertIn('Buy groceries', content)
        self.assertIn('Write report', content)
        self.assertIn('Call dentist', content)
        self.assertIn('Completion rate', content)

    def test_export_csv_format_case_insensitive(self):
        """Test that format parameter is case-insensitive."""
        response = self.client.get(reverse('export_tasks_csv'), {'format': 'XLSX'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('tasks.xlsx', response['Content-Disposition'])

    def test_export_csv_with_empty_task_list(self):
        """Test that export handles empty task list without crashing."""
        Task.objects.all().delete()
        response = self.client.get(reverse('export_tasks_csv'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('ID', content)
