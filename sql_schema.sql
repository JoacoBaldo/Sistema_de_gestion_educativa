SET FOREIGN_KEY_CHECKS = 0;

-- ==========================================
-- Creación de Tablas Maestras
-- ==========================================
CREATE TABLE `status_types` (
  `id` integer NOT NULL,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE `role_types` (
  `id` integer NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE `evaluation_types` (
  `id` integer NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE `file_types` (
  `id` integer NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE `careers` (
  `id` integer NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE `academic_period` (
  `id` integer NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `period_start` timestamp NULL DEFAULT NULL,
  `period_end` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
);

-- ==========================================
-- Creación de Entidades Principales
-- ==========================================
CREATE TABLE `users` (
  `id` integer NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `email` varchar(50) NOT NULL UNIQUE,
  `password` varchar(100) NOT NULL,
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `deleted_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE `student_profiles` (
  `user_id` integer NOT NULL,
  `career_id` integer NULL,
  `document` varchar(255) NOT NULL,
  PRIMARY KEY (`user_id`)
);

CREATE TABLE `classrooms` (
  `id` integer NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `department` varchar(255) DEFAULT NULL,
  `university` varchar(255) DEFAULT NULL,
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
);

CREATE TABLE `classroom_users` (
  `classroom_id` integer NOT NULL,
  `user_id` integer NOT NULL,
  `role_id` integer NOT NULL,
  `status_type_id` integer NOT NULL DEFAULT 0,
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`classroom_id`, `user_id`)
);

CREATE TABLE `class_schedule` (
  `id` integer NOT NULL AUTO_INCREMENT,
  `classroom_id` integer NOT NULL,
  `class_day` integer NOT NULL,
  `class_start` timestamp NOT NULL,
  `class_end` timestamp NOT NULL,
  `academic_period_id` integer NOT NULL,
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
);

CREATE TABLE `teams` (
  `id` integer NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `classroom_id` integer NOT NULL,
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
);

CREATE TABLE `team_members` (
  `team_id` integer NOT NULL,
  `user_id` integer NOT NULL,
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`team_id`, `user_id`)
);

CREATE TABLE `evaluations` (
  `id` integer NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `evaluation_type_id` integer NOT NULL,
  `referenced_eval_id` integer NULL DEFAULT NULL,
  `classroom_id` integer NOT NULL,
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
  `individual` bool NOT NULL DEFAULT true,
  PRIMARY KEY (`id`)
);

CREATE TABLE `grades` (
  `id` integer NOT NULL AUTO_INCREMENT,
  `evaluation_id` integer NOT NULL,
  `user_id` integer NULL DEFAULT NULL,
  `team_id` integer NULL DEFAULT NULL,
  `score` float NOT NULL DEFAULT 0.0,
  `feedback` varchar(255) DEFAULT NULL,
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
);

CREATE TABLE `attendance_events` (
  `id` integer NOT NULL AUTO_INCREMENT,
  `classroom_id` integer NOT NULL,
  `event_date` timestamp NOT NULL,
  `qr_code` varchar(255) DEFAULT NULL,
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
);

CREATE TABLE `attendance_records` (
  `attendance_event_id` integer NOT NULL,
  `user_id` integer NOT NULL,
  `attended` bool NOT NULL DEFAULT false,
  `updated_at` timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`attendance_event_id`, `user_id`)
);

CREATE TABLE `resourses` (
  `id` integer NOT NULL AUTO_INCREMENT,
  `classroom_id` integer NOT NULL,
  `title` varchar(255) NOT NULL,
  `link` varchar(255) NOT NULL,
  `file_type_id` integer NOT NULL,
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
);

-- ==========================================
-- Vinculación de Claves Foráneas
-- ==========================================
ALTER TABLE `student_profiles` ADD CONSTRAINT `fk_profile_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;
ALTER TABLE `student_profiles` ADD CONSTRAINT `fk_profile_career` FOREIGN KEY (`career_id`) REFERENCES `careers` (`id`) ON DELETE SET NULL;
ALTER TABLE `classroom_users` ADD CONSTRAINT `fk_cu_classroom` FOREIGN KEY (`classroom_id`) REFERENCES `classrooms` (`id`) ON DELETE CASCADE;
ALTER TABLE `classroom_users` ADD CONSTRAINT `fk_cu_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;
ALTER TABLE `classroom_users` ADD CONSTRAINT `fk_cu_role` FOREIGN KEY (`role_id`) REFERENCES `role_types` (`id`);
ALTER TABLE `classroom_users` ADD CONSTRAINT `fk_cu_status` FOREIGN KEY (`status_type_id`) REFERENCES `status_types` (`id`);
ALTER TABLE `class_schedule` ADD CONSTRAINT `fk_schedule_classroom` FOREIGN KEY (`classroom_id`) REFERENCES `classrooms` (`id`) ON DELETE CASCADE;
ALTER TABLE `class_schedule` ADD CONSTRAINT `fk_schedule_period` FOREIGN KEY (`academic_period_id`) REFERENCES `academic_period` (`id`);
ALTER TABLE `teams` ADD CONSTRAINT `fk_teams_classroom` FOREIGN KEY (`classroom_id`) REFERENCES `classrooms` (`id`) ON DELETE CASCADE;
ALTER TABLE `team_members` ADD CONSTRAINT `fk_tm_team` FOREIGN KEY (`team_id`) REFERENCES `teams` (`id`) ON DELETE CASCADE;
ALTER TABLE `team_members` ADD CONSTRAINT `fk_tm_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;
ALTER TABLE `evaluations` ADD CONSTRAINT `fk_eval_type` FOREIGN KEY (`evaluation_type_id`) REFERENCES `evaluation_types` (`id`);
ALTER TABLE `evaluations` ADD CONSTRAINT `fk_eval_self` FOREIGN KEY (`referenced_eval_id`) REFERENCES `evaluations` (`id`) ON DELETE SET NULL;
ALTER TABLE `evaluations` ADD CONSTRAINT `fk_eval_classroom` FOREIGN KEY (`classroom_id`) REFERENCES `classrooms` (`id`) ON DELETE CASCADE;
ALTER TABLE `grades` ADD CONSTRAINT `fk_grades_eval` FOREIGN KEY (`evaluation_id`) REFERENCES `evaluations` (`id`) ON DELETE CASCADE;
ALTER TABLE `grades` ADD CONSTRAINT `fk_grades_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;
ALTER TABLE `grades` ADD CONSTRAINT `fk_grades_team` FOREIGN KEY (`team_id`) REFERENCES `teams` (`id`) ON DELETE CASCADE;
ALTER TABLE `attendance_events` ADD CONSTRAINT `fk_events_classroom` FOREIGN KEY (`classroom_id`) REFERENCES `classrooms` (`id`) ON DELETE CASCADE;
ALTER TABLE `attendance_records` ADD CONSTRAINT `fk_records_event` FOREIGN KEY (`attendance_event_id`) REFERENCES `attendance_events` (`id`) ON DELETE CASCADE;
ALTER TABLE `attendance_records` ADD CONSTRAINT `fk_records_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;
ALTER TABLE `resourses` ADD CONSTRAINT `fk_resources_classroom` FOREIGN KEY (`classroom_id`) REFERENCES `classrooms` (`id`) ON DELETE CASCADE;
ALTER TABLE `resourses` ADD CONSTRAINT `fk_resources_type` FOREIGN KEY (`file_type_id`) REFERENCES `file_types` (`id`);

-- ==========================================
-- Carga de Datos Maestros (Semillas)
-- ==========================================
INSERT INTO `status_types` (`id`, `name`) VALUES (0, 'Activo'), (1, 'Inactivo'), (2, 'Regular'), (3, 'Libre');
INSERT INTO `role_types` (`name`) VALUES ('Profesor'), ('Ayudante de catedra'), ('Estudiante');
INSERT INTO `evaluation_types` (`name`) VALUES ('Parcial'), ('Trabajo practico'), ('Recuperatorio'), ('Ejercitacion');
INSERT INTO `file_types` (`name`) VALUES ('documento'), ('presentacion'), ('video');
INSERT INTO `academic_period` (`name`, `period_start`, `period_end`) VALUES 
  ('1C', '2026-03-01 08:00:00', '2026-07-15 23:59:59'),
  ('C2', '2026-08-01 08:00:00', '2026-12-15 23:59:59');
INSERT INTO `careers` (`id`, `name`) VALUES
  (1, 'Ingeniería Civil'),
  (2, 'Ingeniería en Alimentos'),
  (3, 'Ingeniería en Energía Eléctrica'),
  (4, 'Ingeniería Electrónica'),
  (5, 'Ingeniería en Agrimensura'),
  (6, 'Ingeniería en Informática'),
  (7, 'Ingeniería en Petróleo'),
  (8, 'Ingeniería Industrial'),
  (9, 'Ingeniería Mecánica'),
  (10, 'Ingeniería Naval y Mecánica'),
  (11, 'Ingeniería Química'),
  (12, 'Bioingeniería');

SET FOREIGN_KEY_CHECKS = 1;