GET_ALL_FILES = """
SELECT metadata.id, ip_address, host_name, file_name, datetime(time_created),
result, tag_key, tag_value
FROM metadata
LEFT JOIN metadata_tag ON metadata.id = metadata_tag.metadata_id
LEFT JOIN tags ON metadata_tag.tag_id = tags.id
ORDER BY time_created DESC, metadata.id DESC
"""

GET_FILE_BY_ID = """
SELECT metadata.id, ip_address, host_name, file_name, datetime(time_created),
result, tag_key, tag_value
FROM metadata
LEFT JOIN metadata_tag ON metadata.id = metadata_tag.metadata_id
LEFT JOIN tags ON metadata_tag.tag_id = tags.id
WHERE metadata.id = ?
"""


GET_ALL_FILES_BASIC = """
SELECT id, ip_address, host_name, file_name, datetime(time_created), result
FROM metadata
"""

GET_ALL_TAGS = """
SELECT id, tag_key, tag_value
FROM tags
"""

ADD_TAG_TO_FILE = """
INSERT INTO metadata_tag (metadata_id, tag_id)
VALUES (?, ?)
"""

ADD_TAG = """
INSERT INTO tags (tag_key, tag_value)
VALUES (?, ?)
"""

ADD_FILE = """
INSERT INTO metadata (
id, ip_address, host_name, file_name, time_created, result)
VALUES (?, ?, ?, ?, ?, ?)
"""
