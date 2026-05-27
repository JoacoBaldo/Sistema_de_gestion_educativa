CREATE TABLE IF NOT EXISTS request_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    usuario_id INT NULL,
    metodo VARCHAR(10) NOT NULL,
    path VARCHAR(500) NOT NULL,
    status_code INT NOT NULL,
    remote_addr VARCHAR(100),
    user_agent VARCHAR(512),
    request_body TEXT,
    creado_en DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES users(id)
);
