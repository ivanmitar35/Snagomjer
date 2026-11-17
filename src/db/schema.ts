import { index, integer, real, sqliteTable, text } from 'drizzle-orm/sqlite-core';

// Data model v1 (docs/tehnicki_plan.md, section 5).
// Times are Unix milliseconds, weights are always kilograms.

export const exercise = sqliteTable('exercise', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  name: text('name').notNull(),
  muscleGroup: text('muscle_group').notNull(),
  equipment: text('equipment'),
  isCustom: integer('is_custom', { mode: 'boolean' }).notNull().default(false),
  // Custom exercises that appear in history are archived instead of deleted.
  archivedAt: integer('archived_at'),
});

export const workout = sqliteTable(
  'workout',
  {
    id: integer('id').primaryKey({ autoIncrement: true }),
    startedAt: integer('started_at').notNull(),
    // NULL means the workout is still in progress.
    finishedAt: integer('finished_at'),
    note: text('note'),
  },
  (t) => [index('workout_started_at_idx').on(t.startedAt)],
);

export const workoutExercise = sqliteTable(
  'workout_exercise',
  {
    id: integer('id').primaryKey({ autoIncrement: true }),
    workoutId: integer('workout_id')
      .notNull()
      .references(() => workout.id, { onDelete: 'cascade' }),
    exerciseId: integer('exercise_id')
      .notNull()
      .references(() => exercise.id, { onDelete: 'restrict' }),
    position: integer('position').notNull(),
  },
  (t) => [index('workout_exercise_exercise_id_idx').on(t.exerciseId)],
);

export const set = sqliteTable(
  'set',
  {
    id: integer('id').primaryKey({ autoIncrement: true }),
    workoutExerciseId: integer('workout_exercise_id')
      .notNull()
      .references(() => workoutExercise.id, { onDelete: 'cascade' }),
    position: integer('position').notNull(),
    reps: integer('reps').notNull(),
    weight: real('weight').notNull(),
    isWarmup: integer('is_warmup', { mode: 'boolean' }).notNull().default(false),
  },
  (t) => [index('set_workout_exercise_id_idx').on(t.workoutExerciseId)],
);

export const setting = sqliteTable('setting', {
  key: text('key').primaryKey(),
  value: text('value').notNull(),
});

export type Exercise = typeof exercise.$inferSelect;
export type Workout = typeof workout.$inferSelect;
export type WorkoutExercise = typeof workoutExercise.$inferSelect;
export type Set = typeof set.$inferSelect;
export type Setting = typeof setting.$inferSelect;
