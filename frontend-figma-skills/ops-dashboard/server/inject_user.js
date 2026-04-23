const { Pool } = require('pg');
require('dotenv').config({ path: '../../.env' });
console.log('Connecting to', process.env.DATABASE_URL.split('@')[1]);
const pool = new Pool({ connectionString: process.env.DATABASE_URL, ssl: { rejectUnauthorized: false } });

async function insertMissingUser() {
  const client = await pool.connect();
  try {
    const res = await client.query(`
      INSERT INTO user_data (name, uploaded, created, published, "uploadedduration", "createdduration", "publishedduration")
      VALUES ('USER', 0, 5, 0, '00:00:00', '00:01:16', '00:00:00')
      ON CONFLICT (name) DO UPDATE SET
        uploaded = EXCLUDED.uploaded,
        created = EXCLUDED.created;
    `);
    console.log('Inserted USER:', res.rowCount);
  } catch (err) {
    console.error(err);
  } finally {
    client.release();
    pool.end();
  }
}
insertMissingUser();
