import unittest

from scholarship.source_policy import (
    RAW_DOWNLOAD_LIMIT_BYTES,
    RECOMMENDED_SPLIT_BYTES,
    batch_is_complete,
    large_file_route,
)


class SourcePolicyTests(unittest.TestCase):
    def test_normal_file_uses_raw_download(self):
        self.assertEqual(large_file_route(10_000_000), "raw_download")

    def test_raw_download_limit_boundary(self):
        self.assertEqual(large_file_route(RAW_DOWNLOAD_LIMIT_BYTES), "raw_download")
        self.assertEqual(
            large_file_route(RAW_DOWNLOAD_LIMIT_BYTES + 1),
            "work_browser_download_and_split",
        )

    def test_complete_indexed_text_can_be_used(self):
        self.assertEqual(
            large_file_route(RAW_DOWNLOAD_LIMIT_BYTES + 1, indexed_text_complete=True),
            "indexed_text",
        )

    def test_oversize_pdf_is_never_skipped(self):
        self.assertEqual(
            large_file_route(RAW_DOWNLOAD_LIMIT_BYTES + 1),
            "work_browser_download_and_split",
        )

    def test_authenticated_direct_stream_precedes_browser(self):
        self.assertEqual(
            large_file_route(
                RAW_DOWNLOAD_LIMIT_BYTES + 1,
                direct_stream_available=True,
            ),
            "direct_stream_download_and_split",
        )

    def test_verified_split_copy_is_used_when_no_direct_stream(self):
        self.assertEqual(
            large_file_route(RAW_DOWNLOAD_LIMIT_BYTES + 1, verified_split_copy=True),
            "verified_split_copy",
        )

    def test_user_split_is_only_last_resort(self):
        self.assertEqual(
            large_file_route(
                RAW_DOWNLOAD_LIMIT_BYTES + 1,
                direct_stream_available=False,
                browser_available=False,
            ),
            "user_split_required",
        )
        self.assertLess(RECOMMENDED_SPLIT_BYTES, RAW_DOWNLOAD_LIMIT_BYTES)

    def test_unread_large_source_blocks_complete_batch(self):
        self.assertTrue(batch_is_complete(["fully_read", "verified_duplicate"]))
        self.assertFalse(batch_is_complete(["fully_read", "blocked_large_file"]))
        self.assertFalse(batch_is_complete([]))


if __name__ == "__main__":
    unittest.main()
