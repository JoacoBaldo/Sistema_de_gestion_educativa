CREATE TABLE IF NOT EXISTS attendance_event_codes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    attendance_event_id INT NOT NULL,
    user_id INT NOT NULL,
    code VARCHAR(64) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (attendance_event_id) REFERENCES attendance_events(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY uq_event_user (attendance_event_id, user_id)
);
