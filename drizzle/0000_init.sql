CREATE TABLE `exercise` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`name` text NOT NULL,
	`muscle_group` text NOT NULL,
	`equipment` text,
	`is_custom` integer DEFAULT false NOT NULL,
	`archived_at` integer
);
--> statement-breakpoint
CREATE TABLE `set` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`workout_exercise_id` integer NOT NULL,
	`position` integer NOT NULL,
	`reps` integer NOT NULL,
	`weight` real NOT NULL,
	`is_warmup` integer DEFAULT false NOT NULL,
	FOREIGN KEY (`workout_exercise_id`) REFERENCES `workout_exercise`(`id`) ON UPDATE no action ON DELETE cascade
);
--> statement-breakpoint
CREATE INDEX `set_workout_exercise_id_idx` ON `set` (`workout_exercise_id`);--> statement-breakpoint
CREATE TABLE `setting` (
	`key` text PRIMARY KEY NOT NULL,
	`value` text NOT NULL
);
--> statement-breakpoint
CREATE TABLE `workout` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`started_at` integer NOT NULL,
	`finished_at` integer,
	`note` text
);
--> statement-breakpoint
CREATE INDEX `workout_started_at_idx` ON `workout` (`started_at`);--> statement-breakpoint
CREATE TABLE `workout_exercise` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`workout_id` integer NOT NULL,
	`exercise_id` integer NOT NULL,
	`position` integer NOT NULL,
	FOREIGN KEY (`workout_id`) REFERENCES `workout`(`id`) ON UPDATE no action ON DELETE cascade,
	FOREIGN KEY (`exercise_id`) REFERENCES `exercise`(`id`) ON UPDATE no action ON DELETE restrict
);
--> statement-breakpoint
CREATE INDEX `workout_exercise_exercise_id_idx` ON `workout_exercise` (`exercise_id`);