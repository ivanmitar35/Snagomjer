import { drizzle } from 'drizzle-orm/expo-sqlite';
import { openDatabaseSync } from 'expo-sqlite';

import * as schema from './schema';

// The change listener lets useLiveQuery re-render screens after writes.
const sqlite = openDatabaseSync('snagomjer.db', { enableChangeListener: true });

// SQLite leaves foreign keys off by default; cascades and RESTRICT depend on them.
sqlite.execSync('PRAGMA foreign_keys = ON;');

export const db = drizzle(sqlite, { schema });

export type Database = typeof db;
