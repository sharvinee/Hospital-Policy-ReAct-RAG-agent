"""Test safe full-dataset upload without contacting LangSmith."""

import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from evals import upload_dataset


class UploadDatasetTests(unittest.TestCase):
    """Check dataset creation, split reuse, and duplicate prevention."""

    def setUp(self):
        """Create a client with one local example per split."""
        self.client = Mock()
        self.client.create_dataset.return_value = SimpleNamespace(id="dataset-id")
        self.client.read_dataset.return_value = SimpleNamespace(id="dataset-id")
        self.client.read_dataset_version.return_value = SimpleNamespace(as_of="version")
        self.client.list_examples.return_value = []
        self.examples = {
            split: [{"inputs": {}, "metadata": {"id": f"{split}-1"}, "split": split}]
            for split in upload_dataset.SPLITS
        }

    def run_upload(self):
        """Run the uploader using a mock client and local examples."""
        with (
            patch.object(upload_dataset, "Client", return_value=self.client),
            patch.object(upload_dataset, "get_settings", return_value=SimpleNamespace(langsmith_api_key="test")),
            patch.object(upload_dataset, "load_examples", side_effect=lambda split: self.examples[split]),
            patch("sys.argv", ["upload_dataset", "--tag", "baseline"]),
        ):
            upload_dataset.main()

    def test_new_dataset_uploads_both_splits(self):
        """Both labelled splits are uploaded when the dataset is missing."""
        self.client.has_dataset.return_value = False
        self.run_upload()
        self.client.create_dataset.assert_called_once()
        self.assertEqual(self.client.create_examples.call_count, 2)
        self.client.update_dataset_tag.assert_called_once()

    def test_existing_optimization_uploads_only_holdout(self):
        """An existing matching split is skipped and the missing split added."""
        self.client.has_dataset.return_value = True
        self.client.list_examples.side_effect = lambda **kwargs: (
            [SimpleNamespace(metadata={"id": "optimization-1"})]
            if kwargs["splits"] == ["optimization"] else []
        )
        self.run_upload()
        self.client.create_examples.assert_called_once_with(
            dataset_id="dataset-id", examples=self.examples["holdout"]
        )

    def test_complete_dataset_is_not_uploaded_again(self):
        """Rerunning does not create duplicate examples."""
        self.client.has_dataset.return_value = True
        self.client.list_examples.side_effect = lambda **kwargs: [
            SimpleNamespace(metadata={"id": f"{kwargs['splits'][0]}-1"})
        ]
        self.run_upload()
        self.client.create_examples.assert_not_called()

    def test_incomplete_split_stops_before_any_upload(self):
        """Mismatched existing IDs stop the operation before any split is written."""
        self.client.has_dataset.return_value = True
        self.client.list_examples.side_effect = lambda **kwargs: (
            [SimpleNamespace(metadata={"id": "unexpected-id"})]
            if kwargs["splits"] == ["holdout"] else []
        )
        with self.assertRaisesRegex(ValueError, "incomplete or does not match"):
            self.run_upload()
        self.client.create_examples.assert_not_called()
        self.client.update_dataset_tag.assert_not_called()
