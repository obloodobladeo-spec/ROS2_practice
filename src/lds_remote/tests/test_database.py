"""Tests for database connection settings."""

import unittest
from unittest.mock import patch, sentinel

from lds_remote.database import connect_database


class DatabaseConnectionTests(unittest.TestCase):
    """Check password handling for interactive and scripted runs."""

    @patch("lds_remote.database.pymysql.connect", return_value=sentinel.connection)
    @patch("lds_remote.database.getpass", return_value="entered-password")
    @patch("lds_remote.database.sys.stdin.isatty", return_value=True)
    @patch.dict("lds_remote.database.os.environ", {}, clear=True)
    def test_prompts_with_default_account(self, isatty, getpass, connect):
        self.assertIs(connect_database(), sentinel.connection)
        getpass.assert_called_once_with("MySQL password: ")
        self.assertEqual(connect.call_args.kwargs["user"], "rosuser")
        self.assertEqual(connect.call_args.kwargs["password"], "entered-password")
        self.assertEqual(connect.call_args.kwargs["database"], "lds_practice")

    @patch("lds_remote.database.pymysql.connect", return_value=sentinel.connection)
    @patch("lds_remote.database.getpass")
    @patch.dict("lds_remote.database.os.environ", {"LDS_DB_PASSWORD": "set-password"}, clear=True)
    def test_uses_environment_password(self, getpass, connect):
        self.assertIs(connect_database(), sentinel.connection)
        getpass.assert_not_called()
        self.assertEqual(connect.call_args.kwargs["password"], "set-password")

    @patch("lds_remote.database.sys.stdin.isatty", return_value=False)
    @patch.dict("lds_remote.database.os.environ", {}, clear=True)
    def test_noninteractive_run_needs_password(self, isatty):
        with self.assertRaisesRegex(ValueError, "set LDS_DB_PASSWORD"):
            connect_database()


if __name__ == "__main__":
    unittest.main()
