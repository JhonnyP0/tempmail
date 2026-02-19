SET NAMES utf8mb4;

CREATE TABLE IF NOT EXISTS mailboxes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email_address VARCHAR(255) NOT NULL UNIQUE,
    session_token VARCHAR(255) NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_session_token ON mailboxes(session_token);
CREATE INDEX idx_email_address ON mailboxes(email_address);

CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mailbox_id INT NOT NULL,
    sender VARCHAR(255) NOT NULL,
    subject VARCHAR(255) DEFAULT '(No title)',
    body_text TEXT,
    received_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (mailbox_id) REFERENCES mailboxes(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_mailbox_id ON messages(mailbox_id);