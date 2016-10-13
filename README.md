Test user:

username: example
password: example

Features

- Summaries
-- Trial balance
-- Income statement
-- Balance statement
-- Graphs

- Lists
-- Documents
-- Transactions
-- Accounts
-- Clients
-- Suppliers

- Detail
-- Document
--- Download
--- Edit
-- Transaction
-- Account
-- Client
-- Supplier
-- Scenario


Model

Transaction
	is_confirmed OR Scenario
	ie transaction must be confirmed or must be in a scenario.

Cost Centre Transaction
	Same as Transaction but does not form part of the official financial record and is used mainly for internal reporting.
	Cost centre transactions have reduced validation and does not conform to GAAP

