from django.test import TestCase
from .models import Task


class ExportTasksCSVTestCase(TestCase):
    """Tests for CSV export endpoint."""

    def test_export_without_format_parameter_uses_default(self):
        """Crash scenario: export should not crash when format parameter is missing."""
        Task.objects.create(title='Test Task 1')
        Task.objects.create(title='Test Task 2')
        response = self.client.get('/export/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('Test Task 1', response.content.decode())

    def test_export_with_csv_format_parameter(self):
        """Fix scenario: export should work correctly with format=csv."""
        Task.objects.create(title='Test Task')
        response = self.client.get('/export/?format=csv')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        content = response.content.decode()
        self.assertIn('ID', content)
        self.assertIn('Title', content)
        self.assertIn('Completed', content)
        self.assertIn('Created At', content)

    def test_export_with_alternative_format_parameter(self):
        """Edge case: export should accept alternative format parameters."""
        Task.objects.create(title='Test Task')
        response = self.client.get('/export/?format=json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('tasks.json', response['Content-Disposition'])

    def test_export_includes_completion_rate(self):
        """Edge case: export should include completion rate summary."""
        completed_task = Task.objects.create(title='Done Task', completed=True)
        incomplete_task = Task.objects.create(title='Pending Task', completed=False)
        response = self.client.get('/export/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('Completion rate:', content)
        self.assertIn('50.0%', content)
